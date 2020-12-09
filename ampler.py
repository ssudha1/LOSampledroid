#!/usr/bin/python
import ample_types as types
import sys, os, subprocess, struct,binascii
from collections import OrderedDict

listing= OrderedDict()
memList= OrderedDict()
mapList= OrderedDict()
path = ""
lstList=""
def parseFile(lstFile):
	if (os.path.isfile(lstFile)):
		f= open(lstFile,"r")
		lstList = f.read().split(os.linesep + os.linesep)
		lstList.remove(lstList[0])
		lstList.remove(lstList[len(lstList)-1])
		return lstList

def extSE(lstList):#address start and end
	start = lstList[0]
	end = lstList[len(lstList)-1]
	start = start[start.index("range")+6 :start.index("to")-1]
	end = end[end.index("to")+3 :end.index("(")-1]
	return [int(start, 16), int(end, 16)]	
	
def validateAddr(addr,start, end):	
	if (addr < start or addr > end):
		return False
	else:
		return True
	
		
def extAddrRange(lstList):
	
	for entry in lstList:
		#print entry
		addRange = [j for j in entry.split() if ("0x") in j]
		start = addRange[0]
		end = addRange[1]
		listing.update({entry.split()[1]:addRange})
	return listing




def lstPath(path, entry):	
	entryPath = path+"/"+entry.split()[1]
	#print entryPath
	return entryPath[:len(entryPath)-1]


def findAddr(addr, lst):
	#print "addr"
	#print addr
	addrInt = int(addr, 16)
	#print "AddrInt"
	#print addrInt
	start =0
	end=0
	for key, value in lst.items():
		v1 = int(value[1], 16)
		#print key
		#print value
		#print v1
		v0 = int(value[0], 16)
		#print v0
		#print "addrint"
		#print addrInt		
		if addrInt < v1:
			if addrInt in xrange(v0, v1):
				start = value[0]
				end =  value[1]
				#print "AddrInt"
				#print "Addr " + addr
				#print "key " + key
				#print "start " + start
				break
	return [addr, start, key[:len(key)-1]]
	
		
def extRuntime(path):
	process = subprocess.check_output("nm -aS "+path+"/libart.so | grep \"_ZN3art7Runtime9instance_E\"", shell = True)
	#print "Pointer to the Runtime Offset is @ "+ process.split()[0]
	return process.split()[0]
        #process1 = subprocess.check_output("nm -aS "+path+"/libskia.so | grep \"_ZN3art7Runtime9instance_E\"", shell = True)
	#print process.split()[0]
def extBss(lstList, path):
	libRange = [i for i in lstList if ("MAPPED FROM: /system/lib/libart.so") in i]
	return lstList[lstList.index(libRange[2])+1]
	
def extLOS(lstList, path):
	libRangenew = [i for i in lstList if (" MAPPED FROM: /dev/ashmem/dalvik-large object space allocation") in i]
	#return lstList[lstList.index(libRangenew[0])]
	if (libRangenew == [i for i in lstList if (" MAPPED FROM: /dev/ashmem/dalvik-large object space allocation") in i]):
		for n in range(0, 100):
			#print lstList[lstList.index(libRangenew[n])]
			return lstList[lstList.index(libRangenew[n])]
			#n = n+1
	else:
		sys.exit()
			
def extOffset(a, alist):
	#print "starting a"
	#print  a	
	[addr, start, key] = findAddr(a, alist)
	#print "Addr"
	#print addr
	#print "start"
	#print start
	a = int(str(addr), 16)
	#print "a"
	#print  a
	b = int(str(start), 16)
	#print "b"	
	#print  b 
	#print type(b)
	if (start !=0):
		offset = a - b
		#print "offset" 
		#print offset
		aPath = path+"/"+key
		#print aPath
	else:
		offset = int(str(addr), 16) - int(str(start), 16)		
		offset = 0
		aPath = None
		#sys.exit(1)
	return [aPath, offset]
	
def runtimeObj(rPath, bss, instance, memList):
	with open(rPath, 'rb') as g:
		#g.seek(getLibART(bss, instance)) --- to fix this function, extract last three digit from the runtime instance address - 0070a980
		g.seek(int(hex(0x980), 16))
		runtime = hex(struct.unpack("<I", g.read(4))[0])
		#print "Runtime Address is @ "+ runtime 
		[nPath, rAddr] = extOffset(runtime, memList)
		return [runtime, nPath, rAddr]	

def extFhandle(f):
	fhandle =  open(f, 'rb')
	return fhandle		
		
def main(path):
	instance = extRuntime(path)
	#print "Instance" + instance
	lstFile = path+"/mfetch.lst"
	lstList = parseFile(lstFile)
	listing = extAddrRange(lstList)
	#print "listing" + listing
	[memList.update({key:value}) for key, value in listing.items() if key.startswith("mem")]	
	[mapList.update({key:value}) for key, value in listing.items() if key.startswith("map")]
#mapList= OrderedDict()
#[mapList.update({key:value}) for key, value in listing.items() if key.startswith("map")]
	bss = extBss(lstList, path)
	#print bss
	#print "Large Object Space Range"
	los = extLOS(lstList, path)
	#print los
	[runtime, nPath, rAddr] = runtimeObj(lstPath(path, bss), bss, instance, memList)
	return[nPath, rAddr, memList, mapList,listing, lstList, runtime]
		
	
def extPointer(pointer, list):
	[objPath, objOff] = extOffset(pointer, list)
	if objPath is None:
		g= None
	else:
		g = extFhandle(objPath)
	#print g	
	return [g, objOff]
	

