import sys
import argparse
import shutil
import numpy as np
from copy import deepcopy
from collections import deque

class Node:
	def __init__(self, c, f, left = None, right = None):
		self.c = c
		self.f = f
		self.left = left
		self.right = right 


def buildTree(count):
	count_pairs = count.items()
	count_iter = iter(count_pairs)
	pair1 = next(count_iter, '-1')
	pair2 = next(count_iter, '-1')
	if pair2 == '-1':
		return Node(pair1[0], pair1[1])
	del count[pair1[0]]
	del count[pair2[0]]

	root = Node(None, pair1[1] + pair2[1])
	root.left = Node(pair1[0], pair1[1])
	root.right = Node(pair2[0], pair2[1])

	if count:
		root_ = buildTree(count)
		final_root = Node(None, root.f + root_.f)
		final_root.left  =  root
		final_root.right =  root_
		return final_root

	return root


def inorder(root):
	if root == None:
		return
	inorder(root.left)
	print(root.c)
	inorder(root.right)

def findHuffCodes(root, huff_codes, code):
	if root is None:
		return
	if root.left == None and root.right == None:
		huff_codes[root.c] = code
		return
	findHuffCodes(root.left, huff_codes, code + '0')
	findHuffCodes(root.right, huff_codes, code + '1')

def height(root):
	if root is None:
		return -1
	return max(height(root.left), height(root.right)) + 1

def treeToText(root, huff_codes):
	q = deque()
	q.append(root)
	text = '{0:08b}'.format(len(huff_codes))

	while len(q) > 0:
		node = q.popleft()
		if node.c != None:
			print(node.c)
			text += '1' + '{0:08b}'.format(ord(node.c)) + '{0:08b}'.format(len(huff_codes[node.c])) + huff_codes[node.c]
		if node.left != None:
			q.append(node.left)
		if node.right != None:
			q.append(node.right)
	return text

def encode(input_file, output_file):
	count = {}
	file = open(input_file)
	data = file.read()
	print(data)
	for c in data:
		if c in count:
			count[c] += 1
		else:
			count[c] = 1
	
	count = {k: v for k, v in sorted(count.items(), key=lambda item: item[1], reverse = True)}
	print(count)
	root = buildTree(count)
	huff_codes = {}
	findHuffCodes(root, huff_codes, '')
	compressed = ''
	for c in data:
		compressed += huff_codes[c]

	tree_text = treeToText(root, huff_codes)
	compress_pad, tree_pad = 0, 0
	if len(compressed) <= 8:
		compress_pad = 8 - len(compressed)
	else:
		compress_pad = 8 - (len(compressed) % 8)
	if len(tree_text) <= 8:
		tree_pad = 8 - len(tree_text)
	elif len(tree_text) % 8 != 0:
		tree_pad = 8 - (len(tree_text) % 8)
	
	compressed += '0' * compress_pad
	tree_text += '0' * tree_pad
	write_data = '{0:08b}'.format(tree_pad)
	write_data += '{0:08b}'.format(compress_pad)
	b = bytearray()
	b.append(int(write_data[0:8], 2))
	b.append(int(write_data[8:16], 2))
	#print(len(tree_text), len(compressed))
	for i in range(0, len(tree_text), 8):
		byte = tree_text[i:i+8]
		b.append(int(byte, 2))
	for i in range(0, len(compressed), 8):
		byte = compressed[i:i+8]
		b.append(int(byte, 2))

	out_file = open(output_file, 'wb')
	out_file.write(b)
	out_file.close()





def decode(input_file, output_file):
	out_file = open(input_file, 'rb')
	byte = out_file.read()
	huff_codes = {}
	mem = np.frombuffer(byte, dtype=np.uint8)
	mem=np.array(['{0:08b}'.format(mem[b]) for b in np.ndindex(mem.shape)])
	string = ''
	tree_pad = int(mem[0], 2)
	compress_pad = int(mem[1], 2)
	u_chars = int(mem[2], 2)
	for s in range(3, len(mem)):
		string += mem[s]
	i = 0
	for uc in range(u_chars):
		char = chr(int(string[i+1:i+9], 2))
		i += 9
		code_len = int(string[i:i+8], 2)
		i += 8
		code = string[i:i+code_len]
		i += code_len
		huff_codes[code] = char
	while tree_pad > 0:
		i += 1
		tree_pad -= 1
	
	code = ''
	out = open(output_file, 'w')
	while i < len(string)-compress_pad:
		code += string[i]
		if code in huff_codes:
			out.write(huff_codes[code])
			code = ''
		i += 1



def get_options(args=sys.argv[1:]):
	parser = argparse.ArgumentParser(description="Huffman compression.")
	groups = parser.add_mutually_exclusive_group(required=True)
	groups.add_argument("-e", type=str, help="Encode files")
	groups.add_argument("-d", type=str, help="Decode files")
	parser.add_argument("-o", type=str, help="Write encoded/decoded file", required=True)
	options = parser.parse_args()
	return options


if __name__ == "__main__":
	options = get_options()
	if options.e is not None:
		encode(options.e, options.o)
	if options.d is not None:
		decode(options.d, options.o)
