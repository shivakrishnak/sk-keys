---
id: OSY-016
title: Interrupt and Trap
category: Operating Systems
tier: tier-1-foundations
folder: OSY-operating-systems
difficulty: ★☆☆
depends_on: OSY-009
used_by: OSY-089
related: OSY-008, OSY-009, OSY-089
tags:
  - foundational
  - interrupt
  - trap
  - hardware
  - exception
status: complete
version: 4
layout: default
parent: "Operating Systems"
grand_parent: "Technical Mastery"
nav_order: 16
permalink: /technical-mastery/osy/interrupt-trap/
---

## TL;DR

A hardware interrupt is an asynchronous signal from a
device (NIC, timer, keyboard) that preempts the current
thread to handle the event. A trap (software interrupt)
is a synchronous event from the running program (syscall,
page fault, divide-by-zero). Both enter kernel mode.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | OSY-016 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Operating Systems |
| **Tags** | interrupt, trap, IRQ, kernel mode |
| **Prerequisites** | OSY-009 |

---

### Hardware Interrupt vs Trap

```
HARDWARE INTERRUPT (asynchronous - device-initiated):
  Source: external hardware (NIC, disk, keyboard, timer)
  Timing: can happen between ANY two CPU instructions
  Examples:
    NIC: "Packet arrived on eth0!"
    Timer: "100ms tick - check for preemption"
    Disk: "I/O operation complete"
    
  CPU response:
    1. Current instruction completes
    2. CPU saves: rip, rflags, rsp to kernel stack
    3. CPU looks up IDT[irq_number] (Interrupt Descriptor Table)
    4. Jump to interrupt handler (ISR) in kernel
    5. ISR handles the event (reads packet data, etc.)
    6. ISR calls iret -> resume preempted thread

TRAP (synchronous - program-initiated):
  Source: executing program (syscall, fault, debug breakpoint)
  Timing: at a specific instruction
  Examples:
    int 0x80: Linux syscall (legacy)
    SYSCALL: x86-64 system call instruction
    Page fault: access to unmapped virtual address
    #GP: General Protection Fault (invalid memory access)
    #DE: Divide-by-zero (division by zero)
    Breakpoint: debugger INT 3 instruction
```

---

### Interrupt Handling in Linux

```
Linux interrupt handling: two-phase model

PHASE 1 - Top Half (in interrupt context, fast):
  Minimal work with interrupts disabled
  Acknowledge interrupt to hardware
  Save minimal data to kernel queue
  Schedule bottom half for later processing
  Must complete in microseconds

PHASE 2 - Bottom Half (deferred processing):
  softirq, tasklet, or workqueue
  Process the queued data
  Interrupts re-enabled (other interrupts can arrive)
  
Example - NIC receive:
  Top half: copy packet to kernel ring buffer, schedule NAPI
  Bottom half: process packet through network stack
               (IP routing, TCP reassembly, socket delivery)
  
Why two phases?
  Hardware can't wait: NIC needs immediate acknowledgment
  Processing takes time: TCP stack can't block interrupts
```

---

### Interrupts and JVM

```
JVM safepoints and interrupts:
  JVM GC requires all Java threads to stop at a safepoint.
  The JVM signals threads via a memory page flag.
  Threads poll this flag at safepoint check points.
  
  If a thread is in a system call (blocking I/O):
    OS delivers SIGPOLL/SIGALRM to interrupt the syscall
    Syscall returns EINTR (interrupted)
    JVM handles the interrupt, reaches safepoint
    
  This is why Thread.interrupt() works on blocking I/O:
    Sets interrupted flag AND sends SIGPOLL to OS thread
    OS wakes up the thread with EINTR from its I/O wait
    Java throws InterruptedException

Measure interrupt rate:
  $ cat /proc/interrupts
  # Shows per-CPU interrupt counts by IRQ
  $ vmstat 1
  # 'in' column: interrupts per second
```

---

### Textbook Definition

A hardware interrupt is an asynchronous signal from an
I/O device or timer that causes the CPU to suspend the
current execution, save state, and execute the interrupt
service routine (ISR) registered in the Interrupt
Descriptor Table (IDT). A trap (synchronous interrupt)
is raised by the executing program via a special CPU
instruction (SYSCALL) or as a result of an exception
(page fault, division by zero).

---

### Understand It in 30 Seconds

Interrupt: your phone rings while you're working. You
stop working (save state), answer the call (ISR), hang
up, return to work (restore state). Trap: you walk to
the helpdesk yourself (system call) or trip over
something (program fault). Both require "leaving" your
current task to handle the event.

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "Interrupts and system calls are the same" | System calls are synchronous traps initiated by the running program. Interrupts are asynchronous events from hardware that preempt the running program. Different source, different timing |
| "More interrupts = slower system" | High interrupt rate can cause performance issues (interrupt storms). But interrupts are essential for I/O performance. The fix is interrupt coalescing (batch multiple events into one interrupt), not eliminating interrupts |

---

### Mastery Checklist

- [ ] Knows the difference between hardware interrupt (async) and trap (sync)
- [ ] Understands two-phase interrupt handling (top half / bottom half)
- [ ] Can explain why Thread.interrupt() works on blocking I/O syscalls
- [ ] Knows how to read /proc/interrupts to monitor interrupt rates
