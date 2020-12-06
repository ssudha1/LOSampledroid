#!/usr/python
import ample_rbtree as alloc
import ampleParse as art
import ample_types as types
import ampleclass as cls
import ampledex as dx
import amplevm as jvm2
import sys, os, subprocess, struct,binascii
from collections import OrderedDict


path = sys.argv[1]
art.path = path
[nPath, rAddr, memList, mapList, listing,lstList,runtime]=art.main(path)


def readPointer(nPath, rAddr,index):
	k = art.getFhandle(nPath)
	k.seek(rAddr + index)
	addr = hex(struct.unpack("<I", k.read(4))[0])
	return addr

def readInt(nPath, rAddr,index):
	k = art.getFhandle(nPath)
	k.seek(rAddr + index)
	addr = struct.unpack("<i", k.read(4))[0]
	return addr	
	
def getHeap(nPath, rAddr):
	index = art.getIndex('Runtime', 'heap_')
	heapAddr = readPointer(nPath, rAddr,index)
	print "Heap Offset "+ heapAddr
	[heapPath, offset] = art.getOffset(heapAddr, memList)
	return [heapPath, offset]
	

	
def getlosSpace(nPath, rAddr):
	[heapPath, offset] = getHeap(nPath, rAddr)
	largeObjectSpace = readPointer(heapPath, offset,52)
	disContinousSpace = readPointer(heapPath, offset,12)
	allocSpace = readPointer(heapPath, offset,24)
	print "Large object Space Offset " + largeObjectSpace
	print "Discontinous Space offset " + disContinousSpace
	[losPath, offset] = art.getOffset(largeObjectSpace, memList)
        num_bytes_allocated = readInt(losPath, offset, 32)
        num_objects_allocated = readInt(losPath, offset,  40)
        total_bytes_allocated = readInt(losPath, offset, 48)
        total_objects_allocated = readInt(losPath, offset, 56)
	losBegin = readPointer(losPath, offset, 64)
        losEnd = readPointer(losPath, offset, 68)
	lock_ = readPointer(losPath, offset, 72)
	large_objects_ = hex(int(largeObjectSpace, 16)+112)
	#large_objects_ = readPointer(losPath, offset, 112) #Allocationtracker,stdmap-rbtree
	print "Number of bytes allocated " + str(num_bytes_allocated)
        print "Number of objects allocated " + str(num_objects_allocated)
        print "Total bytes allocated " + str(total_bytes_allocated)
        print "Total objects allocated " + str(total_objects_allocated)
        print "Large object Space Begin " + losBegin
        print "Large object space End " + losEnd
	print " Lock " + lock_
	print " Large objects " + large_objects_
	return large_objects_



def getObject(addrStart, jvm2):
	[start, end] = art.getSE(lstList)
	[aPath, offset] = art.getOffset(addrStart, mapList)
	addr = art.getFhandle(aPath)
	print "addr"
	print addr
	print offset
	addr.seek(offset)
	oClass = hex(struct.unpack("<I", addr.read(4))[0])
	if (art.validateAddr(int(oClass, 16), start, end)):
		#jvm2.searchRef(oClass)
		off = addr.tell()-4
		objSize = jvm2.dumpRefs(oClass, addr, off, start)
	
def getLosObjects(nodes_dict, mapList, memList):
	name =""
        print "********Allocation Tracking Actual Data Location*****"
	for K,V in nodes_dict.items():
		K = hex(int(K, 16)+16)
		[losPath, offset] = art.getOffset(K, memList)
		addr = art.getFhandle(losPath)
		#print addr
		#print offset
		addr.seek(offset)
		objPointer = hex(struct.unpack("<I", addr.read(4))[0])
		#print "object pointer"
                #print objPointer
		[klass, monitor, refFile, refOff]=cls.getOKlass(objPointer, mapList)
		name = cls.resolveName(klass, mapList)
		print "Klass " + name +  objPointer


def artrecover(addr, mapList):

    file_type_2 = b'\xff\xd8'
    file_type_1 = b'\x89\x50\x4e\x47'
    pos = 0
    data = addr.read()
    if file_type_1 in data:
        pos = data.find(file_type_1)
        if pos != -1:
            new_data = data[pos:]
            with open("image1.png", "wb") as ofile:
                ofile.write(new_data)
                #print file_type1
                print("Finished extracting image")
    elif file_type_2 in data:
        pos = data.find(file_type_2)
        if pos != -1:
            new_data = data[pos:]
            with open("image2.jpg", "wb") as ofile:
                ofile.write(new_data)
                print("Finished extracting image")
    else:
        print("Header not found")

def getLOSObject(addr1, jvm2):
    K = sys.argv[4]
    [losPath, offset] = art.getOffset(K, mapList)
    print "lospath" +losPath
    addr = art.getFhandle(losPath)
    ofile = hex(struct.unpack("<I", addr.read(4))[0])
    photo = artrecover(addr, mapList)
			



