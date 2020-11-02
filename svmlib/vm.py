
import time
import copy
import types

from .opcodes import *
from .utils import OPCODE_NAME

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __debug__:

   def _prCyan(prt): print("\033[96m {}\033[00m" .format(prt))

   def DEBUG(*args):
       _prCyan(' '.join([str(a) for a in args]))
   
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

#class WaitForInputException(VMException):
#    pass

class StopException(VMException):
    pass

#----------------------------------------------------------------------#
# Virtual Machine state                                                #
#----------------------------------------------------------------------#

def vm_create(initial_context=None, clock=None):
    
    #
    # Alloc
    #
    vm_state = {
        'threads' : {},
        
        'threadid': 0,                   # Last assigned thread id
    }
    
    #
    # Create the first main thread
    #
    main_thread = vm_thread_create(clock=clock, context=initial_context)
    
    vm_add_thread(vm_state, main_thread)

    return vm_state

#----------------------------------------------------------------------#
# Threads                                                              #
#----------------------------------------------------------------------#

THREAD_NEW        = "NEW"
THREAD_RUNNING    = "RUN"
THREAD_WAIT_IO    = "I/O"
THREAD_TERMINATED = "TERMINATED"

def vm_thread_create(pc=0, clock=0, context=None):

    if context is not None:
        context = copy.deepcopy(context)
    else:
        context = {}

    thread = {
        'id'             : None,             # internal ID
        #
        # Execution state
        #        
        'state'          : THREAD_NEW,       # Thread state
        'clock'          : clock,            # Current execution clock
        'pc'             : pc,               # Program counter
        'regstack'       : [],               # Registers
        #
        # 
        #
        'context'        : context,          # Global vars 
        #
        # I/O
        #
        'output'         : [],               # Output data
        
        'input'          : [],               # Input to consume 
        'input_timeout'  : None,
    }

    return thread

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def vm_add_thread(vm_run_state, thread):

    #
    # Thread id
    #
    tid = vm_run_state['threadid']
    vm_run_state['threadid'] += 1

    thread['id'] = tid


    
    #
    # Add to the VM
    #
    vm_run_state['threads'][tid] = thread

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def vm_is_finished( vm_run_state ):

    n = len(vm_run_state['threads'])

    count = 0
    for t in vm_run_state['threads'].values():
        if t['state'] == THREAD_TERMINATED:
            count +=1
    
    if count == n:
        return True
    else:
        return False

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
            
def vm_thread_set_input( thread, input_data):

    if thread['state'] == THREAD_TERMINATED:
        raise Exception("Thread %s not valid for input" % (thread['id']))
        
    thread['input'].append( input_data )
    
    thread['state'] = THREAD_RUNNING

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

        if t['state'] == THREAD_NEW:
            t['state'] = THREAD_RUNNING

    threads_to_execute = [ t for t in  vm_run_state['threads'].values() if t['state'] == THREAD_RUNNING ]

    while threads_to_execute:

        DEBUG("TURN")
        
        for thread in threads_to_execute:
            vm_run_thread(vm_run_state, program, thread)
            DEBUG_SLEEP()

        # Execute only running threads
        threads_to_execute = [ t for t in vm_run_state['threads'].values() if t['state'] == THREAD_RUNNING ]

    return 


def vm_run_thread(vm_run_state, program, thread, run_loop_count=None):

    DEBUG("\tTHREAD: id=%(id)s  state=%(state)s  pc=%(pc)s  clock=%(clock)s  regstack=%(regstack)s  input=%(input)s" % thread)

    thread_context  = thread['context']
    thread_state    = thread['state']
    pc              = thread['pc']
    thread_regstack = thread['regstack']
    
    loop_count = 0
    
    while thread_state: 
        
            if run_loop_count is not None:
                if loop_count > run_loop_count:
                    break
                loop_count += 1

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

            elif opcode == OP_CODE_REGFLUSH:

                n = params

                if n:
                    thread_regstack = thread_regstack[:-n]
                else:
                    thread_regstack = []

            elif opcode == OP_CODE_SET:

                val = params

                thread_regstack.append(val)

            elif opcode == OP_CODE_FLUSHSET:
 
                n, val = params
    
                if n:
                    thread_regstack = thread_regstack[:-n]
                else:
                    thread_regstack = []
    
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

            #
            # ON CONTEXT
            #
            elif opcode == OP_CODE_CONTEXT_LPUSH:

                symbol, value = params
                
                thread_context.get(symbol, thread_context.setdefault(symbol, [])).append( value )

            elif opcode == OP_CODE_CONTEXT_LPOP:

                symbol = params
                
                thread_context[symbol].pop()

            #
            # JUMPS
            #
            elif opcode == OP_CODE_JUMP:

                pc2 = params

                if pc2 >= len(program):
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

                thread_id = thread['id']
                
                #thread['fork_chain'].append(thread_id)

                addresses = params

                for jump in addresses:

                    thread2 = vm_thread_create(jump)

                    #thread2['parent_id'     ] = thread_id
                    #thread2['fork_chain'    ] = list(thread['fork_chain']) # duplicate

                    thread2['state'         ] = THREAD_RUNNING
                    thread2['pc'            ] = jump
                    
                    thread2['clock'         ] = thread['clock']
                    thread2['regstack'      ] = copy.deepcopy(thread_regstack)
                    
                    thread2['context'       ] = copy.deepcopy(thread['context'])
                    
                    t2_input = None
                    if thread['input'] is not None:
                        t2_input = list( thread['input'] )
                    thread2['input'] = t2_input

                    thread2['input_timeout' ] = thread['input_timeout']
                                        
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








            #elif opcode == OP_CODE_FUNCALL:
	    #
            #    DEBUG( "FUNCALL", thread_regstack)
	    #
	    #
            #    fun_obj = params
            #    
            #    fun_params = thread_regstack.pop()
            #    
            #    DEBUG( "    FUN   ", fun_obj)
            #    DEBUG( "    PARAMS", fun_params)
            #    
            #    try:
            #        ret = fun_obj(thread, *list(fun_params))
            #        
            #        thread_regstack.append(ret)
            #    
            #    except WaitForInputException as we:
	    #
            #        DEBUG( "WATING IO")
	    #
            #        thread_regstack.append(params)
            #        thread_regstack.append(fun_obj)
	    #
            #        pc -= 1
	    #
            #        thread_state = THREAD_WAIT_IO
            #        break
            #        
            #    except StopException as se:
            #        break


            #
            # I/O
            #
            elif opcode == OP_CODE_OUTPUT:

                data = thread_regstack.pop()
                thread['output'].append(data)

            elif opcode == OP_CODE_INPUT:

                # Input? Try to consume it.
                if not thread['input']:

                    if thread['input_timeout'] is not None:
                        if thread['clock'] >= thread['input_timeout']:
                            thread_state = THREAD_TERMINATED
                            break
 
                    pc -= 1
                    thread_state = THREAD_WAIT_IO
                    
                    break

                data = thread['input'].pop(0)
                
                thread_regstack.append(data)

            
            else:
                raise VMException("Invalid opcode: %s (pc:%s)" % (opcode, pc))

    #
    # Update thread state
    #

    thread['pc'      ] = pc
    thread['state'   ] = thread_state
    thread['regstack'] = thread_regstack 
    thread['context' ] = thread_context

    if thread_state == THREAD_TERMINATED:
        DEBUG("THREAD TERMINATED")
        DEBUG('    pc       = %s' % ( thread['pc'      ] ) )
        DEBUG('    state    = %s' % ( thread['state'   ] ) )
        DEBUG('    regstack = %s' % ( thread['regstack'] ) )
        DEBUG('    context  = %s' % ( thread['context' ] ) )
   
    return
