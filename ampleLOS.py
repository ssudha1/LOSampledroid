#!/usr/python
#import ample_rbtree as atsafemap
import amplerec as art
import ample_types as types
import amplevm as jvm2
import sys, os, subprocess, struct,binascii
from collections import OrderedDict


path = sys.argv[1]
art.path = path
[nPath, rAddr, memList, mapList, listing,lstList,runtime]=art.main(path)

def extOKlass(reference, mapList):
	[g, objOff] = art.fromPointer(reference, mapList)
	#print g
	#print objOff
	if g is None:
		return ['0x0','0x0', None, objOff]
	else:
		g.seek(objOff)
		klass = hex(struct.unpack("<I", g.read(4))[0])
		#print klass
		monitor = hex(struct.unpack("<I", g.read(4))[0])
	        #print monitor
		#print g
		#print objOff
		return [klass,monitor, g, objOff]
	
def resolveName(klass, mapList):
	name ='Cannot Be Resolved'
	nameOff = extNamePointer(klass, mapList)
	if (int(nameOff, 16)> 0):
		[i, strOff] = art.fromPointer(nameOff, mapList)
		if i is None:
			name ='Cannot Be Resolved'
		else:
			name = art.extStringClass(strOff, i)
	return name	
		
def extNamePointer(klass, mapList):
	nameOff = art.extIndex('Class_Obj', 'name_')
	[k, clOff] = art.fromPointer(klass, mapList)
	if k is not None:
		k.seek(clOff+nameOff)
		nameOff = hex(struct.unpack("<I", k.read(4))[0])
		return nameOff
	else:
		return "0x0"
def readPointer(nPath, rAddr,index):
	k = art.extFhandle(nPath)
	k.seek(rAddr + index)
	addr = hex(struct.unpack("<I", k.read(4))[0])
	return addr

def readInt(nPath, rAddr,index):
	k = art.extFhandle(nPath)
	k.seek(rAddr + index)
	addr = struct.unpack("<i", k.read(4))[0]
	return addr	
	
def extHeap(nPath, rAddr):
	index = art.extIndex('Runtime', 'heap_')
	heapAddr = readPointer(nPath, rAddr,index)
	print "Heap Offset "+ heapAddr
	[heapPath, offset] = art.extOffset(heapAddr, memList)
	return [heapPath, offset]
	

	
def extlosSpace(nPath, rAddr):
	[heapPath, offset] = extHeap(nPath, rAddr)
	largeObjectSpace = readPointer(heapPath, offset,52)
	disContinousSpace = readPointer(heapPath, offset,12)
	allocSpace = readPointer(heapPath, offset,24)
	print "Large object Space Offset " + largeObjectSpace
	print "Discontinous Space offset " + disContinousSpace
	[losPath, offset] = art.extOffset(largeObjectSpace, memList)
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



def extObject(addrStart, jvm2):
	[start, end] = art.extSE(lstList)
	[aPath, offset] = art.extOffset(addrStart, mapList)
	addr = art.extFhandle(aPath)
	print "addr"
	print addr
	print offset
	addr.seek(offset)
	oClass = hex(struct.unpack("<I", addr.read(4))[0])
	if (art.validateAddr(int(oClass, 16), start, end)):
		#jvm2.searchRef(oClass)
		off = addr.tell()-4
		objSize = jvm2.dumpRefs(oClass, addr, off, start)
	
def extLosObjects(nodes_dict, mapList, memList):
	name =""
        print "********Allocation Tracking Actual Data Location*****"
	for K,V in nodes_dict.items():
		K = hex(int(K, 16)+16)
		[losPath, offset] = art.extOffset(K, memList)
		addr = art.extFhandle(losPath)
		#print addr
		#print offset
		addr.seek(offset)
		objPointer = hex(struct.unpack("<I", addr.read(4))[0])
		#print "object pointer"
                #print objPointer
		[klass, monitor, refFile, refOff]=extOKlass(objPointer, mapList)
		name = resolveName(klass, mapList)
		print "Klass " + name +" " + "array" + " " +objPointer


def artrecover(addr, mapList):

    file_type_2 = b'\xff\xd8'
    file_type_1 = b'\x89\x50\x4e\x47\x0D\x0A\x1A\x0A'
    file_type_3 = b'\x4A\x46\x49\x46'
    file_type_4 = b'\x45\x78\x69\x66'
    file_type_5 = b'\x25\x50\x44\x46' 
    file_type_6 = b'\x49\x49\x2A\x00'

    pos = 0
    data = addr.read()
    if file_type_1 in data:
        pos = data.find(file_type_1)
        if pos != -1:
            new_data = data[pos:]
            with open("image1.png", "wb") as ofile:
                ofile.write(new_data)
                #print file_type1
                print("Finished extracting image and save a copy so that new image decoded is not overwritten")
    elif file_type_2 in data:
        pos = data.find(file_type_2)
        if pos != -1:
            new_data = data[pos:]
            with open("image2.jpg", "wb") as ofile:
                ofile.write(new_data)
                print("Finished extracting image and save a copy so that new image decoded is not overwritten")
    elif file_type_3 in data:
        pos = data.find(file_type_3)
        if pos != -1:
            new_data = data[pos:]
            with open("image.jfif", "wb") as ofile:
                ofile.write(new_data)
                print("Finished extracting image and save a copy so that new image decoded is not overwritten")
    elif file_type_4 in data:
        pos = data.find(file_type_4)
        if pos != -1:
            new_data = data[pos:]
            with open("image.exif", "wb") as ofile:
                ofile.write(new_data)
                print("Finished extracting image and save a copy so that new image decoded is not overwritten")
    elif file_type_5 in data:
        pos = data.find(file_type_5)
        if pos != -1:
            new_data = data[pos:]
            with open("doc.pdf", "wb") as ofile:
                ofile.write(new_data)
                print("Finished extracting file and save a copy so that new file decoded is not overwritten")
    elif file_type_6 in data:
        pos = data.find(file_type_6)
        if pos != -1:
            new_data = data[pos:]
            with open("image.tiff", "wb") as ofile:
                ofile.write(new_data)
                print("Finished extracting file and save a copy so that new file decoded is not overwritten")
    else:
        print("The files recovered are not forensically relevant and include char array or resource files of the acquired application")

def extLOSObject(addr1, jvm2):
    K = sys.argv[4]
    [losPath, offset] = art.extOffset(K, mapList)
    print "lospath" +losPath
    addr = art.extFhandle(losPath)
    ofile = hex(struct.unpack("<I", addr.read(4))[0])
    photo = artrecover(addr, mapList)
			


