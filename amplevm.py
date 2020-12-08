#!/usr/bin/python
import ampleLOS as heap
import ampleParse as art
import ample_types as types
import ampleclass as cls
import sys, os, subprocess, struct,binascii
from collections import OrderedDict

path = sys.argv[1]
art.path = path
[nPath, rAddr, memList, mapList, listing, lstList,runtime]=art.main(path)

def extPointer(addr, off):
	[tpath, offset] = art.extOffset(addr, memList)	
	g = art.extFhandle(tpath)
	g.seek(offset+off)
	newAddr = hex(struct.unpack("<I", g.read(4))[0])
	return newAddr

def extObjectArray(length_, addr, array):
	while (length_ >0):
		array.append(hex(struct.unpack("<I", addr.read(4))[0]))
		length_ =length_-1
	return array	
	
def extCharArray(length_, addr, array):
	length_= length_*2
	while (length_ >0):
		array.append(struct.unpack("<c", addr.read(1))[0])
		length_ =length_-1
	return array		
def extIntArray(length_, addr, array):
	while (length_ >0):
		array.append(struct.unpack("<i", addr.read(4))[0])
		length_ =length_-1
	return array
def extFloatArray(length_, addr, array):
	while (length_ >0):
		array.append(struct.unpack("<f", addr.read(4))[0])
		length_ =length_-1
	return array
def extShortArray(length_, addr, array):
	while (length_ >0):
		array.append(struct.unpack("<H", addr.read(2))[0])
		length_ =length_-1
	return array
def extBArray(length_, addr, array):#Byte and Bool
	while (length_ >0):
		array.append(struct.unpack("<B", addr.read(1))[0])
		length_ =length_-1
	return array	
def extLongArray(length_, addr, array):
	while (length_ >0):
		array.append(struct.unpack("<Q", addr.read(8))[0])
		length_ =length_-1
	return array	
	
def checkArray(name,length_, addr, array):
	if('[Ljava.lang.String' in name):
		array = extStringArray(length_, addr, array)
	elif(name =='[C'):	
		array = extCharArray(length_, addr, array)
		length_ = length_*2
	elif(name =='[B' or name =='[Z'):	
		array = extBArray(length_, addr, array)	
	elif(name =='[S'):	
		array = extShortArray(length_, addr, array)	
		length_ = length_*2
	elif(name =='[I'):	
		array = extIntArray(length_, addr, array)
		length_ = length_*4
	elif(name =='[L'):	
		array = extLongArray(length_, addr, array)	
		length_ = length_*8
	elif(name =='[F'):	
		array = extFloatArray(length_, addr, array)	
		length_ = length_*4
	elif(name =='[D'):	
		array = extDoubleArray(length_, addr, array)
		length_ = length_*8	
	elif (name.startswith('[L')):	
		array = extObjectArray(length_, addr, array)
		length_ = length_*4
	return [array, length_]
	

			
def extClsObj(ref, refFile, refOff, fDict, addr, off):
	[name, classFlag, primType, ifields_,methods_, sfields_, dexCache, objSize, refSize, super_class_] =  cls.extClassMembers(ref, refFile, refOff, mapList)
	if(name and name.startswith('[')):
		array=[]
		addr.seek(off+8)
		length_ = struct.unpack("<i", addr.read(4))[0]
		[array, length_] = checkArray(name,length_, addr, array)
		objSize = 8+4+length_
		print "Object Size " + str(objSize)
		print "The array data recovered for "+name +" is " +str(array)
	elif(name == "java.lang.String"):
		prettyName=''
		addr.seek(off+8)
		count = struct.unpack("<i", addr.read(4))[0]
		l = count >> 1
		if (l >0):
			addr.seek(addr.tell()+4)
			prettyName = addr.read(l)
			print "The data for "+name +" is " +prettyName
		else:
			print "Null String"
		objSize = 8+4+4+l
	else:
		print "Object not be dereferenced"
		objSize=8	
	return objSize

def dumpRefs(ref, addr, off, start):
	[klass, monitor, refFile, refOff]=cls.extOKlass(ref, mapList)
	if klass =='0x0':
		print "Invalid address"
		print "\n"
		objSize=8
		return objSize	
	name = cls.resolveName(klass, mapList)
	fDict=OrderedDict()
	objSize=0
	print name
	if ('java.lang.Class' in name):
		objSize = extClsObj(ref, refFile, refOff,fDict, addr, off)
		print "\n"
	elif ('java.lang.String' in name):
		print " Class is String array represented as java.lang.resources representing Android resources in the app dump"
		refFile.seek(refOff+8)
		count = struct.unpack("<i", refFile.read(4))[0]
		l = count >> 1
		if (l >0):
			refFile.seek(refFile.tell()+4)
			prettyName = refFile.read(l)
			print prettyName
		else:
			print "Null String"
		objSize = 8 #8 = object inheritance, 8=count+hash, l = length of string
		print "\n"
	elif (name and name.startswith('[')):
		print "*******The details of the recovered data by AmpleDroid is*******"
		print "Reference Class is an "+ name +" Array "
		array=[]
		#[i, arrayObjOff] = art.fromPointer(ref, mapList)
		#addr.seek(off+8)
		refFile.seek(refOff+8)
		arrSize = struct.unpack("<i", refFile.read(4))[0]
		print "Array size is "+str(arrSize)
		array = checkArray(name,arrSize, refFile, array)
		if array:
			print "The array data for "+name +" is " +str(array)
		#objSize = 8+4+len(array)#8 = object inheritance, 4=position for length of array, len = length of array data
		objSize=8
		print "\n"
	else:
		print "All details revealed"
	return objSize


