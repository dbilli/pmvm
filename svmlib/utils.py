
from . import opcodes

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

OPCODE_NAME = {}

for sym in dir(opcodes):
    if sym.startswith('OP_CODE_'):
        v = getattr(opcodes, sym)
        OPCODE_NAME[ v ] = sym[8:]

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def PFORMAT(p):
    s = ''
    for n,  r in enumerate(p):
        s += "%4s %-10s %s\n" % (n, OPCODE_NAME[r[0]], r[1] if r[1] is not None else '')
    return s

