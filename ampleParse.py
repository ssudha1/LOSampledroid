
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

def getSE(lstList):#address start and end
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
	
		
def getAddrRange(lstList):
	
	for entry in lstList:
		#print entry
		addRange = [j for j in entry.split() if ("0x") in j]
		start = addRange[0]
		end = addRange[1]
		listing.update({entry.split()[1]:addRange})
	return listing

def getLibART(bss, instance):
	#print instance
	insAddr =0;
	if ("[anon:.bss]") in bss: 
		addRange = [j for j in bss.split() if ("0x") in j]
		start = addRange[0]
		end = addRange[1]
		insAddr = int("0x"+instance[len(instance)-4:], 16) -  int("0x"+start[len(start)-4:], 16)
	return insAddr


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
	
		
def getRuntime(path):
	process = subprocess.check_output("nm -aS "+path+"/libart.so | grep \"_ZN3art7Runtime9instance_E\"", shell = True)
	#print "Pointer to the Runtime Offset is @ "+ process.split()[0]
	return process.split()[0]
        #process1 = subprocess.check_output("nm -aS "+path+"/libskia.so | grep \"_ZN3art7Runtime9instance_E\"", shell = True)
	#print process.split()[0]
def getBss(lstList, path):
	libRange = [i for i in lstList if ("MAPPED FROM: /system/lib/libart.so") in i]
	return lstList[lstList.index(libRange[2])+1]
	
def getLOS(lstList, path):
	libRangenew = [i for i in lstList if (" MAPPED FROM: /dev/ashmem/dalvik-large object space allocation") in i]
	#return lstList[lstList.index(libRangenew[0])]
	if (libRangenew == [i for i in lstList if (" MAPPED FROM: /dev/ashmem/dalvik-large object space allocation") in i]):
		for n in range(0, 100):
			#print lstList[lstList.index(libRangenew[n])]
			return lstList[lstList.index(libRangenew[n])]
			#n = n+1
	else:
		sys.exit()
			
def getOffset(a, alist):
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
		[nPath, rAddr] = getOffset(runtime, memList)
		return [runtime, nPath, rAddr]	

def getFhandle(f):
	fhandle =  open(f, 'rb')
	return fhandle		
		
def main(path):
	instance = getRuntime(path)
	#print "Instance" + instance
	lstFile = path+"/mfetch.lst"
	lstList = parseFile(lstFile)
	listing = getAddrRange(lstList)
	#print "listing" + listing
	[memList.update({key:value}) for key, value in listing.items() if key.startswith("mem")]	
	[mapList.update({key:value}) for key, value in listing.items() if key.startswith("map")]
#mapList= OrderedDict()
#[mapList.update({key:value}) for key, value in listing.items() if key.startswith("map")]
	bss = getBss(lstList, path)
	#print bss
	#print "Large Object Space Range"
	los = getLOS(lstList, path)
	#print los
	[runtime, nPath, rAddr] = runtimeObj(lstPath(path, bss), bss, instance, memList)
	return[nPath, rAddr, memList, mapList,listing, lstList, runtime]
	
	
def readString(dPath, dOff, size):
	g = open(dPath, 'r')
	g.seek(dOff)
	dPointer = g.read(size)
	return dPointer	

def getNames(strPointer, memList):
	[sPath, sOff] = getOffset(strPointer, memList)
	with open(sPath, 'rb') as f:
		f.seek(sOff+4)
		size = struct.unpack("<i", f.read(4))[0]
		dPointer = hex(struct.unpack("<I", f.read(4))[0])
		[dPath, dOff] = getOffset(dPointer, memList)
		dPointer = readString(dPath, dOff, size)
		return dPointer
		
def getStringClass(strOff, i):
	prettyName=''
	i.seek(strOff+8)
	count = struct.unpack("<i", i.read(4))[0]
	len = count >> 1
	if (len >0):
		i.seek(i.tell()+4)
		prettyName = i.read(len)
	return prettyName

def getIndex(Obj, member):
	index = types.art_types.get(Obj)[1].get(member)[0]
	return index
		
def getHeap(nPath, rAddr):
	index = getIndex('Runtime', 'heap_')
	heapOff = rAddr + index
	f = getFhandle(nPath)
	f.seek(heapOff)
	heapAddr = hex(struct.unpack("<I", f.read(4))[0])
	return heapAddr
	
def fromPointer(pointer, list):
	[objPath, objOff] = getOffset(pointer, list)
	#print "Object Offset"
	#print objOff
	if objPath is None:
		g= None
	else:
		g = getFhandle(objPath)
	#print g	
	return [g, objOff]
	
def getRefs(table_begin, segment_state):
	refs = []
	[f, refOff] = fromPointer(table_begin, mapList)
	counter =0
	while (counter < segment_state):
		serial = struct.unpack("<i", f.read(4))[0]
		refOff = f.tell()
		f.seek(refOff + serial*4)
		reference = hex(struct.unpack("<I", f.read(4))[0])
		if(int(reference, 16)>0):
			refs.append(reference)
		counter+=1;
		f.seek(refOff+12)
	return refs

#if(ts >0){
#	getTpointer(th, tt, ts):
#}
	
#getfile

	
	

		#get address range and subtract instance address
	
#args = len(sys.argv)
#if (args == 1) and sys.argv.endswith("lst"):
	
#	dumpPath = sys.argv[1]
