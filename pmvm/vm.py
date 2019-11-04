
"""

The Virtual Machine
======================

TIME       ---------|---------|---------|---------|---------|---------|--------->

input         t0  t1   t3       t4 t5 t6       t7
                
VM EXEC             *         *         *         *
VM clock            t0        t3        t4        t7



Virtual Machine opcodes:

BASE OPCODES
============

   PASS                           do nothing and continue
   
   JUMP <pos>
                                  Jumps the current threads to the position <pos>

   FORK <pos1>, <pos2>, ....
                                  Create N execution threads, each thread starts from pos1, pos2, ...

   SETTIMER <n seconds>           
                                  Set timer

   INPUT [match]                  Compare [match] with the current input element.
                                  If [match] does not match with input, the current thread blocks.

   SET <value>                    
                                  Set r0 to <value>

   ADD <n>
                                  Add <n> to register r0.


STACK OPCODES
=============

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
   
   
   





   
   MATCH <flag>
                                  The threads's status "matched" to <flag>
   
   EQUAL <n> <pos>                
                                  If register r0 == <n> jumps to position <pos>
   LTE   <n> <pos>                If register r0 <= <n> jumps to position <pos>
   
   SET <n>
                                  Set register r0 to <n>
   

"""

import time
import copy

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def DEBUG(*args):
    print(' '.join([str(a) for a in args]))
    pass 

def DEBUG_SLEEP():
    #time.sleep(0.3)
    pass

def DEBUG_FORMAT_PROGRAM(program):
    s = ''
    for i,r in enumerate(program): s += "%3d %s %s\n" % (i, r[0],r[1])
    return s
    

def DEBUG_PRINT_PROGRAM(program):
    print(DEBUG_FORMAT_PROGRAM(program))
    pass

#----------------------------------------------------------------------#
# Exceptions                                                           #
#----------------------------------------------------------------------#

class VMException(Exception):
    pass

class VMInvalidOperation(VMException):
    pass

#----------------------------------------------------------------------#
# OPCODES                                                              #
#----------------------------------------------------------------------#

OP_CODE_PASS = 'PASS'

def PASS():
    return (OP_CODE_PASS,None)

#----------------------------------------------------------------------#

OP_CODE_JUMP  = 'JUMP'

def JUMP(addr):
    return ( OP_CODE_JUMP , addr )

#----------------------------------------------------------------------#

OP_CODE_FORK = 'FORK'

def FORK(addresses):
    return ( OP_CODE_FORK, addresses )

#----------------------------------------------------------------------#

OP_CODE_SETTIMER  = 'SETTIMER'

def SETTIMER(seconds):
    return ( OP_CODE_SETTIMER , seconds )
    
#----------------------------------------------------------------------#

OP_CODE_INPUT = 'INPUT'

def INPUT(input_matcher):
    """
    The object "input_matcher" must be an object implementing the __eq__ operator.
    
    This object will be compared with virtual machine "input" elements.
    
    Example:
        class InputMatcher(object):

            def __init__(self, data):
                self.data = data

            def __eq__(self, other):
                return self.data == other
    """
    return (OP_CODE_INPUT, input_matcher)    

#----------------------------------------------------------------------#

OP_CODE_SET  = 'SET'

def SET(val):
    return ( OP_CODE_SET, val)

#----------------------------------------------------------------------#

OP_CODE_ADD  = 'ADD'

def ADD(val):
    return ( OP_CODE_ADD, val)

#----------------------------------------------------------------------#

OP_CODE_EQUAL  = 'EQUAL'

def EQUAL(val, addr):
    return ( OP_CODE_EQUAL , (val, addr) )

#----------------------------------------------------------------------#

OP_CODE_LT   = 'LT'

def LT(val, addr):
    return ( OP_CODE_LT	 , (val, addr) )

#----------------------------------------------------------------------#

OP_CODE_MATCH = 'MATCH'

def MATCH(flag=True):
    return (OP_CODE_SET, 0 if flag else -1)

#----------------------------------------------------------------------#

OP_CODE_STACKPUSH  = 'STACKPUSH' #
OP_CODE_STACKPOP   = 'STACKPOP'  #<n>
OP_CODE_STACKGET   = 'STACKGET'  #<pos>
OP_CODE_STACKSET   = 'STACKSET'  #<pos>                Save <value> in stack[$sp+pos]

OP_CODE_STACKPUSHV = 'STACKPUSHV' #<value>              Append <valu> to stack and increm[$sp]
OP_CODE_STACKSETV  = 'STACKSETV' #<pos> <value>        Save <value> in stack[$sp+pos]

def STACKPUSH():      
    return (OP_CODE_STACKPUSH, None)

def STACKPOP(n):           
    return (OP_CODE_STACKPOP, n)

def STACKSET(pos):  
    return (OP_CODE_STACKSET, pos)

def STACKGET(pos):         
    return (OP_CODE_STACKGET, pos)


def STACKPUSHV(value):  
    return (OP_CODE_STACKPUSHV, value)

def STACKSETV(pos, value):  
    return (OP_CODE_STACKSETV, (pos,value))



#----------------------------------------------------------------------#
# Virtual Machine state                                                #
#----------------------------------------------------------------------#

_tid = 0

THREAD_TERMINATED = 0
THREAD_RUNNING    = 1
THREAD_WAIT_IO    = 2


def VM_THREAD(pc=0):
    
    global _tid
    
    thread = {
        'id'             : _tid,             # internal ID

        '_stats': {
            'op_count' : 0
        },

        'state'          : THREAD_RUNNING,   
        'clock'          : 0,                # Current execution clock

        'pc'             : pc,               # Program counter
        'r0'             : 0,
        
        'timer_clock'    : None,             # The clock to the next timer
        
        'input'          : None,             # Input to consume 
        
        'sp'             : 0,                # Stack Pointer
        'stack'          : [],
    }
    _tid += 1

    return thread

def VM_STATE():

    state = {
        'threads'       : [],                   # Current threads of execution
    }
    return state








































#----------------------------------------------------------------------#




#----------------------------------------------------------------------#


#----------------------------------------------------------------------#







#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def vm_init( vm_run_state, program ):

    # Create the first main thread
    main_thread = VM_THREAD()
    vm_run_state['threads'].append( main_thread )
    
    vm_bootstrap( vm_run_state, program)

    return

def vm_bootstrap( vm_run_state, program ):
    return vm_run_all_threads( vm_run_state, program )

def vm_is_finished( vm_run_state ):

    nt = len(vm_run_state['threads'])

    if nt == 0:
        return True

    if nt == len([ t for t in vm_run_state['threads'] if t['state'] == THREAD_TERMINATED ]):
        return True
    
    return False

def vm_set_clock( vm_run_state, clock=None ):

    clock = clock if clock is not None else time.time()

    for t in vm_run_state['threads']:
        t['clock'] = clock

def vm_set_input( vm_run_state, input_data):

    for t in vm_run_state['threads']:

        if t['state'] == THREAD_TERMINATED:
            continue

        t['input'] = [ input_data ]

        #t['state'] = THREAD_RUNNING




def vm_run_all_threads(vm_run_state, program):


    DEBUG("WAKING?")

    for t in  vm_run_state['threads']:
        if t['state'] == THREAD_WAIT_IO:
            DEBUG("\t THREAD:", "id", t['id'], "state", t['state'], "timer", t['timer_clock'])

            if t['input']:
                t['state'] = THREAD_RUNNING
                DEBUG("\t\tWAKEUP")

            if t['timer_clock'] is not None and t['timer_clock'] <= t['clock']:
                DEBUG("\t\tTIMEOUT (%s / %s)" % (t['timer_clock'], t['clock']))
                t['r0'] = -1
                t['state'] = THREAD_TERMINATED 


    threads_to_execute = [ t for t in  vm_run_state['threads'] if t['state'] != THREAD_TERMINATED ]

    while threads_to_execute:

        DEBUG("TURN")
        for t in threads_to_execute:
            DEBUG("\t THREAD:", t)
        DEBUG( "" )
        
        for thread in threads_to_execute:
            vm_run_thread(vm_run_state, program, thread)
            DEBUG_SLEEP()

        # Execute only running threads
        threads_to_execute = [ t for t in vm_run_state['threads'] if t['state'] == THREAD_RUNNING]

    return 


def vm_run_thread(vm_run_state, program, thread):

    DEBUG("\t", "EXECUTING THREAD", thread['id'])
    

    while thread['state'] == THREAD_RUNNING:

            pc = thread['pc']
            if pc >= len(program):
                DEBUG( "\t", "\t", "REACHED END OF PROGRAM" )
                thread['state'] = THREAD_TERMINATED
                break
                
            opcode, params = program[pc]
            
            DEBUG( "\t", "\t pc=%s/%s -> opcode=%s params=%s" % (pc, len(program), opcode, params) )
            DEBUG( "\t", "\t", "\t", "%s" % (thread) )
            
            if opcode == OP_CODE_PASS:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                continue

            if opcode == OP_CODE_JUMP:
                thread['_stats']['op_count'] += 1

                pc2 = params
                
                if pc2 >= len(program):
                    raise VMInvalidOperation("Invalid JUMP to %s (pc:%s)" % (pc2, pc))
                
                thread['pc'] = pc2

                continue



            if opcode == OP_CODE_SETTIMER:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                seconds = params
                
                thread['timer_clock'] = thread['clock'] + seconds

                continue

            if opcode == OP_CODE_FORK:
                thread['_stats']['op_count'] += 1

                addresses = params

                pc += 1
                thread['pc'] = pc

                for jump in addresses:

                    thread2 = VM_THREAD(jump)

                    thread2['state'         ] = THREAD_RUNNING
                    thread2['clock'         ] = thread['clock']
                    thread2['stack'         ] = copy.copy(thread['stack'])
                    
                    thread2['_stats'] = {}
                    thread2['_stats'].update( thread['_stats'] )
                    
                    t2_input = None
                    if thread['input'] is not None:
                        t2_input = [ data for data in thread['input'] ]
                    thread2['input'] = t2_input
                    
                    DEBUG( "\t", "\t", "\t", "NEW THREAD", thread2 )
                    vm_run_state['threads'].append( thread2 )

                continue

            if opcode == OP_CODE_INPUT:
                thread['_stats']['op_count'] += 1
                
                input_match = params
                
                thread['r0'] = -1

                # Input? Try to consume it.
                if thread['input']:

                    input_to_process = thread['input'][0]

                    if input_to_process == input_match:

                        thread['input'].pop(0)
                        
                        DEBUG( "\t", "\t", "\t", "CONSUMED" )
                            
                        thread['r0'] = 0
                        
                        pc += 1
                        thread['pc'] = pc

                        continue
                        
                    else:
                        if thread['timer_clock'] is not None:
                            DEBUG( "\t", "\t", "\t", "NOT MATCHED. WAIT" )
                            thread['state'] = THREAD_WAIT_IO
                            continue
                        else:
                            thread['r0'] = -1
                            thread['state'] = THREAD_TERMINATED
                            DEBUG( "\t", "\t", "\t", "NOT MACHED. EXIT!" )
                            break

                else:
                    DEBUG( "\t", "\t", "\t", "STOPPED" )
                    thread['state'] = THREAD_WAIT_IO
                    continue

            if opcode == OP_CODE_SET:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                val = params

                thread['r0'] = val
                
                continue

            if opcode == OP_CODE_ADD:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                val = params

                thread['r0'] += val
                
                continue

            if opcode == OP_CODE_EQUAL:
                thread['_stats']['op_count'] += 1
            
                pc += 1
                thread['pc'] = pc
                
                val, addr = params
                
                if thread['r0'] == val:
                    thread['pc'] = addr
            
                continue
            
            if opcode == OP_CODE_LT:
                thread['_stats']['op_count'] += 1
            
                pc += 1
                thread['pc'] = pc
            
                val, addr = params
            
                if thread['r0'] < val:
                    thread['pc'] = addr
                    
                continue







            if opcode == OP_CODE_STACKPUSH:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                value = thread['r0']

                thread['stack'].append(value)

                continue


            if opcode == OP_CODE_STACKPOP:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                n = params

                stack_len = len(thread['stack'])
                thread['stack'] = thread['stack'][:stack_len-n]

                continue

            if opcode == OP_CODE_STACKSET:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                pos = params
                
                value = thread['r0']

                if pos >= 0: pos = thread['sp'] + pos         
                else       : pos = len(thread['stack']) + pos 

                thread['stack'][pos] = value

                continue

            if opcode == OP_CODE_STACKGET:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                pos = params

                if pos >= 0: pos = thread['sp'] + pos 
                else       : pos = len(thread['stack']) + pos 

                value = thread['stack'][ pos ]

                thread['r0'] = value

                continue

            if opcode == OP_CODE_STACKPUSHV:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                value = params

                thread['stack'].append(value)

                continue

            if opcode == OP_CODE_STACKSETV:
                thread['_stats']['op_count'] += 1

                pc += 1
                thread['pc'] = pc

                pos, value = params

                if pos >= 0: pos = thread['sp'] + pos         
                else       : pos = len(thread['stack']) + pos 

                thread['stack'][pos] = value

                continue


            raise VMException("Invalid opcode: %s (pc:%s)" % (opcode, pc))


def vm_free_terminated_threads(vm_run_state):
    vm_run_state['threads'] = [ t for t in vm_run_state['threads'] if t['state'] != THREAD_TERMINATED ]


def vm_run(vm_run_state, program):

    DEBUG("-----------------")
    DEBUG("RUN")#, input_to_process)
    
    vm_run_all_threads(vm_run_state, program)
    
    vm_free_terminated_threads(vm_run_state)
    
    return



#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def get_machine_expected_inputs(vm_run_state, program):

    r = []

    for thread in vm_run_state['threads']:

        if thread['state'] != THREAD_WAIT_IO:
            continue

        pc = thread['pc']
        
        opcode, params = program[pc]
        
        if opcode != OP_CODE_INPUT:
            continue

        input_match = params        
        
        r.append(input_match)
    
    return list(set(r))

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __name__ == "__main__":

    import sys
    import unittest

    class BaseTests(unittest.TestCase):

        def test_0(self): 

            program = []

            vm = VM_STATE()
            vm_init(vm, program)
            
            vm_run(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )

        def test_1_pass(self): 

            program = [
                PASS(),
            ]

            vm = VM_STATE()
            vm_init(vm, program)
            
            vm_run(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )

        def test_2_jump(self): 

            program = [
                PASS(),       # 0
                JUMP(3),      # 1
                PASS(),       # 2
                PASS(),       # 3
            ]

            vm = VM_STATE()
            vm_init(vm, program)
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['_stats']['op_count'] == 3)

        def test_2_jump2(self): 

            program = [
                JUMP(2),      # 1
                PASS(),       # 0
            ]
            
            vm = VM_STATE()

            with self.assertRaises(VMException):
                vm_init(vm, program)
                vm_run_all_threads(vm, program)
            
            self.assertFalse( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['_stats']['op_count'] == 1)


        def test_3_split(self): 

            program = [
                FORK([3,6]),   # 0
                PASS()   ,     # 1   Thread 0 (main)
                JUMP(10) ,     # 2

                PASS()   ,     # 3   thread 1
                PASS()   ,     # 4
                JUMP(10) ,     # 5   

                PASS()   ,     # 6   thread 2
                PASS()   ,     # 7
                PASS()   ,     # 8
                JUMP(10) ,     # 9

                PASS()   ,     # 10  END
            ]

            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( len(vm['threads']) == 3 )
            self.assertTrue( vm['threads'][0]['_stats']['op_count'] == 4 )
            self.assertTrue( vm['threads'][1]['_stats']['op_count'] == 5 )
            self.assertTrue( vm['threads'][2]['_stats']['op_count'] == 6 )




        def test_4_timer(self): 

            program = [
                SETTIMER(666),  # 1
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)
                
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['timer_clock'] == 666)

        def test_5_input_match(self): 

            program = [
                INPUT('a'),  # 1
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_set_input(vm, 'a')
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['r0'] == 0 )

        def test_5_input_not_match(self): 

            program = [
                INPUT('a'),  # 1
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_set_input(vm, 'b')
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertFalse( vm['threads'][0]['r0'] == 0 )


        def test_6_1_pushstack(self): 

            program = [
                STACKPUSHV(666),  # 1
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['stack'] == [666,] )

        def test_6_2_stackpop(self): 

            program = [
                STACKPUSHV(1),  # 1
                STACKPUSHV(2),  # 1
                STACKPUSHV(3),  # 1
                STACKPUSHV(4),  # 1
                STACKPOP(1),
                STACKPOP(1),
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['stack'] == [1,2] )

        def test_6_3_stackset(self): 

            program = [
                STACKPUSHV(1),  # 1
                STACKPUSHV(2),  # 1
                STACKPUSHV(3),  # 1
                STACKPUSHV(4),  # 1
                STACKSETV(0, 11),
                STACKSETV(1, 12),
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['stack'] == [11,12,3,4] )

        def test_6_4_stackget(self): 

            program = [
                STACKPUSHV('a'),  # 0
                STACKPUSHV('b'),  # 1
                STACKPUSHV('c'),  # 2
                STACKPUSHV('d'),  # 3
                STACKGET(2),
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]["r0"] == 'c' )

        def test_6_5_stackget(self): 

            program = [
                STACKPUSHV('a'),  # 0
                STACKPUSHV('b'),  # 1
                STACKPUSHV('c'),  # 2
                STACKPUSHV('d'),  # 3
                STACKGET(-1),
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]["r0"] == 'd' )

    unittest.main()
