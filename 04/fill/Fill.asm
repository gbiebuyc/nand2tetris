// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

(START)
@KBD
D=M
@DRAW_BLACK
D;JNE
@DRAW_WHITE
D;JEQ

(DRAW_BLACK)
@8192
D=A
(LOOP_BLACK)
D=D-1
@SCREEN
A=A+D
M=-1
@LOOP_BLACK
D;JGE
@START
0;JMP

(DRAW_WHITE)
@8192
D=A
(LOOP_WHITE)
D=D-1
@SCREEN
A=A+D
M=0
@LOOP_WHITE
D;JGE
@START
0;JMP
