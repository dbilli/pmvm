
"""

Virtual Machine opcodes:

   INPUT [match]                  Compare [match] with the current input element.
                                  If [match] does not match with input, the current thread blocks.
   
   MATCH flag
                                  The VM's state "matched" to flag
  
   SPLIT <pos1>, <pos2>, ....
                                  Create N execution threads, each thread starts from pos1, pos2, ...
   
   JUMP <pos>
                                  Jumps the current threads to the position <pos>
   
   EQUAL <n> <pos>                
                                  If register r0 is equal to <n> jumps to position <pos>
   
   SET <n>
                                  Set register r0 to <n>
   
   ADD <n>
                                  Add <n> to register r0.

"""

import time

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def DEBUG(*args):
    print(' '.join([str(a) for a in args]))
    pass 

def DEBUG_SLEEP():
    #time.sleep(1)
    pass

#----------------------------------------------------------------------#
# OPCODES                                                              #
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

OP_CODE_MATCH = 'MATCH'

def MATCH(flag=True):
    return (OP_CODE_MATCH, flag)

#----------------------------------------------------------------------#

OP_CODE_SPLIT = 'SPLIT'

def SPLIT(addresses):
    return ( OP_CODE_SPLIT, addresses )

#----------------------------------------------------------------------#

OP_CODE_JUMP  = 'JUMP'

def JUMP(addr):
    return ( OP_CODE_JUMP , addr )

#----------------------------------------------------------------------#

OP_CODE_EQUAL  = 'EQUAL'

def EQUAL(val, addr):
    return ( OP_CODE_EQUAL , (val, addr) )

#----------------------------------------------------------------------#

OP_CODE_SET  = 'SET'

def SET(val):
    return ( OP_CODE_SET, val)

#----------------------------------------------------------------------#

OP_CODE_ADD  = 'ADD'

def ADD(val):
    return ( OP_CODE_ADD, val)


#----------------------------------------------------------------------#
# Virtual Machine state                                                #
#----------------------------------------------------------------------#

_tid = 0

THREAD_TERMINATED = 0
THREAD_RUNNING    = 1
THREAD_STOPPED    = 2

def VM_THREAD(program_counter=0):
    
    global _tid
    
    thread = {
        'id'             : _tid,             # internal ID
        'program_counter': program_counter,  # Program counter
        'r0'             : 0,                # Register r0

        'state'          : THREAD_RUNNING,            # The thread was stopped before consuming the input.

        'input_consumed' : False,
    }
    _tid += 1

    return thread

def VM_STATE():

    state = {
        'threads'       : {},                   # Current threads of execution
        
        
        'matched'       : False,                # The match
        'input_group'   : [],                   # Sequence of "inputs" that "matched" the program.
    }

    ## Create the first main thread
    #main_thread = VM_THREAD()
    #state['threads'][ main_thread['id'] ] = main_thread
    return state

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def vm_init( vm_run_state, program ):

    # Create the first main thread
    main_thread = VM_THREAD()
    vm_run_state['threads'][ main_thread['id'] ] = main_thread
    
    return vm_run( vm_run_state, program)
    
def vm_is_finished( vm_run_state ):

    return len(vm_run_state['threads']) == 0

def vm_run( vm_run_state, program, input_to_process=None):

    #vm_run_state['input_consumed'] = False

    DEBUG("-----------------")
    DEBUG("RUN", input_to_process)

    threads_to_execute = list(vm_run_state['threads'].values())
    for t in threads_to_execute:
        t['state'       ] = THREAD_RUNNING
        t['input_consumed'] = False

        
    while threads_to_execute:

        DEBUG("TURN")
        for t in threads_to_execute:
            DEBUG("\t THREAD:", t)
        DEBUG( "" )
        
        for thread in threads_to_execute:
            vm_run_thread(vm_run_state, program, thread, input_to_process)
            DEBUG_SLEEP()
        
        vm_run_state['threads'] = dict([(t['id'],t) for t in vm_run_state['threads'].values() if t['state'] != THREAD_TERMINATED])

        threads_to_execute = [ t for t in vm_run_state['threads'].values() if t['state'] == THREAD_RUNNING]

    return vm_run_state['matched']

       #vm_run_threads(vm_run_state, program, input_to_process, threads_to_execute)
 #def vm_run_threads(vm_run_state, program, input_to_process, executing_threads):
#
#        threads_to_execute = []
#
#        for thread in executing_threads:


def vm_run_thread(vm_run_state, program, thread, input_to_process):
    
    DEBUG("\t", "EXECUTING THREAD", thread['id'])

    while thread['state'] == THREAD_RUNNING:


            pc = thread['program_counter']
            if pc >= len(program):
                DEBUG( "\t", "\t", "REACHED END OF PROGRAM" )
                #del vm_run_state['threads'][thread['id']]
                thread['state'] = THREAD_TERMINATED
                continue
                

            opcode, params = program[pc]
            DEBUG( "\t", "\t pc=%s/%s -> opcode=%s params=%s" % (pc, len(program), opcode, params) )
            
            if input_to_process is None:
                if opcode in [OP_CODE_INPUT, OP_CODE_MATCH]:
                    thread['state'] = THREAD_STOPPED
                    DEBUG( "\t", "\t", "\t", "STOPPED FOR FIRST INPUT" )
                    break

            if opcode == OP_CODE_MATCH:

                flag = params

                vm_run_state['matched'] = flag

                pc += 1
                thread['program_counter'] = pc


            # if the this thread reached a OP_CODE_INPUT
            # and the current input was already consumed by other threads, stop the
            # current thread and exit.
            elif opcode == OP_CODE_INPUT:

                if thread['input_consumed']:
                    DEBUG( "\t", "\t", "\t", "STOPPED" )
                    thread['state'] = THREAD_STOPPED
                    continue


                input_match = params
                
                DEBUG( "\t", "\t", "COMPARE", input_to_process, input_match )
                
                if input_to_process == input_match:

                    thread['input_consumed'] = True
                    
                    vm_run_state['input_group'].append( input_match )

                    DEBUG( "\t", "\t", "\t", "CONSUMED" )
                        
                    #thread['consumed'] = True
                    
                    pc += 1
                    thread['program_counter'] = pc
                    
                else:
                    thread['state'] = THREAD_TERMINATED
                    DEBUG( "\t", "\t", "\t", "NOT MACHED. EXIT!" )
                    del vm_run_state['threads'][thread['id']]
                    break
                    


                #del vm_run_state['threads'][thread['id']]
                #thread = None

            elif opcode == OP_CODE_JUMP:

                pc = params

                thread['program_counter'] = pc

            elif opcode == OP_CODE_SPLIT:

                addresses = params

                thread['program_counter'] = addresses[0]

                for jump in addresses[1:]:

                    thread2 = VM_THREAD(jump)
                    thread2['state'] = THREAD_RUNNING
                    thread2['r0'] = thread['r0']
                    thread2['input_consumed'] = thread['input_consumed']
                    
                    DEBUG( "\t", "\t", "\t", "NEW THREAD", thread2 )
                    vm_run_state['threads'][thread2['id']] = thread2

            elif opcode == OP_CODE_SET:

                val = params

                thread['r0'] = val

                pc += 1
                thread['program_counter'] = pc

            elif opcode == OP_CODE_ADD:

                val = params

                thread['r0'] += val

                pc += 1
                thread['program_counter'] = pc

            elif opcode == OP_CODE_EQUAL:

                val, addr = params

                if thread['r0'] == val:
                    thread['program_counter'] = addr
                else:
                    pc += 1
                    thread['program_counter'] = pc

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def get_machine_expected_inputs(vm_run_state, program):

    r = []

    for thread in vm_run_state['threads'].values():

        #if not thread['stopped']:
        #    continue

        pc = thread['program_counter']
        
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

    #import unittest
    #
    #class TestStringMethods(unittest.TestCase):
    #
    #    def test_upper(self):
    #        self.assertEqual('foo'.upper(), 'FOO')
    #
    #    def test_isupper(self):
    #        self.assertTrue('FOO'.isupper())
    #        self.assertFalse('Foo'.isupper())
    #
    #    def test_split(self):
    #        s = 'hello world'
    #        self.assertEqual(s.split(), ['hello', 'world'])
    #        # check that s.split fails when the separator is not a string
    #        with self.assertRaises(TypeError):
    #            s.split(2)
    #            
    
    #unittest.main()


    #
    # MATCH
    #
    print(("*" * 120 + "\n") * 4)

    program = [
        MATCH(),
    ]
    print(program)
    
    state = VM_STATE()
    vm_init(state, program)
    vm_run(state, program, 'a')
    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])
    
    assert (vm_is_finished(state) == True )
    assert (state['matched']      == True )
    
    #
    # NOMATCH
    #
    print(("*" * 120 + "\n") * 4)
    program = [
        MATCH(False),
    ]
    print(program)

    state = VM_STATE()
    vm_init(state, program)
    vm_run(state, program, 'c')
    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])
    
    assert (vm_is_finished(state) == True )
    assert (state['matched']      == False )

    #
    # a  <EOF>
    #
    print(("*" * 120 + "\n") * 4)
    
    program = [
        INPUT('c'),
        
        MATCH(),
    ]
    print(program)


    state = VM_STATE()
    vm_init(state, program)
    vm_run(state, program, 'a')
    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])

    assert (vm_is_finished(state) == True )
    assert (state['matched']      == False )
    
    print( (">" * 120 + "\n") * 2 )

    print(program)

    state = VM_STATE()
    vm_init(state, program)
    vm_run(state, program, 'c')
    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])
    
    assert (vm_is_finished(state) == True )
    assert (state['matched']      == True )



    #
    # a b c <EOF>
    #
    print(("*" * 120 + "\n") * 4)
    
    program = [
        INPUT('a'),
        INPUT('b'),
        INPUT('c'),
        
        MATCH(),
    ]
    print(program)

    state = VM_STATE()
    vm_init(state, program)
    
    for i in 'abc':
        vm_run(state, program, i)
        
    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])

    assert (vm_is_finished(state) == True )
    assert (state['matched']      == True )
    
    print( (">" * 120 + "\n") * 2 )

    state = VM_STATE()
    vm_init(state, program)
    
    for i in 'abd':
        vm_run(state, program, i)
        
    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])

    assert (vm_is_finished(state) == True  )
    assert (state['matched']      == False )

    #
    # (a | b | c) <EOF>
    #
    print(("*" * 120 + "\n") * 4)
    
    program = [
        SPLIT([1,3,5]),      # 0
        INPUT('a'),          # 1
            JUMP(7),         # 2
        INPUT('b'),          # 3
            JUMP(7),         # 4
        INPUT('c'),          # 5
            JUMP(7),         # 6
            
        MATCH(),             # 7
    ]
    
    print(program)

    state = VM_STATE()
    vm_init(state, program)
    vm_run(state, program, 'c')
    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])

    assert (vm_is_finished(state) == True )
    assert (state['matched']      == True )


    #
    # a? <EOF>
    #
    print(("*" * 120 + "\n") * 4)

    program = [
        SPLIT([1,2]),       # 0
        INPUT('a'),         # 1
        
        MATCH(),            # 2
    ]
    
    print(program)

    state = VM_STATE()
    vm_init(state, program)
    vm_run(state, program, 'c')
    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])
    
    assert (vm_is_finished(state) == True )
    assert (state['matched']      == True )


    #
    # A+ B <EOF>
    #
    print(("*" * 120 + "\n") * 4)

    program = [
        # A
        INPUT('a'),          # 0
        SPLIT( [0,2] ),      # 1
        # B                  
        INPUT('b'),          # 2
        
        MATCH(),             # 3
    ]

    print(program)

    state = VM_STATE()
    vm_init(state, program)
    for i in 'ab':
        vm_run(state, program, i)

    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])
    
    assert (vm_is_finished(state) == True )
    assert (state['matched']      == True )



    print( (">" * 120 + "\n") * 2 )
    print(program)

    state = VM_STATE()
    vm_init(state, program)
    for i in 'aaaaaac':
        vm_run(state, program, i)

    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])
    
    assert (vm_is_finished(state) == True )
    assert (state['matched']      == False )



    print( (">" * 120 + "\n") * 2 )
    print(program)

    state = VM_STATE()
    vm_init(state, program)
    for i in 'aaaaaab':
        vm_run(state, program, i)

    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])
    
    assert (vm_is_finished(state) == True )
    assert (state['matched']      == True )



    print( (">" * 120 + "\n") * 2 )
    print(program)

    state = VM_STATE()
    vm_init(state, program)
    for i in 'bc':
        vm_run(state, program, i)

    print("")
    print("VM        :", state)
    print("Terminated:", vm_is_finished(state))
    print("Matched   :", state['matched'])
    
    assert (vm_is_finished(state) == True )
    assert (state['matched']      == False )



    """

    #
    # A*
    #
    program = [
        SPLIT([1,3]),        # 0
        # A                  
        INPUT('a'),          # 1
        JUMP(0),             # 2
        # B                  
        MATCH(),             # 3
    ]

    #
    # a+
    #
    program = [ 
        INPUT('a'),          # 0
        SPLIT([0,2]),        # 1
        MATCH(),             # 2
    ]                            

    state = VM_STATE()
    matched = run_machine(state, program, 'a')
    matched = run_machine(state, program, 'a')
    matched = run_machine(state, program, 'c')
    matched = run_machine(state, program, 'a')
    matched = run_machine(state, program, 'b')
    matched = run_machine(state, program, 'c')

    print("----------------")
    print(matched)	
    """
