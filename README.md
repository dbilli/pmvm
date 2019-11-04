# Pattern Matching Virtual Machine

*PMVM*  is a naive **virtual machine** that can consume a stream of (complex) data and recognize complex patterns.

[TOC]

## Introduction

The idea behind PMVM is to implement complex pattern matching by running a pattern matching program inside a simple VM.

Very complex patterns can be implemented by adding feature the virtual machine.

### Light-weight threads

The virtual machine supports **lightweight threads** used to implement *forks*  of the the current execution thread. 

This permits to implement easily complex (non-deterministic) patters like:
* A|B|C
* A+ 
* A?
* A*

### PMVM is JSONable

The VM **run state** is described with  **JSON-able** data structures (tuples, lists, dictionaries). 

This permits to:

* Implement the VM in other languages very easily.
* Store/load the *VM* from an *in-memory database store* (memcache, redis, mongodb) and use them in a distribuited system.


## How it works

### The VM architecture

TODO

### The *compiled* program 

The VM runs a *compiled program*.  A *compiled program* is a list of *instructions*.

An *instructions* is a tuple of two elements:

* OPCODE: a **string**
* PARAM(s): a **single** parameter or a **list** of parameters.

#### Example 1

A simple exit(0) program:

    exit(0)

The bytecode:

    [
     ( 'SET' , 0 ),
    ]

#### Example 2:

A loop program:

    do
        pass
    while 1

The bytecode:

    [
     ( 'PASS', None ),        # address 0
     ( 'JUMP', 0    ),        # address 1
    ]


### Opcodes

#### Basic opcodes

    PASS                           do nothing and continue
    
    JUMP <pos>
                                   Jumps the current threads to the position <pos>
    
    SETTIMER <n seconds>           
                                   Set timer
    
    INPUT [match]                  Compare [match] with the current input element.
                                   If [match] does not match with input, the current thread blocks.
    
    MATCH <flag>
                                   The threads's status "matched" to <flag>
    
    SET <value>                    
                                   Set r0 to <value>
    
    ADD <n>
    
    EQUAL <n> <pos>                
                                   If register r0 == <n> jumps to position <pos>
    LTE   <n> <pos>                If register r0 <= <n> jumps to position <pos>
                                   Add <n> to register r0.

#### Fork opcode

    FORK <pos1>, <pos2>, ....
                                   Create N execution threads, each thread starts from pos1, pos2, ...

#### Stack opcodes

    STACKPOP  <n>
                                   Remove <n> from stack
    STACKGET  <pos>                
                                   Read value from stack and stores in r0
    STACKSET  <value>              
                                   Save r0 in stack[$sp+pos]
    STACKSETV <pos> <value>        
                                   Save <value> in stack[$sp+pos]
    STACKPUSHV <value>              
                                   Append <valu> to stack and increm[$sp]

### Threads

TODO

### Input handling

TODO


## The API

TODO
