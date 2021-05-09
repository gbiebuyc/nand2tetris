#!/usr/bin/env python3
from sys import argv
import re

if len(argv) < 2:
	print("usage: ./VMTranslator.py sourcefile.vm")
	quit()

if not argv[1].endswith('.vm'):
	print("bad file")
	quit()

sourcefile = open(argv[1], 'r')
outfilename = re.sub(r'\.vm$', '.asm', argv[1])
outfile = open(outfilename, 'w')

segments = {
	'local': 'LCL',
	'argument': 'ARG',
	'this': 'THIS',
	'that': 'THAT',
}

push_segment = """\
@segmentPtr
D=M
@i
A=D+A // addr = segmentPtr + i
D=M
@SP
A=M
M=D   // *SP = *addr
@SP
M=M+1 // SP++
"""

pop_segment = """\
@segmentPtr
D=M
@i
D=D+A
@R13
M=D   // addr = segmentPtr + i
@SP
M=M-1 // SP--
A=M
D=M
@R13
A=M
M=D   // *addr = *SP
"""

push_constant = """\
@i
D=A
@SP
A=M
M=D
@SP
M=M+1
"""

push_temp = """\
@5
D=A
@i
A=D+A // addr = 5 + i
D=M
@SP
A=M
M=D   // *SP = *addr
@SP
M=M+1 // SP++
"""

pop_temp = """\
@5
D=A
@i
D=D+A
@R13
M=D   // addr = 5 + i
@SP
M=M-1 // SP--
A=M
D=M
@R13
A=M
M=D   // *addr = *SP
"""

push_variable = """\
@variable
D=M
@SP
A=M
M=D
@SP
M=M+1 // SP++
"""

pop_variable = """\
@SP
M=M-1 // SP--
A=M
D=M
@variable
M=D
"""

operation = """\
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
M=DoperationM
@SP
M=M+1
"""

operation_unary = """\
@SP
M=M-1
A=M
M=operationM
@SP
M=M+1
"""

comparison = """\
@SP
M=M-1
A=M
D=M
@SP
M=M-1
A=M
D=M-D  // D = SP[-2] - SP[-1]
@YESline
D;comparison
(NOline)
@SP
A=M
M=0
@DONEline
0;JMP
(YESline)
@SP
A=M
M=-1
(DONEline)
@SP
M=M+1
"""

for i_line, line in enumerate(sourcefile):
	line = re.sub(r'//.*$', '', line).strip()
	if len(line) == 0:
		continue
	command = line.split()
	print('// ' + line, file=outfile)
	instructions = None

	if command[0] == 'push':
		if command[1] == 'constant':
			instructions = push_constant.replace('i', command[2])
		elif command[1] in segments:
			instructions = push_segment.replace('i', command[2]
				).replace('segmentPtr', segments[command[1]])
		elif command[1] == 'temp':
			instructions = push_temp.replace('i', command[2])
		elif command[1] == 'static':
			instructions = push_variable.replace('variable', 'Foo.' + command[2])
		elif command[1] == 'pointer':
			pointer = ['THIS', 'THAT'][int(command[2])]
			instructions = push_variable.replace('variable', pointer)
	elif command[0] == 'pop':
		if command[1] in segments:
			instructions = pop_segment.replace('i', command[2]
				).replace('segmentPtr', segments[command[1]])
		elif command[1] == 'temp':
			instructions = pop_temp.replace('i', command[2])
		elif command[1] == 'static':
			instructions = pop_variable.replace('variable', 'Foo.' + command[2])
		elif command[1] == 'pointer':
			pointer = ['THIS', 'THAT'][int(command[2])]
			instructions = pop_variable.replace('variable', pointer)
	elif command[0] == 'add':
		instructions = operation.replace('operation', '+')
	elif command[0] == 'sub':
		instructions = operation_unary.replace('operation', '-') + \
		               operation.replace('operation', '+')
	elif command[0] == 'and':
		instructions = operation.replace('operation', '&')
	elif command[0] == 'or':
		instructions = operation.replace('operation', '|')
	elif command[0] == 'neg':
		instructions = operation_unary.replace('operation', '-')
	elif command[0] == 'not':
		instructions = operation_unary.replace('operation', '!')
	elif command[0] == 'eq':
		instructions = comparison.replace('comparison', 'JEQ').replace('line', str(i_line))
	elif command[0] == 'lt':
		instructions = comparison.replace('comparison', 'JLT').replace('line', str(i_line))
	elif command[0] == 'gt':
		instructions = comparison.replace('comparison', 'JGT').replace('line', str(i_line))

	if instructions:
		print(instructions, file=outfile)
	else:
		print('warning: not implemented: ' + line)
