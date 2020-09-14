
import time
import copy
import types

from .opcodes import *
from .utils import OPCODE_NAME

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __debug__:
   def DEBUG(*args):
       print(' '.join([str(a) for a in args]))
   
   def DEBUG_SLEEP():
       #time.sleep(0.05)
       pass
else:    
   def DEBUG(*args):
       pass 
   
   def DEBUG_SLEEP():
       pass

#----------------------------------------------------------------------#
# Exceptions                                                           #
#----------------------------------------------------------------------#

class VMException(Exception):
    pass

class VMInvalidOperation(VMException):
    pass

class WaitForInputException(VMException):
    pass

class StopException(VMException):
    pass

#----------------------------------------------------------------------#
# Virtual Machine state                                                #
#----------------------------------------------------------------------#

def vm_create(initial_context=None, clock=None):

    vm_state = {
        'threads' : {},
        'threadid': 0,                   # Last assigned thread id
    }
    
    _vm_init( vm_state, initial_context=initial_context, clock=clock )
    
    return vm_state

#----------------------------------------------------------------------#
# Threads                                                              #
#----------------------------------------------------------------------#

_tid = 0

THREAD_TERMINATED = "TERM"
THREAD_RUNNING    = "RUN"
THREAD_WAIT_IO    = "I/O"

def vm_thread_create(pc=0, clock=0, context=None):

    if context is not None:
        context = copy.deepcopy(context)
    else:
        context = {}

    global _tid

    thread = {
        'id'             : None,             # internal ID
        
        'respawn'        : True,             # Start new thread when this ends

        'context'        : context,          # Global vars 

        #
        # Execution state
        #        
        'state'          : THREAD_RUNNING,   # Thread state
        'clock'          : clock,            # Current execution clock
        'pc'             : pc,               # Program counter
        'regstack'       : [],               # Registers

        #
        # I/O
        #
        'output'         : [],               # Output data
        'input'          : [],               # Input to consume 
        #'input_timer'    : None,            # 
    }
    _tid += 1

    return thread

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def _vm_init( vm_run_state, initial_context=None, clock=None ):

    # Create the first main thread
    main_thread = vm_thread_create(clock=clock, context=initial_context)
    
    vm_add_thread(vm_run_state, main_thread)
    
    return

def vm_add_thread(vm_run_state, thread):

    tid = vm_run_state['threadid']
    vm_run_state['threadid'] += 1

    thread['id'] = tid

    vm_run_state['threads'][tid] = thread

def vm_get_thread(vm_run_state, tid):

    try:
        return vm_run_state['threads'][tid]
    except KeyError as e:
        raise Exception("Invalid thread id %s" % (tid))

#----------------------------------------------------------------------#

def vm_is_finished( vm_run_state ):

    n = len(vm_run_state['threads'])

    count = 0
    for t in vm_run_state['threads'].values():
        if t['state'] == THREAD_TERMINATED:
            count +=1
    
    #print(__file__, count, n)
    
    if count == n:
        return True
    else:
        return False

def vm_is_waiting_input( vm_run_state ):

    t = 0
    w = 0
    n = 0
    for thread in vm_run_state['threads'].values():
        n += 1
        if thread['state'] == THREAD_WAIT_IO:
            w += 1
        elif thread['state'] == THREAD_TERMINATED:
            t += 1

    return w > 0 and (n - t) == w

#----------------------------------------------------------------------#
# CLOCK                                                                #
#----------------------------------------------------------------------#

def vm_set_clock( vm_run_state, clock=None ):

    clock = clock if clock is not None else time.time()

    for t in vm_run_state['threads'].values():
        t['clock'] = clock

#----------------------------------------------------------------------#
# IO                                                                   #
#----------------------------------------------------------------------#

def vm_get_threads_output( vm_run_state):

    outputs = []
    
    for tid, t in vm_run_state['threads'].items():

        if not t['output']:
            continue
            
        out_data = t['output']
        t['output'] = []

        outputs.append( (tid, out_data) )
    
    return outputs


def vm_set_input(vm_run_state, input_data, thread_id=None):

    if thread_id is not None:

        t = vm_run_state['threads'][thread_id]
        vm_thread_set_input(t, input_data)
        
    else:

        for tid, t in vm_run_state['threads'].items():
            vm_thread_set_input(t, input_data)

            
def vm_thread_set_input( thread, input_data):

    if thread['state'] == THREAD_TERMINATED:
        raise Exception("Thread %s not valid for input" % (thread['id']))
        
    thread['input'].append( input_data )
    
    thread['state'] = THREAD_RUNNING


#def vm_set_input( vm_run_state, thread_id, input_data):
#
#    for t in vm_run_state['threads']:
#
#        if t['id'] == thread_id:
#
#            if t['state'] == THREAD_TERMINATED:
#                break
#            
#            t['input'] = [ input_data ]


#def vm_write_output(thread, data):
#    thread['output'] += data


#def vm_read_input(thread, timeout=None):
#
#    if not thread['input']:
#        vm_thread_set_timer(thread, timeout)
#           
#        raise WaitForInputException(timeout)
#    
#    return thread['input'].pop()

#----------------------------------------------------------------------#
# THREAD TIMER                                                         #
#----------------------------------------------------------------------#

#def vm_thread_set_timer(thread, seconds):
#    if seconds is None:
#        thread['input_timer'] = None
#    else:
#        thread['input_timer'] = thread['clock'] + seconds

#----------------------------------------------------------------------#
# THREAD EXECUTIONS                                                    #
#----------------------------------------------------------------------#

def vm_run_all_threads(vm_run_state, program):

    for t in  vm_run_state['threads'].values():

        if t['state'] == THREAD_TERMINATED: 
            continue

        if t['state'] == THREAD_WAIT_IO:
            if t['input']:
                t['state'] = THREAD_RUNNING

        #if t['input_timer'] is not None:
        #    if t['input_timer'] <= t['clock']:
        #        DEBUG("TIMER EXPIRED!")
        #        t['regstack'] = [0]
        #        t['state'] = THREAD_TERMINATED 

    threads_to_execute = [ t for t in  vm_run_state['threads'].values() if t['state'] == THREAD_RUNNING ]

    while threads_to_execute:

        DEBUG("TURN")
        
        for thread in threads_to_execute:
            vm_run_thread(vm_run_state, program, thread)
            DEBUG_SLEEP()

        # Execute only running threads
        threads_to_execute = [ t for t in vm_run_state['threads'].values() if t['state'] == THREAD_RUNNING ]

    return 


def vm_thread_exit( thread, code ):

    thread['status'  ] = THREAD_TERMINATED
    thread['regstack'] = [code]


def vm_run_thread(vm_run_state, program, thread, run_loop_count=None):

    DEBUG("\tTHREAD: id=%(id)s  state=%(state)s  pc=%(pc)s  regstack=%(regstack)s  input=%(input)s" % thread)

    thread_context  = thread['context']
    thread_state    = thread['state']
    pc              = thread['pc']
    thread_regstack = thread['regstack']
    
    run_loop_count = 0
    
    while thread_state: 
        
            if run_loop_count is not None:
                if run_loop_count > 2:
                    break
                run_loop_count += 1


            DEBUG_SLEEP()

            if pc >= len(program):
                thread_state = THREAD_TERMINATED
                break
                
            opcode, params = program[pc]

            DEBUG( "\t", "\t pc=%s/%s -> opcode=%s params=%s regstack=%s" % (pc, len(program), OPCODE_NAME[opcode], params, thread_regstack) )

            pc += 1

            if opcode == OP_CODE_PASS:

                pass

            elif opcode == OP_CODE_STOP:

                r = params

                thread_regstack = [r]
                thread_state = THREAD_TERMINATED

            elif opcode == OP_CODE_SETRESPAWN:

                r = params
                thread['respawn'] = r

            elif opcode == OP_CODE_REGFLUSH:

                n = params

                if n:
                    thread_regstack = thread_regstack[:-n]
                else:
                    thread_regstack = []
                #DEBUG("\t\t\t", "stack", thread_regstack)

            elif opcode == OP_CODE_SET:

                val = params

                thread_regstack.append(val)

            elif opcode == OP_CODE_CREATETUPLE:

                size = params
                
                if size > 0:

                    elements = thread_regstack[-size:]
                
                    thread_regstack = thread_regstack[:-size]
                    
                    args_tuple = tuple(elements)
                else:
                    args_tuple = tuple()
                         
                thread_regstack.append( args_tuple )

            elif opcode == OP_CODE_CREATEDICT:
                
                v = {}
                thread_regstack.append( v  )

            elif opcode == OP_CODE_DICTSETK:
                
                v = thread_regstack.pop()
                k = thread_regstack.pop()
                d = thread_regstack.pop()
                
                d[k] = v
                
                thread_regstack.append( d )

            elif opcode == OP_CODE_REGSUM:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1+v2 )
                
            elif opcode == OP_CODE_REGSUB:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 - v2 )
                
            elif opcode == OP_CODE_REGMUL:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 * v2 )

            elif opcode == OP_CODE_REGDIV:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 / v2 )
                
            elif opcode == OP_CODE_REGMOD:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 % v2 )

            elif opcode == OP_CODE_REGNEG:

                v = thread_regstack.pop()
                
                thread_regstack.append( -v )

            elif opcode == OP_CODE_REGBITONE:

                v = thread_regstack.pop()
                
                thread_regstack.append( ~v )

            elif opcode == OP_CODE_REGNOT:

                v = thread_regstack.pop()
                
                thread_regstack.append( not (v) )

            elif opcode == OP_CODE_REGPOW:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()
                
                v = v1 ** v2

                thread_regstack.append( v )

            elif opcode == OP_CODE_REGLSHIFT:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 << v2 )

            elif opcode == OP_CODE_REGRSHIFT:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 >> v2 )

            elif opcode == OP_CODE_REGBITAND:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 & v2 )

            elif opcode == OP_CODE_REGBITXOR:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 ^ v2 )

            elif opcode == OP_CODE_REGBITOR:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                thread_regstack.append( v1 | v2 )

            elif opcode == OP_CODE_REGEQ:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()
                
                thread_regstack.append(v1 == v2)

            elif opcode == OP_CODE_REGNEQ:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()
                
                thread_regstack.append( v1 != v2 )

            elif opcode == OP_CODE_REGLT:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()
                
                thread_regstack.append( v1 < v2 )

            elif opcode == OP_CODE_REGLTE:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()
                
                thread_regstack.append( v1 <= v2 )

            elif opcode == OP_CODE_REGGT:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()
                
                thread_regstack.append( v1 > v2 )

            elif opcode == OP_CODE_REGGTE:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()
                
                thread_regstack.append( v1 >= v2 )

            elif opcode == OP_CODE_LOADSYM:

                symbol = thread_regstack.pop()
                
                v = thread_context[ symbol ]
                
                thread_regstack.append( v )

            elif opcode == OP_CODE_LOADSYMLV:

                symbol = thread_regstack.pop()
                
                v = (None, symbol)
                
                thread_regstack.append( v )

            elif opcode == OP_CODE_STORESYM:

                val    = thread_regstack.pop()
                symbol = thread_regstack.pop()
                
                context1, symbol1 = symbol
                if context1 is None:
                    context1 = thread_context
                
                context1[symbol1] = val
                
                thread_regstack.append( val )

            elif opcode == OP_CODE_GETATTR:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()

                val = v1[v2]
                    
                thread_regstack.append( val )

            elif opcode == OP_CODE_GETATTRLV:

                v2 = thread_regstack.pop()
                v1 = thread_regstack.pop()
                
                context1, sym1 = v1
                sym2 = v2
                
                if context1 is None:
                    context1 = thread_context

                v1 = context1[sym1]
                
                val = ( v1, sym2 )
                    
                thread_regstack.append( val )


            elif opcode == OP_CODE_JUMP:

                pc2 = params

                if pc2 >= len(program):
                    #thread['_stats']['op_count'] += 1
                    raise VMInvalidOperation("Invalid JUMP to %s (pc:%s)" % (pc2, pc))
                
                pc = pc2

            elif opcode == OP_CODE_JUMPR:

                rel_pos = params
                
                pc += rel_pos

            elif opcode == OP_CODE_IFTRUE:

                addr = params

                v = thread_regstack[-1]
                
                if v:
                    pc += addr

            elif opcode == OP_CODE_IFFALSE:
            
                addr = params
            
                v = thread_regstack[-1]
                
                if not v:
                    pc += addr

            elif opcode == OP_CODE_FORK:

                addresses = params

                for jump in addresses:

                    thread2 = vm_thread_create(jump)

                    thread2['state'         ] = THREAD_RUNNING
                    thread2['pc'            ] = jump
                    
                    thread2['clock'         ] = thread['clock']
                    thread2['regstack'         ] = copy.copy(thread_regstack)
                    
                    thread2['context'       ] = copy.copy(thread['context'])
                    
                    #thread2['_stats'        ] = copy.copy(thread['_stats'])
                    #thread2['_stats']['op_count'] += 1
                    
                    t2_input = None
                    if thread['input'] is not None:
                        t2_input = [ data for data in thread['input'] ]
                    thread2['input'] = t2_input
                    
                    #vm_run_state['threads'].append( thread2 )
                    vm_add_thread( vm_run_state, thread2 )

            #
            # CALL
            #
            elif opcode == OP_CODE_CALL:

                n_args, n_kwargs = params
                
                fun_callable    = thread_regstack.pop()
                
                stacked_params = thread_regstack[-(n_args + n_kwargs): ]
                
                del thread_regstack[-(n_args + n_kwargs): ]
                
                args   =      stacked_params[          : n_args ]  if n_args   else list()
                kwargs = dict(stacked_params[ -n_kwargs:        ]) if n_kwargs else dict()
                
                try:
                    DEBUG( "CALLING %s args=%s:%r  kargs=%s:%r" % (fun_callable, n_args, args, n_kwargs, kwargs))
                    
                    ret = fun_callable(thread, *args, **kwargs)
                    
                    thread_regstack.append(ret)
                    
                except StopException as se:
                    break

            #
            # CALL_SYM
            #
            elif opcode == OP_CODE_CALL_SYM:

                n_args, n_kwargs = params
                
                fun_sym    = thread_regstack.pop()
                
                stacked_params = thread_regstack[-(n_args + n_kwargs): ]
                
                del thread_regstack[-(n_args + n_kwargs): ]
                
                fun_callable = thread_context[ fun_sym ]
                args   =      stacked_params[          : n_args ]  if n_args   else list()
                kwargs = dict(stacked_params[ -n_kwargs:        ]) if n_kwargs else dict()
                
                try:
                    DEBUG( "CALLING %s args=%s:%r  kargs=%s:%r" % (fun_callable, n_args, args, n_kwargs, kwargs))
                    
                    ret = fun_callable(thread, *args, **kwargs)
                    
                    thread_regstack.append(ret)
                    
                except StopException as se:
                    break

            elif opcode == OP_CODE_CALL_NATIVE:

                fun_callable, n_args, n_kwargs = params
                
                stacked_params = thread_regstack[-(n_args + n_kwargs): ]
                
                del thread_regstack[-(n_args + n_kwargs): ]
                
                args   =      stacked_params[          : n_args ]  if n_args   else list()
                kwargs = dict(stacked_params[ -n_kwargs:        ]) if n_kwargs else dict()
                
                try:
                    DEBUG( "CALLING %s args=%s:%r  kargs=%s:%r" % (fun_callable, n_args, args, n_kwargs, kwargs))
                    
                    ret = fun_callable(thread, *args, **kwargs)
                    
                    thread_regstack.append(ret)
                    
                except StopException as se:
                    break








            elif opcode == OP_CODE_FUNCALL:

                DEBUG( "FUNCALL", thread_regstack)


                fun_obj = params
                
                fun_params = thread_regstack.pop()
                
                DEBUG( "    FUN   ", fun_obj)
                DEBUG( "    PARAMS", fun_params)
                
                try:
                    ret = fun_obj(thread, *list(fun_params))
                    
                    thread_regstack.append(ret)
                
                except WaitForInputException as we:

                    DEBUG( "WATING IO")

                    thread_regstack.append(params)
                    thread_regstack.append(fun_obj)

                    pc -= 1

                    thread_state = THREAD_WAIT_IO
                    break
                    
                except StopException as se:
                    break


            #
            # I/O
            #
            elif opcode == OP_CODE_OUTPUT:

                data = thread_regstack.pop()
                thread['output'].append(data)

            elif opcode == OP_CODE_INPUT:

                # Input? Try to consume it.
                if not thread['input']:
                    pc -= 1
                    thread_state = THREAD_WAIT_IO
                    
                    break

                data = thread['input'].pop(0)
                
                thread_regstack.append(data)
                
                #input_match = thread_regstack.pop()
                #    
                #    input_to_process = thread['input'][0]
                #    
                #    DEBUG(  "\t","\t","INPUT:", input_to_process)
                #    DEBUG(  "\t","\t","MATCH:", input_match)
		#
                #    if input_to_process == input_match:
		#
                #        thread['input'].pop(0)
                #        
                #        thread_state = THREAD_RUNNING
		#
                #    else:
                #        if not terminate_on_mismatch:
                #            
                #            thread_regstack.append(input_match)
                #            pc -= 1
                #            
                #            thread_state = THREAD_WAIT_IO
                #            break
                #            
                #        else:
                #            if thread['input_timer'] is not None:
                #                thread_regstack.append(input_match)
                #                
                #                pc -= 1
                #                thread_state = THREAD_WAIT_IO
                #                
                #                break
                #            else:
                #                thread_regstack.append(0)
                #                thread_state = THREAD_TERMINATED
                #                break


            #elif opcode == OP_CODE_SETTIMER:
	    #
            #    seconds = params
            #    
            #    thread['timer_clock'] = thread['clock'] + seconds
	    #
            #    else:
            #        pc -= 1
            #        thread_state = THREAD_WAIT_IO
	    #
            #        break
            
            else:
                raise VMException("Invalid opcode: %s (pc:%s)" % (opcode, pc))

            #thread['_stats']['op_count'] += 1

    if thread_state == THREAD_TERMINATED:
        DEBUG("THREAD TERMINATED")

    thread['pc'      ] = pc
    thread['state'   ] = thread_state
    thread['regstack'] = thread_regstack 
    thread['context' ] = thread_context

    return

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def vm_free_terminated_threads(vm_run_state):

    vm_run_state['threads'] = dict([ (tid, t) for tid, t in vm_run_state['threads'].items() if t['state'] != THREAD_TERMINATED ])

    return

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def get_machine_expected_inputs(vm_run_state, program):

    r = []

    for thread in vm_run_state['threads'].values():

        if thread['state'] != THREAD_WAIT_IO:
            continue

        pc = thread['pc']
        
        opcode, params = program[pc]
        
        if opcode != OP_CODE_INPUT:
            continue

        input_matcher = params        
        
        r.append(input_matcher)
    
    return list(set(r))

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#




















                




            #elif opcode == OP_CODE_ARRAY:
	    #
            #    pc += 1
	    #
            #    n = params
	    #
            #    array_elements = thread_regstack[-n:]
	    #
            #    thread_regstack = thread_regstack[:-n]
	    #
            #    thread_regstack.append( array_elements )
            #                

	    #





            #elif opcode == OP_CODE_EQUAL:
	    #
            #    pc += 1
            #    
            #    val, addr = params
            #    
            #    if thread['r0'] == val:
            #        thread_pc = addr
            #
            #elif opcode == OP_CODE_LT:
            #
            #    pc += 1
            #
            #    val, addr = params
            #
            #    if thread['r0'] < val:
            #        thread_pc = addr
                    








            #elif opcode == OP_CODE_STACKPUSH:
	    #
            #    pc += 1
	    #
            #    value = thread['r0']
	    #
            #    thread['stack'].append(value)
	    #
            #elif opcode == OP_CODE_STACKPOP:
	    #
            #    pc += 1
	    #
            #    n = params
	    #
            #    stack_len = len(thread['stack'])
            #    thread['stack'] = thread['stack'][:stack_len-n]
	    #
            #elif opcode == OP_CODE_STACKSET:
	    #
            #    pc += 1
	    #
            #    pos = params
            #    
            #    value = thread['r0']
	    #
            #    if pos >= 0: pos = thread['sp'] + pos         
            #    else       : pos = len(thread['stack']) + pos 
	    #
            #    thread['stack'][pos] = value
	    #
            #elif opcode == OP_CODE_STACKGET:
	    #
            #    pc += 1
	    #
            #    pos = params
	    #
            #    if pos >= 0: pos = thread['sp'] + pos 
            #    else       : pos = len(thread['stack']) + pos 
	    #
            #    value = thread['stack'][ pos ]
	    #
            #    thread['r0'] = value
	    #
            #elif opcode == OP_CODE_STACKPUSHV:
	    #
            #    pc += 1
	    #
            #    value = params
	    #
            #    thread['stack'].append(value)
	    #
            #elif opcode == OP_CODE_STACKSETV:
	    #
            #    pc += 1
	    #
            #    pos, value = params
	    #
            #    if pos >= 0: pos = thread['sp'] + pos         
            #    else       : pos = len(thread['stack']) + pos 
	    #
            #    thread['stack'][pos] = value

