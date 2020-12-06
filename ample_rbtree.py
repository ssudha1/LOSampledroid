import ample_types as types
import ampleParse as art
import sys, os, subprocess, struct,binascii
from collections import OrderedDict

nodes_dict = OrderedDict()
def nodeMeta(pointer, memList):
	[g, objOff]  = art.fromPointer(pointer, memList)
	g.seek(objOff)
	begin = hex(struct.unpack("<I", g.read(4))[0])
	tail = hex(struct.unpack("<I", g.read(4))[0])	
	return [g, g.tell(), begin, tail]
	
def get_rbtree_header(large_objects_, memList):
	[g, objOff, node_begin, node_tail] = nodeMeta(large_objects_, memList)
	g.seek(objOff)
	nodeSize = struct.unpack("<i", g.read(4))[0]
	return [node_begin,node_tail,nodeSize]

def get_node(pointer,memList):
	[g, objOff, first_node, second_node] = nodeMeta(pointer, memList)
	g.seek(objOff)
	third_node = hex(struct.unpack("<I", g.read(4))[0])
	color = struct.unpack("<b", g.read(1))[0]
	if (color==1):
		color = "Black"
	else:
		color = "Red"
	return [first_node, second_node, third_node,color]

def get_endnode(node_begin, memList):
	[ed_parent_node, ed_right_node, ed_left_node,color] = get_node(node_begin, memList)
	if (ed_parent_node != '0x0'):
		return "error"
	return [ed_parent_node, ed_right_node, ed_left_node,color]

def get_rootnode(ed_left_node, memList):
	[rt_parent_node, rt_right_node, rt_left_node,color] = get_node(ed_left_node, memList)
        print "****Allocation Tracking Map Details****"
	print rt_parent_node +" "+rt_right_node+" "+rt_left_node+" "+ color
	return [rt_parent_node, rt_right_node, rt_left_node,color]

def rb_traversal(node_begin, node_tail, nodeSize, memList):
	[ed_parent_node, ed_right_node, ed_left_node,color] = get_endnode(node_begin, memList)	
	[rt_parent_node, rt_right_node, rt_left_node,color] = get_rootnode(ed_left_node, memList)	
	counter= 0
	if (rt_parent_node== node_begin):
		nodes_dict.update({node_begin:color})
		nodes_dict.update({ed_left_node:color})
		nodes = OrderedDict()
		if rt_right_node!='0x0':
			nodes.update({rt_right_node:ed_left_node})
		if rt_left_node!='0x0':	
			nodes.update({rt_left_node:ed_left_node})
		while counter < nodeSize-3:
			node = nodes.keys()[counter]
			parent = nodes[node]
			[first_node, second_node, third_node,color] = get_node(node, memList)
			if first_node == parent:
				if second_node!='0x0':
					nodes.update({second_node:node})
				if node!=node_tail and third_node!='0x0':
					nodes.update({third_node:node})
			else:
				if first_node!='0x0':
					nodes.update({first_node:node})
				if second_node!='0x0':
					nodes.update({second_node:node})
			nodes_dict.update({node:color})
			counter+=1
	else:
		return "Error in nodes"
	return nodes_dict

	
	
