
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
# BASE                                                                 #
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

OP_CODE_PASS = 1 

if __debug__: OP_CODE_PASS = 'PASS'

def PASS(comment=None):
    return (OP_CODE_PASS, comment)

#----------------------------------------------------------------------#

OP_CODE_STOP = 2 
if __debug__: OP_CODE_STOP = 'STOP'

def STOP(r):
    return (OP_CODE_STOP, r)

#----------------------------------------------------------------------#

OP_CODE_SETRESPAWN = 3 
if __debug__: OP_CODE_SETRESPAWN = 'SETRESPAWN'

def SETRESPAWN(b):
    return (OP_CODE_SETRESPAWN, b)

#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
# REGISTRY                                                             #
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

OP_CODE_REGFLUSH = 100
if __debug__: OP_CODE_REGFLUSH = 'REGFLUSH'

def REGFLUSH(n=None):
    return (OP_CODE_REGFLUSH, n)

#----------------------------------------------------------------------#

OP_CODE_SET = 101
if __debug__: OP_CODE_SET = 'SET'

def SET(val):
    return ( OP_CODE_SET, val)

#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#  TUPLE                                                               #    
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

#
# tuple(a,b,c)
#
OP_CODE_CREATETUPLE = 200
if __debug__: OP_CODE_CREATETUPLE = 'CREATETUPLE'

def CREATETUPLE(size):
    return ( OP_CODE_CREATETUPLE, size )
    
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#  DICTS                                                               #    
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

#
# dict()
#
OP_CODE_CREATEDICT = 300
if __debug__: OP_CODE_CREATEDICT = 'CREATEDICT'

def CREATEDICT():
    return ( OP_CODE_CREATEDICT, None)

#
# d[k] = v
#
OP_CODE_DICTSETK = 301
if __debug__: OP_CODE_DICTSETK = 'DICTSETK'

def DICTSETK():
    return ( OP_CODE_DICTSETK, None)

#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
# Operators                                                            #
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

#
# a + b
#
#
#
OP_CODE_REGSUM = 400 

def REGSUM():
    return (OP_CODE_REGSUM, None)

#
# a - b
#
OP_CODE_REGSUB = 401

def REGSUB():
    return (OP_CODE_REGSUB, None)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

#
# a * b
#
OP_CODE_REGMUL = 402 

def REGMUL():
    return (OP_CODE_REGMUL, None)

#
# a / b
#
OP_CODE_REGDIV = 403

def REGDIV():
    return (OP_CODE_REGDIV, None)

#
# a mod b
#
OP_CODE_REGMOD = 404

def REGMOD():
    return (OP_CODE_REGMOD,None)

#
# a ** b
#
OP_CODE_REGPOW = 405

def REGPOW():
    return (OP_CODE_REGPOW, None)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

# -v
OP_CODE_REGNEG = 406

def REGNEG():
    return (OP_CODE_REGNEG, None)

#
# ~a
#
OP_CODE_REGBITONE = 407

def REGBITONE():
    return (OP_CODE_REGBITONE, None)

#
# !a
#
OP_CODE_REGNOT = 408

def REGNOT():
    return (OP_CODE_REGNOT, None)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

#
# a << b
#
OP_CODE_REGLSHIFT = 409

def REGLSHIFT():
    return (OP_CODE_REGLSHIFT, None)

#
# a >> b
#
OP_CODE_REGRSHIFT = 410

def REGRSHIFT():
    return (OP_CODE_REGRSHIFT, None)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

#
# a & b
#
OP_CODE_REGBITAND = 411

def REGBITAND():
    return (OP_CODE_REGBITAND, None)

#
# a ^ b
#
OP_CODE_REGBITXOR = 412

def REGBITXOR():
    return (OP_CODE_REGBITXOR, None)

#
# a | b
#
OP_CODE_REGBITOR = 413

def REGBITOR():
    return (OP_CODE_REGBITOR, None)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

#
# a < b
#
OP_CODE_REGLT = 414

def REGLT():
    return (OP_CODE_REGLT, None)

#
# a <= b
#
OP_CODE_REGLTE = 415

def REGLTE():
    return (OP_CODE_REGLTE, None)

#
# a > b
#
OP_CODE_REGGT = 416

def REGGT():
    return (OP_CODE_REGGT, None)

#
# a >= b
#
OP_CODE_REGGTE = 417

def REGGTE():
    return (OP_CODE_REGGTE, None)

#----------------------------------------------------------------------#

#
# a == b
#
OP_CODE_REGEQ = 418

def REGEQ():
    return (OP_CODE_REGEQ,None)

#
# a != b
#
OP_CODE_REGNEQ = 419

def REGNEQ():
    return (OP_CODE_REGNEQ,None)


#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
# SYMBOLS                                                              #
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

#
#  SYMBOL = <value>
#
OP_CODE_STORESYM = 500

def STORESYM():
    return ( OP_CODE_STORESYM, None )

#
#  SYM
# 
OP_CODE_LOADSYM = 501

def LOADSYM():
    return ( OP_CODE_LOADSYM, None	 )

#
# REF SYM
#
OP_CODE_LOADSYMLV = 502

def LOADSYMLV():
    return ( OP_CODE_LOADSYMLV, None )

#----------------------------------------------------------------------#

#
# <obj>.<field>
#
OP_CODE_GETATTR = 510

def GETATTR():
    return ( OP_CODE_GETATTR, None )

#
# REF <obj>.<field>
#
OP_CODE_GETATTRLV = 511

def GETATTRLV():
    return ( OP_CODE_GETATTRLV, None )

#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
# JUMPS                                                                #
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

#
# PC = <addr>
#
OP_CODE_JUMP  = 600
if __debug__: OP_CODE_JUMP  = 'JUMP'

def JUMP(addr):
    return ( OP_CODE_JUMP , addr )

#----------------------------------------------------------------------#

#
# PC + <pos>
#
OP_CODE_JUMPR  = 601
if __debug__: OP_CODE_JUMPR  = 'JUMPR'

def JUMPR(pos):
    return ( OP_CODE_JUMPR , pos )

#----------------------------------------------------------------------#

OP_CODE_IFTRUE = 602
if __debug__: OP_CODE_IFTRUE = 'IFTRUE'

def IFTRUE(addr):
    return (OP_CODE_IFTRUE, addr)

OP_CODE_IFFALSE = 603
if __debug__: OP_CODE_IFFALSE = 'IFFALSE'

def IFFALSE(addr):
    return (OP_CODE_IFFALSE, addr)



#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
# FUNCTIONS                                                            #
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

#
# CALL  callable object
#
# Code:
#
#        fun1 ( 1,2,3, name1=4, name2=5, name3=6 )
#
# STACK VALUES
#
#        [
#            ...
#            1
#            2
#            3
#            ('name1', 4)
#            ('name2', 5)
#            ('name3', 6)
#            <calleble object  fun1 at 0x7f8b0ad411e0 >
#        ]
#
# OPCODE:
#        [
#            CALL(3,3)
#        ]
#
OP_CODE_CALL = 800
if __debug__: OP_CODE_CALL = 'CALL'

def CALL(n_args=0, n_kwargs=0):
    return ( OP_CODE_CALL, (n_args, n_kwargs) )

#
# CALL_SYM  by symbol name
#
# Code:
#        fun1 ( 1,2,3, name1=4, name2=5, name3=6 )
#
# STACK VALUES
#
#        [
#            ...
#            1
#            2
#            3
#            ('name1', 4)
#            ('name2', 5)
#            ('name3', 6)
#            'fun1'
#        ]
#
# OPCODE:
#        [
#            CALL(3,3)
#        ]
#

#: prova
OP_CODE_CALL_SYM = 810
if __debug__: OP_CODE_CALL_SYM = 'CALL_SYM'

def CALL_SYM(n_args=0, n_kwargs=0):
    return ( OP_CODE_CALL_SYM, (n_args, n_kwargs) )

#
# CALL_NATIVE
#
# Code:
#        fun1 ( 1,2,3, name1=4, name2=5, name3=6 )
# 
# STACK VALUES
#
#        [
#            ...
#            1
#            2
#            3
#            ('name1', 4)
#            ('name2', 5)
#            ('name3', 6)
#        ]
#
# OPCODE:
#        [
#            CALL(fun, 3,3)
#        ]
#
OP_CODE_CALL_NATIVE = 820
if __debug__: OP_CODE_CALL_NATIVE = 'CALL_NATIVE'

def CALL_NATIVE(fun_callable, n_args=0, n_kwargs=0):
    return ( OP_CODE_CALL_NATIVE, (fun_callable, n_args, n_kwargs) )


#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
# IO                                                                   #
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

#
# Write da on OUTPUT
#
OP_CODE_OUTPUT = 900
if __debug__: OP_CODE_OUTPUT = 'OUTPUT'

def OUTPUT():
    return ( OP_CODE_OUTPUT, None )


#
# Read (or wait for) input data
#
OP_CODE_INPUT = 35
if __debug__: OP_CODE_INPUT = 'INPUT'

def INPUT():
    return (OP_CODE_INPUT, None)    




#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
# THREADING                                                            #
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#
#----------------------------------------------------------------------#

OP_CODE_FORK = 700
if __debug__: OP_CODE_FORK = 'FORK'

def FORK(addresses):
    return ( OP_CODE_FORK, addresses )


#----------------------------------------------------------------------#

#OP_CODE_SETTIMER  = 34
#
#def SETTIMER(seconds):
#    return ( OP_CODE_SETTIMER , seconds )
#    
#----------------------------------------------------------------------#




#----------------------------------------------------------------------#

#
# Indica che la virtualmachine sta aspettando un particolare tipo di input
#

#OP_CODE_INPUT_MATCH = 35
#if __debug__: OP_CODE_INPUT_MATCH = 'INPUT_MATCH'
#
#def INPUT_MATCH():
#    return (OP_CODE_INPUT_MATCH, None)    
#



#----------------------------------------------------------------------#
# ARRAY                                                                #    
#----------------------------------------------------------------------#

#OP_CODE_ARRAY = 300
#
#def ARRAY(n):
#    return (OP_CODE_ARRAY,n)

#----------------------------------------------------------------------#




#----------------------------------------------------------------------#
#
#OP_CODE_EQUAL  = 38
#
#def EQUAL(val, addr):
#    return ( OP_CODE_EQUAL , (val, addr) )
#
##----------------------------------------------------------------------#
#
#OP_CODE_LT   = 39
#
#def LT(val, addr):
#    return ( OP_CODE_LT	 , (val, addr) )
#
#----------------------------------------------------------------------#

#OP_CODE_MATCH = 40
#
#def MATCH(flag=True):
#    return (OP_CODE_SET, 0 if flag else -1)

#----------------------------------------------------------------------#

#OP_CODE_STACKPUSH  = 41 #'STACKPUSH' #
#OP_CODE_STACKPOP   = 42 #'STACKPOP'  #<n>
#OP_CODE_STACKGET   = 43 #'STACKGET'  #<pos>
#OP_CODE_STACKSET   = 44 #'STACKSET'  #<pos>                Save <value> in stack[$sp+pos]
#
#OP_CODE_STACKPUSHV = 45 #'STACKPUSHV' #<value>              Append <valu> to stack and increm[$sp]
#OP_CODE_STACKSETV  = 46 #'STACKSETV' #<pos> <value>        Save <value> in stack[$sp+pos]
#
#def STACKPUSH():      
#    return (OP_CODE_STACKPUSH, None)
#
#def STACKPOP(n):           
#    return (OP_CODE_STACKPOP, n)
#
#def STACKSET(pos):  
#    return (OP_CODE_STACKSET, pos)
#
#def STACKGET(pos):         
#    return (OP_CODE_STACKGET, pos)
#
#
#def STACKPUSHV(value):  
#    return (OP_CODE_STACKPUSHV, value)
#
#def STACKSETV(pos, value):  
#    return (OP_CODE_STACKSETV, (pos,value))

