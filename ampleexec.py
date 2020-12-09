#!/usr/bin/python
import ample_atsafemap as atsafemap
import ampleLOS as heap
import amplerec as art
import amplevm as jvm2

from collections import OrderedDict
import sys,struct



if(sys.argv[2]=="LOS"):
	nPath = heap.nPath
	rAddr = heap.rAddr
	memList = heap.memList
	mapList = heap.mapList
	large_objects_ = heap.extlosSpace(nPath, rAddr)
	[node_begin, node_tail, nodeSize] = atsafemap.ext_rbtree_header(large_objects_, memList)
	nodes_dict = atsafemap.rb_traversal(node_begin, node_tail, nodeSize, memList)
	for K, V in nodes_dict.items():
		print K+"\t"+V
	heap.extLosObjects(nodes_dict, mapList, memList)
	if len(sys.argv)==3:
	    print "Get the multimedia data by decoding the address above"
	elif (sys.argv[3]=="decodelosobject"):
	    addr = sys.argv[4]
	    print "@ Address "+addr
            print " The extracted large object details"
	    heap.extLOSObject(addr, jvm2)
	
	

