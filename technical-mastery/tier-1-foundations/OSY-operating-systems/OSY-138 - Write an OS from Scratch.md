---
id: OSY-138
title: Write an OS from Scratch
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★★★
depends_on: OSY-001, OSY-022, OSY-060, OSY-131
used_by: []
related: OSY-131, OSY-134, OSY-139
tags:
  - OS-development
  - from-scratch
  - bootloader
  - kernel
  - hands-on
  - assembly
  - C
  - learning
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 138
permalink: /technical-mastery/osy/write-os-from-scratch/
---

## TL;DR

Writing a minimal OS from scratch is the most effective
way to understand every concept in this category. You do
not need to write a production OS - just getting to "Hello,
World" from the bootloader teaches: x86 boot sequence,
privilege levels, memory mapping, and interrupt handling.
The key insight: an OS is just code that runs first and
sets up abstractions for everyone else.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-138 |
| **Difficulty** | ★★★ Expert |
| **Category** | Operating Systems |
| **Tags** | OS from scratch, bootloader, kernel development, OSDev, QEMU, learning project |
| **Prerequisites** | OSY-001, OSY-022, OSY-060, OSY-131 |

---

### Why Build an OS (Even Partially)

```
What you learn that no amount of reading teaches:
  
  1. Every abstraction has a cost
     File: just bytes at known disk offsets + a name in a table
     Process: a set of registers + a memory map + a stack
     Thread: a register set + a stack pointer; sharing everything else
     
  2. The kernel is not magic
     It's code that runs with CPL=0 (ring 0)
     That's the ONLY difference between kernel and your code
     
  3. Memory layout becomes visceral
     When you write the linker script yourself:
     you understand EXACTLY where code/data/stack lives
     
  4. Interrupts become real
     When YOUR interrupt handler fires on a keyboard press:
     you understand preemption, not just describe it
     
  5. Bugs become instructive
     Triple fault (CPU resets): your GDT is wrong
     Page fault at 0x00000000: null pointer dereferenced in kernel
     Random reboot: stack overflow; you overwrote the kernel itself
     All of these are learning experiences that stick
```

---

### Minimum Viable OS: What You Need

```
Required knowledge:
  C: comfortable with pointers, structs, bitwise ops
  Assembly: basic understanding of MOV, PUSH, POP, INT, IRET
  x86: rings (0/3), segments, basic memory model
  
Tools needed:
  nasm: x86 assembler (for bootloader)
  gcc: compiler with -m32 or -m64; --freestanding
  ld: linker (for custom linker scripts)
  qemu-system-x86_64: x86 emulator (test without real hardware)
  
The minimum OS boot sequence:
  1. CPU powers on; loads BIOS from ROM
  2. BIOS: POST (power-on self-test); loads Master Boot Record (MBR)
  3. MBR (512 bytes): our first code; we write this
  4. MBR: loads the kernel from disk
  5. Kernel: sets up protected mode (32-bit) or long mode (64-bit)
  6. Kernel: initializes GDT (Global Descriptor Table)
  7. Kernel: enables paging
  8. Kernel: sets up IDT (Interrupt Descriptor Table)
  9. Kernel: runs first process
  
Reaching "Hello World" on screen:
  VGA text buffer: 0xB8000 in physical memory
  Write ASCII + color byte to this address
  Character appears on screen
  No driver needed: it's just a memory address
```

---

### Stage 1: Bootloader (Assembly)

```nasm
; boot.asm - BIOS bootloader (MBR stage)
; Loaded at 0x7C00 by BIOS
; Must fit in 512 bytes

[BITS 16]           ; real mode (16-bit on boot)
[ORG 0x7C00]        ; BIOS loads us here

start:
    ; Set up segments
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00  ; stack grows down from 0x7C00
    
    ; Print "OS Loading..."
    mov si, msg
    call print_string
    
    ; Load kernel from disk (sectors 2+)
    ; In a real bootloader: use BIOS int 0x13
    ; For simplicity: assume kernel loaded by multiboot/GRUB
    
    ; Switch to protected mode
    cli                 ; disable interrupts
    lgdt [gdt_desc]     ; load GDT
    
    ; Set protected mode bit in CR0
    mov eax, cr0
    or eax, 0x1
    mov cr0, eax
    
    ; Far jump to flush instruction prefetch + set CS
    jmp 0x08:protected_mode_start
    
print_string:
    mov ah, 0x0E    ; BIOS teletype function
.loop:
    lodsb           ; load byte from [si] into al; si++
    test al, al     ; is it null terminator?
    jz .done
    int 0x10        ; BIOS print char
    jmp .loop
.done:
    ret

msg db "OS Loading...", 13, 10, 0

; GDT (Global Descriptor Table)
gdt_start:
    dq 0x0000000000000000   ; null descriptor
gdt_code:
    dq 0x00CF9A000000FFFF   ; code segment (ring 0)
gdt_data:
    dq 0x00CF92000000FFFF   ; data segment (ring 0)
gdt_end:

gdt_desc:
    dw gdt_end - gdt_start - 1
    dd gdt_start

[BITS 32]
protected_mode_start:
    ; We're in 32-bit protected mode!
    mov ax, 0x10    ; data segment selector
    mov ds, ax
    mov ss, ax
    mov esp, 0x90000  ; stack at 576KB
    
    ; Write "Hello from Kernel!" to VGA
    mov edi, 0xB8000  ; VGA text buffer
    mov al, 'H'
    mov ah, 0x0F     ; white on black
    mov [edi], ax
    ; ... (write rest of string)
    
    ; Halt the CPU
    hlt
    jmp $            ; infinite loop (if HLT returns)

times 510 - ($ - $$) db 0  ; pad to 510 bytes
dw 0xAA55                   ; boot signature (required!)
```

---

### Stage 2: C Kernel

```c
/* kernel.c - minimal kernel entry point */

/* VGA text buffer at physical 0xB8000 */
#define VGA_BUFFER ((volatile unsigned short *)0xB8000)
#define VGA_WHITE_ON_BLACK 0x0F00
#define VGA_COLS 80
#define VGA_ROWS 25

static int cursor_row = 0;
static int cursor_col = 0;

void vga_putchar(char c) {
    if (c == '\n') {
        cursor_row++;
        cursor_col = 0;
        return;
    }
    
    int idx = cursor_row * VGA_COLS + cursor_col;
    VGA_BUFFER[idx] = VGA_WHITE_ON_BLACK | (unsigned char)c;
    
    cursor_col++;
    if (cursor_col >= VGA_COLS) {
        cursor_col = 0;
        cursor_row++;
    }
}

void vga_print(const char *str) {
    while (*str) {
        vga_putchar(*str++);
    }
}

/* Called from assembly after protected mode setup */
void kernel_main(void) {
    vga_print("Hello from kernel!\n");
    vga_print("Kernel is running in 32-bit protected mode.\n");
    vga_print("CR0 bit 0 (protected mode enable) = 1\n");
    
    /* Halt forever */
    while (1) {
        __asm__("hlt");
    }
}
```

```bash
# Build commands:
nasm -f bin boot.asm -o boot.bin
gcc -m32 -ffreestanding -nostdlib -c kernel.c -o kernel.o
ld -m elf_i386 -Ttext 0x1000 -e kernel_main \
   --oformat binary kernel.o -o kernel.bin

# Concatenate: boot sector + kernel
cat boot.bin kernel.bin > os.img

# Pad to a disk image
dd if=/dev/zero bs=512 count=2880 > floppy.img
dd if=os.img of=floppy.img conv=notrunc

# Test in QEMU:
qemu-system-x86_64 -fda floppy.img
# Should see "Hello from kernel!" on screen
```

---

### Stage 3: What to Implement Next

```
After "Hello World", the interesting parts:

1. Interrupt handling (IDT setup)
   - Handle keyboard interrupts
   - Handle timer interrupts (PIT chip)
   - Handle page faults (exception 14)
   
2. Memory management
   - Physical page allocator (bitmap or free list)
   - Virtual memory (paging)
   - Simple malloc/free
   
3. Processes
   - Process structure (registers, memory map)
   - Context switch (save/restore registers)
   - Simple round-robin scheduler
   
4. System calls
   - int 0x80 or syscall instruction
   - Transition from user mode (ring 3) to kernel (ring 0)
   
5. A file system
   - FAT12 on floppy image (simple)
   - Or: read-only tarball as initial filesystem (like early Linux)
   
6. A shell
   - Read keyboard input
   - Parse commands
   - Execute programs

Good resources:
  OSDev Wiki: wiki.osdev.org
  Little Book About OS Development (free, online)
  Writing a Simple Operating System from Scratch (Nick Blundell, PDF)
  xv6: MIT teaching OS (modern C, x86/RISC-V, ~10K lines, very readable)
```

---

### Java-OS Connection

```
After building even a minimal OS, Java concepts become crystal clear:

  Java synchronized block -> you implement mutex with LOCK XCHG
  Java Thread -> you implement process context switch
  Java new Object() -> you implement a heap allocator
  Java File.read() -> you implement VFS open/read
  Java OOM -> you implement the physical page allocator running out
  JVM -Xmx -> you set the limit on the physical page allocator
  
The moment you write context switch assembly:
  You understand EXACTLY what a JVM thread is
  You understand EXACTLY why creating threads has overhead
  You understand EXACTLY what "user space vs kernel space" means
  
This is the most valuable 20 hours you can spend on OS education.
```
