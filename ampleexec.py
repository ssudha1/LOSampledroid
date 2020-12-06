import ample_rbtree as alloc
import ampleLOS as heap
import ampleParse as art
import amplevm as jvm2

from collections import OrderedDict
import sys,struct



if(sys.argv[2]=="LOS"):
	nPath = heap.nPath
	rAddr = heap.rAddr
	memList = heap.memList
	mapList = heap.mapList
	large_objects_ = heap.getlosSpace(nPath, rAddr)
	[node_begin, node_tail, nodeSize] = alloc.get_rbtree_header(large_objects_, memList)
	nodes_dict = alloc.rb_traversal(node_begin, node_tail, nodeSize, memList)
	for K, V in nodes_dict.items():
		print K+"\t"+V
	heap.getLosObjects(nodes_dict, mapList, memList)
	if len(sys.argv)==3:
	    print "Get the multimedia data by decoding the address above"
	elif (sys.argv[3]=="decodelosobject"):
	    addr = sys.argv[4]
	    print "@ Address "+addr
            print " The extracted large object details"
	    heap.getLOSObject(addr, jvm2)
	elif (sys.argv[3]=="getarray"):
	    addr = sys.argv[4]
	    print "@ Address "+addr
            print "The extracted large object primitive array"
	    heap.getObject(addr, jvm2)
	

