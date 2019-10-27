
from pmvm.vm import INPUT
from pmvm.vm import MATCH#, NOMATCH
from pmvm.vm import SPLIT, JUMP, EQUAL
from pmvm.vm import SET, ADD
from pmvm.vm import VM_STATE
from pmvm.vm import vm_run, vm_init, vm_is_finished
from pmvm.vm import get_machine_expected_inputs

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class BasePatternMachine(object):

    def __init__(self, name):
        self.name = name

    def compile(self, start_pos=0, end_program=True):
        raise Exception("Not implemented")

    def toString(self):
        raise Exception("Not implemented")

    def __str__(self):
        return self.toString()

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class SinglePattern(BasePatternMachine):
    """
    Pattern:
    
        a
    
    VM:
          : INPUT(a)
          
          : MATCH()
    """
    def __init__(self, name, input_handler):
        super(SinglePattern, self).__init__(name)

        self.input_handler = input_handler

    def compile(self, start_pos=0, end_program=True):

        program = []

        program.append( INPUT(self.input_handler) )

        if end_program == True:
            program.append( MATCH() )

        return program

    def toString(self):
        return "<%s>" % (self.name)
        
#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class SequencePattern(BasePatternMachine):
    """
    Pattern:
    
        ABC
        
    VM:
          : code A
          : code B
          : code C
          
          : MATCH()
    """
    def __init__(self, name, patterns):
        super(SequencePattern, self).__init__(name)

        self.patterns = patterns

    def compile(self, start_pos=0, end_program=True):

        #
        # a | b | c
        #
        program = []

        sub_program_pos = start_pos
        for pattern in self.patterns:
            compiled = pattern.compile(start_pos=sub_program_pos, end_program=False)
            
            program += compiled
            
            sub_program_pos += len(compiled)

        if end_program == True:
            program.append(  MATCH() )
        
        return program

    def toString(self):
        return "(" + ','.join([ str(p) for p in self.patterns ]) + ")"

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class AlternativePattern(BasePatternMachine):
    """
    Pattern:
    
        A|B|C
        
    VM:
          : SPLIT(L1,L2,L3)
        L1: code A
          : JUMP(L4)
        L2: code B
          : JUMP(L4)
        L3: code C
          : JUMP(L4)
        L4: 
            
          : MATCH()
    """

    def __init__(self, name, patterns):

        super(AlternativePattern, self).__init__(name)

        self.patterns = patterns

    def compile(self, start_pos=0, end_program=True):

        program = []

        sub_program_pos = 0

        sub_programs = []
        for pattern in self.patterns:
            
            compiled = pattern.compile(start_pos=sub_program_pos, end_program=False)
            
            sub_programs.append( (sub_program_pos, compiled) )

            sub_program_pos += len(compiled) + 1
        
        jumps = [ (start_pos+pos+1) for pos, prog in sub_programs ]

        program.append( SPLIT(jumps) )

        for pos, subprogram in sub_programs:
            program += subprogram
            program.append(  JUMP( start_pos + sub_program_pos + 1 ) )

        if end_program == True:
            program.append( MATCH() )

        return program

    def toString(self):
        return "(" + '|'.join([ str(p) for p in self.patterns ]) + ")"

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class OptionalPattern(BasePatternMachine):
    """
    Pattern:
    
        A?
        
    VM:
          : SPLIT(L1,L2)
        L1: code A
        L2: 
        
          : MATCH()
    """
    
    def __init__(self, name, pattern):
        super(OptionalPattern, self).__init__(name)

        self.pattern = pattern

    def compile(self, start_pos=0, end_program=True):

        program = []

        compiled = self.pattern.compile(start_pos=(start_pos + 1), end_program=False)

        program.append(  SPLIT( [start_pos+1, start_pos+len(compiled)+1] ) )

        program += compiled

        if end_program == True:
            program.append( MATCH() )

        return program

    def toString(self):
        return "(" + str(self.pattern) + ")?"

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class RepetitionPattern(BasePatternMachine):
    """
    Pattern:
    
        A+
        
    VM:
        L1: code A
          : SPLIT(L1,L2)
        L2: 
        
          : MATCH()
    """
    def __init__(self, name, pattern):
        super(RepetitionPattern, self).__init__(name)

        self.pattern = pattern

    def compile(self, start_pos=0, end_program=True):

        program = []

        compiled = self.pattern.compile(start_pos=start_pos, end_program=False)

        program += compiled

        end_pos = start_pos + len(compiled) + 1

        program.append( SPLIT( [start_pos, end_pos] ) )

        if end_program == True:
            program.append( MATCH() )
        
        return program

    def toString(self):
        return "(" + str(self.pattern) + ")+"

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class StarRepetitionPattern(BasePatternMachine):
    """
    Pattern:
    
        A*
    
    VM 1:
        L1: SPLIT(L2, L3)
        L2: code A
          : JUMP(L1)
        L3: 
        
          : MATCH()
    
    Pattern:
    
        A+?
    
    VM:
          : SPLIT(L1,L2)
        L1: 
        
        L3: code A
          : SPLIT(L3,L4)
        L4: 
        
        L2: 
        
          : MATCH()
    """
    def __init__(self, name, pattern):
        super(StarRepetitionPattern, self).__init__(name)

        self.pattern = OptionalPattern(name+'?', RepetitionPattern(name+"+", pattern))

    def compile(self, start_pos=0, end_program=True):
        return self.pattern.compile(start_pos=start_pos, end_program=end_program)

    def toString(self):
        return "(" + str(self.pattern) + ")*"

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class MinMaxRepetitionPattern_OLD(BasePatternMachine):
    """
    Pattern:
            A+{min,max} 
            
            A A A  A A A A
           -min->  -max->
    VM:
          : code A
          : code A
          : code A
          
          : SPLIT(LE,LM)
          
        LM:
        
          : code A
          : SPLIT(+1,LE)

          : code A
          : SPLIT(+1,LE)

          : code A

        LE:
        
          : MATCH()
    """
    def __init__(self, name, pattern, min=1, max=None):
        super(MinMaxRepetitionPattern, self).__init__(name)

        self.pattern = pattern
        self.min     = min
        self.max     = max

    def compile(self, start_pos=0, end_program=True):

        program = []

        #  : code A
        #  : code A
        #  : code A
        for n in range(self.min):
            compiled = self.pattern.compile(start_pos=start_pos, end_program=False)
            program += compiled
            start_pos += len(compiled)

        #
        #  : SPLIT(LE,LM)
        LM_pos = start_pos + 1
        LE_pos = LM_pos + (len(compiled) * (self.max-self.min)) + (1 * (self.max-self.min-1))

        program.append( SPLIT([LE_pos, LM_pos]) )
        start_pos += 1

        #  : code A
        #
        #  : SPLIT(+1,LE)
        
        for n in range(self.max-self.min):
            compiled = self.pattern.compile(start_pos=start_pos, end_program=False)
            program += compiled
            start_pos += len(compiled)

            if n < (self.max-self.min-1):
                program.append( SPLIT([LE_pos, start_pos + 1]) )

        if end_program == True:
            program.append( MATCH() )

        return program

    def toString(self):
        return "(" + str(self.pattern) + "){%s,%s}+" % (self.min, self.max)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#


class MinMaxRepetitionPattern(BasePatternMachine):
    """
    Pattern:
            A+{N,M} 
            
              A A A  A A A A A
              --N->  ----M--->
    VM:
           : SET(0)             1
        LO :                    2 
           :  code A
        LA : ADD(1)             
        L1 : EQUAL(N  , LN)     +1      matched N times?
        L2 : EQUAL(M  , LM)     +2      matched M times?
        L3 : EQUAL(M+1, LX)     +3      matched > M times?
        L  : JUMP(LO)           +4

        LN : MATCH()            +5
             SPLIT(END, L0)     +6

        LM : SPLIT(END, L0)     +7

        LX : MATCH(0)           +8
        
        END:                    +9
             
    """
    def __init__(self, name, pattern, min=1, max=None):
        super(MinMaxRepetitionPattern, self).__init__(name)

        self.pattern = pattern
        self.min     = min
        self.max     = max

    def compile(self, start_pos=0, end_program=True):

        program = []

        #   : SET(r,0)
        program.append( SET(0) )

        #L0 : code A
        L0_pos = len(program)
        compiled = self.pattern.compile(start_pos=L0_pos, end_program=False)
        program += compiled

        #LA : ADD(1)
        LA_pos = len(program)
        program.append( ADD(1) )

        #L1 : EQUAL(N  , LN)
        #L2 : EQUAL(M  , LM)
        #L3 : EQUAL(M+1, LX)
        program.append( EQUAL(self.min  , LA_pos+5) )
        program.append( EQUAL(self.max  , LA_pos+7) )
        program.append( EQUAL(self.max+1, LA_pos+8) )

        #L  : JUMP(LO)
        program.append( JUMP(L0_pos) )
           
        #LN : SPLIT(END, L0)
        program.append( MATCH() )
        program.append( SPLIT([LA_pos+9, L0_pos]) )

        #LM : SPLIT(END, L0)
        program.append( SPLIT([LA_pos+9, L0_pos]) )
        
        #LX : MATCH(0)
        program.append( MATCH(False) )
          

        #END:
        
        #if end_program == True:
        #    program.append( MATCH() )

        return program

    def toString(self):
        return "(" + str(self.pattern) + "){%s,%s}+" % (self.min, self.max)




if __name__ == "__main__":

    import sys
    
    input_string = sys.argv[1]

    def PRINT(p):
        for n, r in enumerate(p):
            print(n, r)

    import pprint

    p  = SinglePattern('A', 'a')
    
    p1 = SinglePattern('A', 'a')
    p2 = SinglePattern('B', 'b')
    p3 = SinglePattern('C', 'c')
    p = AlternativePattern('Alternative', [p1,p2,p3])
    #
    #p = SequencePattern('S', [p1, p2, p3])
    #p = RepetitionPattern('R', p)
    #p = StarRepetitionPattern('*', p1)
    p = MinMaxRepetitionPattern('minmax', p, 2, 4)
    #p = SequencePattern('S', [p, p3])

    print("PATTERN", p)
    print("INPUT  ", input_string)
    

    print("-----------PROGRAM------------")
    program = p.compile()
    PRINT(program)
    print("-------------END--------------")

    vm_state = VM_STATE()

    vm_init(vm_state, program)
    
    while input_string:
        c = input_string[0]
        input_string = input_string[1:]

        expected = get_machine_expected_inputs(vm_state, program )

        print( expected, "->", c)
        
        vm_run(vm_state, program, c)

        print("vm threads:         = ", )
        for tid, t in sorted(vm_state['threads'].items()):
            print("\t", t)
        print("vm status: finished = ", vm_is_finished(vm_state))
        print("vm status: matched  = ", vm_state['matched'    ])
        print("vm status: group    = ", vm_state['input_group'])

        if (vm_is_finished(vm_state)):
            print("FINISHED")
            break
        
    for i,r in enumerate(program): print("%3d %s %s" % (i, r[0],r[1]) )
    print(">>>>>>>>>>> FINISH >>>>>>>>>>")
    print("Remaining:", input_string)	
