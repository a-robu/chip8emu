import sys
import random
import time
import pygame
import Tkinter, tkFileDialog
import beep

MATCH_VBEMU_MODE = False
BACK_COLOR = (36, 60, 165)
FORE_COLOR = (40, 150, 220)
pygame.init()

ZOOM = 10
disp_width = 64
disp_height = 32

window = pygame.display.set_mode((disp_width * ZOOM, disp_height * ZOOM))

root = Tkinter.Tk()
root.withdraw()

filename = "E:/Dropbox/Programming Projects/2013 Q2/tetris.c8"
filename = "E:/Dropbox/Programming Projects/2013 Q2/invaders.c8"
#filename = "E:/Dropbox/Programming Projects/2013 Q2/pong2.c8"

'''
filename = "rs-chip8asm\minimal.c8"

import subprocess
a = subprocess.call([r'rs-chip8asm\mchipper.exe',
                     r'rs-chip8asm\minimal.c8',
                     r'rs-chip8asm\minimal.chp'])

#'''
filename = tkFileDialog.askopenfilename()
f = open(filename, 'rb')
program_data = f.read()
f.close()

#0,1,2...9,A,B,C,D,E,F
fontset = [ 0xF0, 0x90, 0x90, 0x90, 0xF0,
            0x20, 0x60, 0x20, 0x20, 0x70,
            0xF0, 0x10, 0xF0, 0x80, 0xF0,
            0xF0, 0x10, 0xF0, 0x10, 0xF0,
            0x90, 0x90, 0xF0, 0x10, 0x10,
            0xF0, 0x80, 0xF0, 0x10, 0xF0,
            0xF0, 0x80, 0xF0, 0x90, 0xF0,
            0xF0, 0x10, 0x20, 0x40, 0x40,
            0xF0, 0x90, 0xF0, 0x90, 0xF0,
            0xF0, 0x90, 0xF0, 0x10, 0xF0,
            0xF0, 0x90, 0xF0, 0x90, 0x90,
            0xE0, 0x90, 0xE0, 0x90, 0xE0,
            0xF0, 0x80, 0x80, 0x80, 0xF0,
            0xE0, 0x90, 0x90, 0x90, 0xE0,
            0xF0, 0x80, 0xF0, 0x80, 0xF0,
            0xF0, 0x80, 0xF0, 0x80, 0x80 ]

key_map = {pygame.K_x: 0x0,
           pygame.K_1: 0x1,
           pygame.K_2: 0x2,
           pygame.K_3: 0x3,
           pygame.K_q: 0x4,
           pygame.K_w: 0x5,
           pygame.K_e: 0x6,
           pygame.K_a: 0x7,
           pygame.K_s: 0x8,
           pygame.K_d: 0x9,
           pygame.K_z: 0xa,
           pygame.K_c: 0xb,
           pygame.K_4: 0xc,
           pygame.K_r: 0xd,
           pygame.K_f: 0xe,
           pygame.K_v: 0xf}

code_to_key_map = {}
for key in key_map:
    code_to_key_map[key_map[key]] = key

if not MATCH_VBEMU_MODE:
    mem = [0 for x in range(0x1000)]
else:
    mem = [0 for x in range(0xFFFF)]

#load fonts
for i in range(len(fontset)):
    if not MATCH_VBEMU_MODE:
        mem[i] = fontset[i]
    else:
        mem[i + 0x1000] = fontset[i]
    #TODO! put this back

#load program
for i in range(len(program_data)):
    mem[0x200 + i] = ord(program_data[i])

disp = []
def clear_disp():
    global disp
    disp = [[0 for y in range(disp_height)] for x in range(disp_width)]
clear_disp()

def render_disp():    
    window.fill(BACK_COLOR)
    for x in range(len(disp)):
        for y in range(len(disp[0])):
            if disp[x][y]:
                window.fill(FORE_COLOR, (x * ZOOM, y * ZOOM, ZOOM, ZOOM))
           

def byte_to_list(byte):
    b = byte
    l = []
    for i in range(8):
        l.append(b & 1)
        b = b >> 1
    l.reverse()
    return l
    
pc = 0x200
stack = []
V = [0 for x in range(0x10)]
I = 0
delay_timer = 0
sound_timer = 0
dirty_screen = False
last_time = time.time()
time_elapsed = 0

def print_ch(addr, length):
    for i in range(length):
        l = byte_to_list(mem[addr + i])
        for a in range(len(l)):
            if l[a] is 1:
                l[a] = '#'
            else:
                l[a] = ' '
        print ''.join(l)
        
if MATCH_VBEMU_MODE:
    trace = []
    with open("trace.txt") as tr:
        while True:
            line  = tr.readline()
            if line == "":
                break
            pc_op_vs = {}
            pc_op_vs['pc'] = int(line, 16)
            pc_op_vs['op'] = int(tr.readline(), 16)
            pc_op_vs['vs'] = []
            for i in range(0, 16):
                pc_op_vs['vs'].append(int(tr.readline(), 16))
            pc_op_vs['I'] = int(tr.readline(), 16) 
            trace.append(pc_op_vs)

    trace_i = 0


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            print '	'.join([hex(x) for x in range(len(V))])
            print '	'.join([hex(x) for x in V])
            print "---"
            print ('0000000000' + bin(V[0xA])[2:])[-8:]
            print ('0000000000' + bin(V[0xB])[2:])[-8:]
            print ('0000000000' + bin(V[0xC])[2:])[-8:]
            sys.exit()

    opcode = (mem[pc] << 8) + mem[pc + 1]
    
    if MATCH_VBEMU_MODE:
        if not (pc == trace[trace_i]['pc'] and opcode == trace[trace_i]['op'] and V == trace[trace_i]['vs'] and I == trace[trace_i]['I']):
            if I + 0x1000 != trace[trace_i]['I']:
                print
                print
                print
                print "--------------------- AHA!!"
                print "--- prev trace"
                print "his pc:", hex(trace[trace_i - 1]['pc']), "his opcode:", hex(trace[trace_i - 1]['op']), "his I:", hex(trace[trace_i - 1]['I'])
                print "his Vs:", [hex(i) + " " + hex(trace[trace_i - 1]['vs'][i]) for i in range(len(trace[trace_i - 1]['vs']))]
                print "--- curr trace"
                print "my  pc:", hex(pc), "my  opcode:", hex(opcode), "my  I:", hex(I)
                print "his pc:", hex(trace[trace_i]['pc']), "his opcode:", hex(trace[trace_i]['op']), "his I:", hex(trace[trace_i]['I'])
                print "my Vs:", [hex(i) + " " + hex(V[i]) for i in range(len(V))]
                print "his Vs:", [hex(i) + " " + hex(trace[trace_i]['vs'][i]) for i in range(len(trace[trace_i]['vs']))]
                diffs = []
                for i in range(16):
                    if V[i] != trace[trace_i]['vs'][i]:
                        diffs.append(hex(i))
                if diffs:
                    print "|||||||| V DIFFS FOUND:", diffs
                print "---------------------------------"
                print
                print
                print

        trace_i += 1

    
    pc += 2

    #00E0 - CLS - Clear the display
    if opcode == 0x00E0:
        clear_disp()            

    #00EE Return from a subroutine.
    elif opcode == 0x00EE:
        pc = stack.pop()

    #1nnn - JP addr - Jump to location nnn.
    elif opcode & 0xF000 == 0x1000:
        pc = opcode & 0x0FFF

    #2nnn - CALL addr - Call subroutine at nnn.
    elif opcode & 0xF000 == 0x2000:
        stack.append(pc)
        pc = opcode & 0x0FFF
    
    #3xkk - SE Vx, byte Skip next instruction if Vx = kk.
    elif opcode & 0xF000 == 0x3000:
        if V[(opcode & 0x0F00) >> 8] == opcode & 0x00FF:
            pc += 2
    
    #4xkk - SNE Vx, byte - Skip next instruction if Vx != kk.
    elif opcode & 0xF000 == 0x4000:
        if V[(opcode & 0x0F00) >> 8] != opcode & 0x00FF:
            pc += 2
    
    #5xy0 - SE Vx, Vy - Skip next instruction if Vx = Vy.
    elif opcode & 0xF000 == 0x5000:
        if V[(opcode & 0x0F00) >> 8] == V[(opcode & 0x00F0) >> 4]:
            pc += 2

    #6xkk - LD Vx, byte - Set Vx = kk.
    elif opcode & 0xF000 == 0x6000:
        V[(opcode & 0x0F00) >> 8] = opcode & 0x00FF

    #7xkk - ADD Vx, byte - Set Vx = Vx + kk.
    elif opcode & 0xF000 == 0x7000:
        V[(opcode & 0x0F00) >> 8] = (V[(opcode & 0x0F00) >> 8] + opcode & 0x00FF) % 0x100

    #8xy0 - LD Vx, Vy - Set Vx = Vy.
    elif opcode & 0xF00F == 0x8000:
        V[(opcode & 0x0F00) >> 8] = V[(opcode & 0x00F0) >> 4]
        

    #8xy1 - OR Vx, Vy - Set Vx = Vx OR Vy.
    elif opcode & 0xF00F == 0x8001:
        V[(opcode & 0x0F00) >> 8] |= V[(opcode & 0x00F0) >> 4]        

    #8xy2 - AND Vx, Vy - Set Vx = Vx AND Vy.
    elif opcode & 0xF00F == 0x8002:       
        V[(opcode & 0x0F00) >> 8] &= V[(opcode & 0x00F0) >> 4]        

    #8xy3 - XOR Vx, Vy - Set Vx = Vx XOR Vy.
    elif opcode & 0xF00F == 0x8003:
        V[(opcode & 0x0F00) >> 8] ^= V[(opcode & 0x00F0) >> 4]

    #8xy4 - ADD Vx, Vy - Set Vx = Vx + Vy, set VF = 1 if carry
    elif opcode & 0xF00F == 0x8004: 
        result = V[(opcode & 0x0F00) >> 8] + V[(opcode & 0x00F0) >> 4]
        if (V[(opcode & 0x0F00) >> 8] + V[(opcode & 0x00F0) >> 4]) > 0xFF:
            #TODO fix the above expr
            V[0xF] = 1
        else:
            V[0xF] = 0
        V[(opcode & 0x0F00) >> 8] = result % 0x100
            
    #8xy5 - SUB Vx, Vy - Set Vx = Vx - Vy, set VF = NOT borrow.
    elif opcode & 0xF00F == 0x8005:
        if V[(opcode & 0x0F00) >> 8] >= V[(opcode & 0x00F0) >> 4]:
            V[0xF] = 1
        else:
            V[0xF] = 0
        V[(opcode & 0x0F00) >> 8] = (V[(opcode & 0x0F00) >> 8] - V[(opcode & 0x00F0) >> 4]) % 0x100

    #8xy6 - SHR Vx {, Vy} - Set Vx = Vx SHR 1.
    elif opcode & 0xF00F == 0x8006:
        V[0xF] = V[(opcode & 0x0F00) >> 8] & 0x1
        V[(opcode & 0x0F00) >> 8] = V[(opcode & 0x0F00) >> 8] >> 1

    #8xy7 - SUBN Vx, Vy - Set Vx = Vy - Vx, set VF = NOT borrow.
    elif opcode & 0xF00F == 0x8007:
        if V[(opcode & 0x00F0) >> 4] >= V[(opcode & 0x0F00) >> 8]:
            V[0xF] = 1
        else:
            V[0xF] = 0
        V[(opcode & 0x0F00) >> 8] = (V[(opcode & 0x00F0) >> 4] -
                                   V[(opcode & 0x0F00) >> 8]) % 0x100

    #8xyE - SHL Vx {, Vy} - Set Vx = Vx SHL 1.
    elif opcode & 0xF00F == 0x800E:
        V[(opcode & 0x0F00) >> 8] = (V[(opcode & 0x0F00) >> 8] << 1) % 0x100

    #9xy0 - SNE Vx, Vy - Skip next instruction if Vx != Vy.
    elif opcode & 0xF00F == 0x9000:
        if V[(opcode & 0x0F00) >> 8] != V[(opcode & 0x00F0) >> 4]:
            pc += 2

    #Annn - LD I, addr - Set I = nnn.
    elif opcode & 0xF000 == 0xA000:
        I = opcode & 0x0FFF

    #Bnnn - JP V0, addr - Jump to location nnn + V0.
    elif opcode & 0xF000 == 0xB000:
        pc = (opcode & 0x0FFF) + V[0x0]

    #Cxkk - RND Vx, byte - Set Vx = random byte AND kk.
    elif opcode & 0xF000 == 0xC000:
        if not MATCH_VBEMU_MODE:
            V[(opcode & 0x0F00) >> 8] = (opcode & 0x00FF) & random.randint(0, 0xFF)
        else:
            V[(opcode & 0x0F00) >> 8] = (opcode & 0x00FF) & 100
        
    #Dxyn - DRW Vx, Vy, nibble - Display sprite at I at (Vx, Vy), VF = coll
    elif opcode & 0xF000 == 0xD000:
        V[0xF] = 0
        for row in range(opcode & 0xF):
            this_row = byte_to_list(mem[I + row])
            for x_offset in range(8):
                if this_row[x_offset]:                        
                    x = (V[(opcode & 0x0F00) >> 8] + x_offset) % disp_width
                    y = (V[(opcode & 0x00F0) >> 4] + row) % disp_height

                    if disp[x][y]:
                        V[0xF] = 1
                    
                    disp[x][y] = this_row[x_offset] ^ disp[x][y]

        dirty_screen = True

    #Ex9E - SKP Vx - Skip next instruction if key with the value of Vx is pressed.
    elif opcode & 0xF0FF == 0xE09E:
        if pygame.key.get_pressed()[code_to_key_map[V[(opcode & 0x0F00) >> 8]]]:
            pc += 2
                    
    #ExA1 - SKNP Vx - Skip next instruction if key with the value of Vx is not pressed.
    elif opcode & 0xF0FF == 0xE0A1:
        if not pygame.key.get_pressed()[code_to_key_map[V[(opcode & 0x0F00) >> 8]]]:
            pc += 2

    #Fx07 - LD Vx, DT - Set Vx = delay timer value.
    elif opcode & 0xF0FF == 0xF007:
        if not MATCH_VBEMU_MODE:
            V[(opcode & 0x0F00) >> 8] = delay_timer
        else:
            V[(opcode & 0x0F00) >> 8] = 0

    #Fx0A - LD Vx, K - Wait for a key press, store the value of the key in Vx.
    elif opcode & 0xF0FF == 0xF00A:
        key = None

        for pygame_key in key_map:
            if pygame.key.get_pressed()[pygame_key]:
                if pygame_key in key_map:
                    key = key_map[pygame_key]
                    break

        while not key:                
            ev = pygame.event.wait()
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.KEYDOWN:
                if ev.key in key_map:
                    key = key_map[ev.key]
            time.sleep(0.0000001)
        V[(opcode & 0x0F00) >> 8] = key

    #Fx15 - LD DT, Vx - Set delay timer = Vx.
    elif opcode & 0xF0FF == 0xF015:
        delay_timer = V[(opcode & 0x0F00) >> 8]

    #Fx18 - LD ST, Vx - Set sound timer = Vx.
    elif opcode & 0xF0FF == 0xF018:
        sound_timer = V[(opcode & 0x0F00) >> 8]
        if sound_timer:
            beep.start()

    #Fx1E - ADD I, Vx - Set I = I + Vx.
    elif opcode & 0xF0FF == 0xF01E:
        I += V[(opcode & 0x0F00) >> 8]

    #Fx29 - LD F, Vx - Set I = location of sprite for digit Vx.
    elif opcode & 0xF0FF == 0xF029:
        if not MATCH_VBEMU_MODE:
            I = V[(opcode & 0x0F00) >> 8] * 5
        else:
            I = 0x1000 + V[((opcode & 0x0F00) >> 8)] * 5
        #TODO

    #Fx33 - LD B, Vx - Store BCD representation of Vx in memory locations I, I+1, and I+2.    
    elif opcode & 0xF0FF == 0xF033:
        vx = V[(opcode & 0x0F00) >> 8]        

        mem[I + 2] = vx % 10
        vx /= 10

        mem[I + 1] = vx % 10
        vx /= 10
        
        mem[I] = vx % 10

    #Fx55 - LD [I], Vx - Store registers V0 through Vx in memory starting at location I.
    elif opcode & 0xF0FF == 0xF055:        
        for i in range(((opcode & 0x0F00) >> 8) + 1):
            mem[I + i] = V[i]

    #Fx65 - LD Vx, [I] - Read registers V0 through Vx from memory starting at location I.
    elif opcode & 0xF0FF == 0xF065:
        for i in range(((opcode & 0x0F00) >> 8) + 1):
            V[i] = mem[I + i]

    elif opcode == 0x0000:
        print "GIE"
        break
    
    else:
        print '------ not decoded ------',hex(opcode)

    
    now = time.time()
    dt = now - last_time
    time_elapsed += dt
    if time_elapsed > 1.0 / 60:
        if delay_timer > 0:
            delay_timer -= 1
        if sound_timer > 0:
            sound_timer -= 1
        else:
            beep.stop()
        time_elapsed = 0
    last_time = now

    if dirty_screen:
        render_disp()
        pygame.display.update()
    
    time.sleep(0.0000001)

render_disp()
pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    time.sleep(0.05)
            



