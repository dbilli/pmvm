# svmlib: Simple Virtual Machine Library

## 1. Introduction

The idea behind **svmlib** is to implement a *lightweight virtual machine* with the following features:

* Simple API 
* *JSON-izable* VM state
* Support for basic data types (integer,float, strings), arrays and dictionaries
* Lightweight threads
* Input/ouput primitives
* External code execution (function call)

### 1.1. Examples

#### Example 1

Pseudo-code:

    print(1+2)
    exit(0)

Using *svmlib*:

    from svmlib import *
    
    program = [
        SET(1),        # push value 1
        SET(2),        # push value 2
        REGSUM(),      # push 1+2
        SET("print"),  # 
        LOADSYM(),
        CALL(),
        STOP(0),       # exit(0)
    ]
    
    vm = vm_create()
    vm_run_all_threads(vm, program)
    
    print(vm['threads'][0]['output'])

#### Example 2

Pseudo-code:

    fork 
         {                       // thread 1
            print('Hello')
         }
         ,
         {                       // thread 2
            print('Hallo')
         }
         ,
         {                       // thread 3
            print('Salut')
         }

    print('END')
    

Using *svmlib*:


    from svmlib import *
    
    program = [
        FORK([4,7]),            # 0: fork +2 threads
        
        SET('Hello'),           # 1:                  thread 1
        OUTPUT(),               # 2: print('Hello')
        JUMP(7),                # 3:
        
        SET('Hallo'),           # 4:                  thread 2
        OUTPUT(),               # 5: print('Hallo')
        JUMP(7),                # 6:
        
        SET('Salut'),           # 7:                  thread 3
        OUTPUT(),               # 8: print('Salut')
        STOP(0),                # 9:
        
        SET('END'),             #10: print('END')
    ]
    
    vm = vm_create()
    vm_run_all_threads(vm, program)


#### Example 3


Call a *user-defined* function *fun1*:

    fun1('param1', 'param1', 'param1')

Using *svmlib*:

    from svmlib import *
    
    program = [
        SET('param1'),
        SET('param2'),
        SET('param3'),
        CREATETUPLE(3),      # args = ('param1,'param2','param3')
        
        SET('fun1'),         # load external function "fun1"
        LOADSYM(),
        
        CALL()               # fun1(*args)
    ]
    
    def fun1(vm_thread, a1, a2, a3):
        print("a1=%s a2=%s a3=%s" % (a1,a2,a3))
    
    exec_context = {
        'fun1': fun1,
    }
    
    vm = vm_create(exec_context)
    vm_run_all_threads(vm, program)


### 1.1. VM State is JSONable

The VM **run state** is described with  **JSON-able** data structures (tuples, lists, dictionaries). 

This permits to:

* Implement the VM in other languages very easily.
* Store/load the *VM* from an *in-memory database store* (memcache, redis, mongodb) and use them in a distribuited system.


### 1.2. Light-weight threads

The virtual machine supports **lightweight threads** used to implement *forks* of the the current execution thread. 

This permits to implement easily complex non-deterministic algorithms for patter matching logic:

* P1 | P2 | P3 : alternative
* P+, P* : repetition
* P? : optional pattern

### 1.3. Data Types

The VM supports the types used by almost every modern programming language:

* Nil/None/Null
* Numbers (integers, floats)
* Arrays (vectors)
* Dictionaries (tables/maps)

### 1.4. Input/Output

The VM implements a very basic I/O.








## 2. The VM architecture

### 2.1. The *compiled* program and Opcodes

The VM runs a *program*.

A *program* is a **array** of *instructions*.

One *instruction* (or *opcode*) is a tuple of two elements:

    ( opcode , params )

* opcode: **number**
* params: a **single** value OR an **array** of parameters.

#### Example 1

A simple exit(0) program:

    exit(0)

A possible *compiled version*:

    [
     (2, 0),        # 0: exit 0
    ]


#### Example 2:

A loop program:

    do
        pass
    while 1

A possible *compiled version*:

    [
     (1, ),         # 0: pass
     (2, 0),        # 1: JUMP 0
    ]

Example:

    (1, )                     # PASS  
    
    (2, 0)                    # STOP(0)
    
    (600, [30,55,72])         # FORK 4 threads


### 2.2. The CPU registers

The VM is a "stack based" virtual machine. VM instructions (opcodes): 

* pop values from the stack
* perform some logic
* push return value on the stack.

Example:

    
    [
     (101, 1),       # SET 1     push value 1 on the stack
     (101, 2),       # SET 2     push value 2 on the stack
     (400,  ),       # REGSUM    pop 2 values from the stack, sum them and push result on the stack
    ]

### 2.3. Threads

#### 2.3.1. Light-weight

The VM support *light-weight* threads and **do not use** OS's native threading APIs.

A thread can *fork* and create an unlimited number of *threads*.

* ID
* running state (RUNNING/TERMINATED/WAITING FOR IO)
* Registry stack
* Program Counter (PC)
* INPUT buffer
* OUTPUT buffer
* CLOCK 
* Execution context (dictionary)

The *program* is started inside the *main thread*. 

Threads do not share any data.

#### 2.3.2. Time/Clock

The VM has an internal clock. 

The *clock* is a simple integer value and rappresent the number of seconds since the epoch.

The *clock* is indipendent from the system time and must be set properly when running the VM.

#### 2.3.4. Input handling

Every thread has 2 I/O channels:

* Input channel
* Output channel

A program can read data from *input* channel and write data to *output* channel.

#### 2.3.2. Execution context and global symbols

An *execution context* is the *memory* of the virtual machine. It is a dictionary of *symbols* the program code can read and write.

#### 2.3.3. External function calling

The *program* can *call* external funtions defined in the *execution context*.

The *external* function accepts at least one parameter: the VM thread object calling the function. The other parameters are the *real* function parameters.

    from svmlib import *
    
    def power(thread_obj, n, e):
        print("CALLING POWER FROM THREAD %s" % (thread_obj['id']))
        return n ** e
    
    execution_context = {
        'pow: power
    }
    
    program = [
        ...
        ...
    ]
    
    vm = vm_create(execution_context)
    vm_run_all_threads(vm, program)


## 3. Python API

### 3.1 Creating programs (bytecode)

A program is a list of tuples opcodes. 

    program = [
        (2, 0),        # exit 0
    ]

Instead of use *tuples* you can use functions provided by **svmlib.opcodes** module. 

    from svmlib.opcodes import *

    program = [
        STOP(0)
    ]

### 3.2 Create a VM State object

Use the **vm_create** function to create a *virtual machine* object:

    from svmlib import vm_create
    
    vm = vm_create()

A *initial context* and initial *clock* can be specified:

    import time
    
    from svmlib import vm_create
    
    context = {
        'pi': 3.14
    }
    
    vm = vm_create(initial_context=context, clock=time.time())

### 3.3 Set current clock

Use **vm_set_clock** to set/change the current clock for all threads:

    import time
    
    from svmlib import vm_create, vm_set_clock

    vm = vm_create()
    
    vm_set_clock(vm, time.time())

### 3.4 Execution

In order to run a program call the **vm_run_all_threads** function. After a *run* you have to test for VM's termination with **vm_is_finished**.

    import time
    
    from svmlib import *
    
    program = [
        STOP(0)
    ]
    
    vm = vm_create()
    
    while True:
        vm_run_all_threads(vm, program)
        if vm_is_finished(vm):
            break


## Appendix 1: Opcodes table

This is the table of valid opcodes:


| Opcode #   | Opcode Name     | Operand type       | Description                                                                                     |
|:----------:|-----------------|--------------------|-------------------------------------------------------------------------------------------------|
|            | PASS            | string             | do nothing. Operand is a comment string                                                         |
|            | STOP            | integer            | Terminate the current thread. REGSTACK.append( OPEARAND )                                       |
|            |                 |                    |                                                                                                 |
|            | REGFLUSH        |                    | REGSTACK = []                                                                                   | 
|            | SET             | *                  | REGSTACK.append( OPEARAND )                                                                     | 
|            |                 |                    |                                                                                                 |
|            | CREATETUPLE     | integer            | elements = REGSTACK.pop( OPEARAND ). REGSTACK.append( tuple(elements) )                         |
|            |                 |                    |                                                                                                 |
|            | CREATEDICT      |                    | REGSTACK.append( {} )                                                                           | 
|            | DICTSETK        |                    | v,k,d = REGSTACK.pop(3). d[k] = v. REGSTACK.append( d )                                         |
|            |                 |                    |                                                                                                 |
|            | REGSUM          |                    | a,b = REGSTACK.pop(2).  REGSTACK.append( a + b )                                                |
|            | REGSUB          |                    | a,b = REGSTACK.pop(2).  REGSTACK.append( a - b )                                                |
|            |                 |                    |                                                                                                 |
|            | REGMUL          |                    | a,b = REGSTACK.pop(2).  REGSTACK.append( a * b )                                                |
|            | REGDIV          |                    | a,b = REGSTACK.pop(2).  REGSTACK.append( a / b )                                                |
|            | REGMOD          |                    | a,b = REGSTACK.pop(2).  REGSTACK.append( a % b )                                                |
|            | REGPOW          |                    | a,b = REGSTACK.pop(2).  REGSTACK.append( a ** b )                                               | 
|            |                 |                    |                                                                                                 |
|            | REGNEG          |                    | a = REGSTACK.pop(). REGSTACK.append( -a )                                                       |
|            | REGBITONE       |                    | a = REGSTACK.pop(). REGSTACK.append( ~a )                                                       |
|            | REGNOT          |                    | a = REGSTACK.pop(). REGSTACK.append( ~a )                                                       |
|            |                 |                    |                                                                                                 |
|            | REGLSHIFT       |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a << b )                                                |
|            | REGRSHIFT       |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a >> b )                                                |
|            |                 |                    |                                                                                                 |
|            | REGBITAND       |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a and b )                                               |
|            | REGBITXOR       |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a xor b )                                               |
|            | REGBITOR        |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a or  b )                                               |
|            |                 |                    |                                                                                                 |
|            | REGLT           |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a <  b )                                                |
|            | REGLTE          |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a <= b )                                                |
|            | REGGT           |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a >  b )                                                |
|            | REGGTE          |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a >= b )                                                |
|            |                 |                    |                                                                                                 |
|            | REGEQ           |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a == b )                                                |
|            | REGNEQ          |                    | a,b = REGSTACK.pop(2). REGSTACK.append( a != b )                                                |
|            |                 |                    |                                                                                                 |
|            | STORESYM        |                    | val,sym  = REGSTACK.pop(2). CONTEXT[sym] = val                                                  |
|            | LOADSYM         |                    | sym = REGSTACK.pop(). val = CONTEXT[sym]. REGSTACK.append( val )                                |
|            |                 |                    |                                                                                                 |
|            | GETATTR         |                    | obj,sym = REGSTACK.pop(2). val = obj[sym]. REGSTACK.append( val )                               |
|            |                 |                    |                                                                                                 |
|            | LOADSYMLV       |                    | sym = REGSTACK.pop(). ref = REF(CONTEXT, sym). REGSTACK.append( ref )                           |
|            | GETATTRLV       |                    | obj,sym = REGSTACK.pop(2). ref = REF(obj,sym). REGSTACK.append( ref )                           |
|            |                 |                    |                                                                                                 |
|            | JUMP            | integer            | PC = OPERAND                                                                                    |
|            | JUMPR           | integer            | PC + OPERAND                                                                                    |
|            | IFTRUE          | integer            | if REGSTACK.peek(1) then PC = OPERAND                                                           |
|            | IFFALSE         | integer            | if not REGSTACK.peek(1) then PC = OPERAND                                                       |
|            |                 |                    |                                                                                                 |
|            | FORK            | list of numbers    | Create N threads. THREAD[n].PC = OPERAND[n]                                                     |
|            |                 |                    |                                                                                                 |
|            | CALL            |                    | sym,params = REGSTACK.pop(2). fun = CONTEXT[sym]. r = fun(params). REGSTACK.append(r).          |
|            |                 |                    |                                                                                                 |
|            | OUTPUT          |                    | val = REGSTACK.pop(). write val to OUTPUT                                                       |



