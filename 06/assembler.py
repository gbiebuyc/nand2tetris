#!/usr/bin/env python3
from sys import argv
import re

if len(argv) < 2:
	print("usage: ./assembler.py sourcefile.asm")
	quit()

if not argv[1].endswith('.asm'):
	print("bad file")
	quit()

sourcefile = open(argv[1], 'r')
outfilename = re.sub(r'\.asm$', '.hack', argv[1])
outfile = open(outfilename, 'w')

comp_translation = {
	'0': '101010',
	'1': '111111',
	'-1': '111010',
	'D': '001100',
	'A': '110000',
	'!D': '001101',
	'!A': '110001',
	'-D': '001111',
	'-A': '110011',
	'D+1': '011111',
	'A+1': '110111',
	'D-1': '001110',
	'A-1': '110010',
	'D+A': '000010',
	'D-A': '010011',
	'A-D': '000111',
	'D&A': '000000',
	'D|A': '010101',
}

dest_translation = {
	'0': '000',
	'M': '001',
	'D': '010',
	'MD': '011',
	'A': '100',
	'AM': '101',
	'AD': '110',
	'AMD': '111',
}

jump_translation = {
	'0': '000',
	'JGT': '001',
	'JEQ': '010',
	'JGE': '011',
	'JLT': '100',
	'JNE': '101',
	'JLE': '110',
	'JMP': '111',
}

symbol_table = {
	'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3,
	'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
	'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11,
	'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
	'SCREEN': 16384,
	'KBD': 24576,
	'SP': 0,
	'LCL': 1,
	'ARG': 2,
	'THIS': 3,
	'THAT': 4,
}

# First pass
label_addr = 0
for line in sourcefile:
	line = re.sub(r'\s', '', line)
	line = re.sub(r'//.*$', '', line)
	if len(line) == 0:
		continue
	match = re.match(r'^\((.*?)\)', line)
	if match:
		label = match.group(1)
		symbol_table[label] = label_addr
		continue
	label_addr += 1

# Second pass
sourcefile.seek(0)
n = 16
for line in sourcefile:
	line = re.sub(r'\s', '', line)
	line = re.sub(r'//.*$', '', line)
	if len(line) == 0:
		continue
	if line[0] == '(':
		continue
	if line[0] == '@':
		val = line[1:]
		if val in symbol_table:
			val = symbol_table[val]
		elif val.isdigit():
			val = int(val)
		else:
			symbol_table[val] = n
			val = n
			n += 1
		print(f'0{val:015b}', file=outfile)
	else:
		dest = comp = jump = '0'
		match1 = re.match(r'^(.*)=(.*)$', line)
		match2 = re.match(r'^(.*);(.*)$', line)
		if match1:
			dest, comp = match1.groups();
		elif match2:
			comp, jump = match2.groups();
		instr = '111'
		if 'M' in comp:
			instr += '1'
			comp = comp.replace('M', 'A')
		else:
			instr += '0'
		instr += comp_translation[comp]
		instr += dest_translation[dest]
		instr += jump_translation[jump]
		print(instr, file=outfile)
