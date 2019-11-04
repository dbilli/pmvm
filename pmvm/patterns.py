"""
    Pattern:
    
         I{in=<seconds>}(a)

    VM:
         : ALARM n
         : CLOCK 
         
         : a
         
         : LTE n P1
         : MATCH(0)
         : JUMP END
         
       P1: MATCH(1)
         : 

        E: EXITCONTEXT 
      
      END:
"""


from pmvm.vm import INPUT, MATCH, FORK, JUMP, EQUAL, SET, ADD, LT, SETTIMER
from pmvm.vm import STACKPUSHV, STACKGET, STACKPOP, STACKSET, STACKSETV
from pmvm.vm import VM_STATE
from pmvm.vm import vm_run, vm_init, vm_is_finished, vm_set_input, vm_run_all_threads, vm_set_clock
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

class InputPattern(BasePatternMachine):
    """
    Pattern:
    
        I(a)
    
    VM:
          : INPUT(a)
          
          : MATCH()
    """
    def __init__(self, name, input_handler):
        super(InputPattern, self).__init__(name)

        self.input_handler = input_handler

    def compile(self, start_pos=0, end_program=True):

        program = []

        program.append( INPUT(self.input_handler) )

        if end_program == True:
            program.append( MATCH() )

        return program

    def toString(self):
        return "I(%s)" % (self.name)


#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class InputWithTimer(InputPattern):
    """
    Pattern:
    
         I{in=<seconds>}(a)

    VM:
         : SETTIMER n
         : INPUT a 
      END:
    """
    def __init__(self, name, seconds, input_handler):
        super(InputWithTimer, self).__init__(name, input_handler)

        self.seconds       = seconds

    def compile(self, start_pos=0, end_program=True):

        program = []

        program.append( SETTIMER(self.seconds) )
        program.append( INPUT(self.input_handler) )

        if end_program == True:
            program.append( MATCH() )

        return program

    def toString(self):
        return "I{in=%s}(%s)" % (self.name)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class SequencePattern(BasePatternMachine):
    """
    Pattern:
    
        (ABC)
        
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
        # a b c
        #
        program = []
        
        program.append(  MATCH(False) )
        start_pos += 1

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
    
        (A|B|C)
        
    VM:
          : FORK(L2,L3)
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
        
        jumps = [ (start_pos+pos+1) for pos, prog in sub_programs[1:] ]

        program.append( FORK(jumps) )

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
    
        (A)?
        
    VM:
          : FORK(L2)
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

        program.append(  FORK( [start_pos+len(compiled)+1] ) )

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
    
        (A)+
        
    VM:
        L1: code A
          : FORK(L1)
        
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

        program.append( FORK( [start_pos] ) )

        if end_program == True:
            program.append( MATCH(1) )
        
        return program

    def toString(self):
        return "(" + str(self.pattern) + ")+"

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class StarRepetitionPattern(BasePatternMachine):
    """
    Pattern:
    
        (A)*
    
    VM 1:
        L1: FORK(L3)
          : code A
          : JUMP(L1)
        L3: 
        
          : MATCH()


    ComposedPattern:
    
        (A+)?
    
    VM:

          : FORK(L?)         \
                             |
        L+:            \     |
          : code A     | A+  | ?
          : FORK(L+)   /     |
                             |
        L?:                  /

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

class MinMaxRepetitionPattern(BasePatternMachine):
    """
    Pattern:
            (A){N,M}+ 
            
              A A A  A A A A A
              --N->  ----M--->
    VM:
        S  : STACKPUSHV(-1)             ret = -1
             STACKPUSHV(0)              count = 0
           
        LO : ...
             code A
             ...

        LA : STACKGET(-1)        LA+0      read count
           : ADD(1)              LA+1      count = count + 1 
           : STACKSET(-1)        LA+2      save count
                                      
        X  : LT(N, L0)           LA+3      N
           : STACKSETV(-2,0)     LA+4      MATCHED ret = 0. 

        Y  : FORK(END)           LA+5      M
           : LT(M, L0)           LA+6      
        
           : STACKSETV(-2,-1)    LA+7      NOT MACHED (M > 0).  ret=-1

        END: 
           : STACKGET(-2)        LA+8      r0 = ret
           : STACKPOP(2)         LA+9      del ret,count
           
        FIN:                     LA+10 
        
    """
    def __init__(self, name, min, max, pattern):
        super(MinMaxRepetitionPattern, self).__init__(name)

        self.pattern = pattern
        self.min     = min
        self.max     = max

    def compile(self, start_pos=0, end_program=True):

        program = []
        
        pos = start_pos

        #S  : STACKPUSHV(-1)             ret = -1
        #     STACKPUSHV(0)              count = 0
        program.append( STACKPUSHV(-1) )
        program.append( STACKPUSHV(0) )

        #L0 : code A
        L0_pos = pos + len(program)
        compiled = self.pattern.compile(start_pos=L0_pos, end_program=False)
        compiled_len = len(compiled)
        program += compiled

        #LA : STACKGET(-1)        LA+0      read count
        #   : ADD(1)              LA+1      count = count + 1 
        #   : STACKSET(-1)        LA+2      save count
        LA_pos = L0_pos + compiled_len
        program.append( STACKGET(-1) )
        program.append( ADD(1) )
        program.append( STACKSET(-1) )

        #X  : LT(N, L0)           LA+3      N
        #   : STACKSETV(-2,0)     LA+4
        program.append( LT(self.min, L0_pos) )
        program.append( STACKSETV(-2,0) )
        
        #Y  : FORK(END)           LA+5      M
        #   : LT(M, L0)           LA+6      
        program.append( FORK( [LA_pos+8] ) )
        program.append( LT(self.max, L0_pos) )
        
        #   : SETSTACKV(-2,-1)    LA+7
        program.append( STACKSETV(-2,-1) )

        #END: 
        #   : STACKGET(-2)        LA+8      r0 = ret
        #   : STACKPOP(2)         LA+9      del ret,count
        program.append( STACKGET(-2) )
        program.append( STACKPOP(2) )

        #FIN:                     LA+9 
        #if end_program == True:
        #    program.append( MATCH() )

        return program

    def toString(self):
        return "(" + str(self.pattern) + "){%s,%s}+" % (self.min, self.max)






if __name__ == "__main__":

    import sys
    import sys
    import unittest
    import os.path

    from pmvm.vm import DEBUG_FORMAT_PROGRAM, DEBUG_PRINT_PROGRAM, DEBUG
    from pmvm.vm import vm_is_finished
    from pmvm.vm import THREAD_TERMINATED, THREAD_WAIT_IO

    class TestPatterns(unittest.TestCase):
        
        #
        # InputPattern
        #            
        def test_InputPattern(self): 
            
            input_sequence = [
                 # input , expected_input
                ('a', 'a'),
            ]
            
            p  = InputPattern('A', 'a')
            program = p.compile()
            
            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:
                
                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state) == True )
            self.assertTrue( vm_state['threads'][0]['r0']           == 0 )

        #
        # AlternativePattern
        #            
        def test_AlternativePattern(self): 
            
            input_sequence = [
                ('a', 'abc'),
            ]
            
            p = AlternativePattern('Alternative', [
                InputPattern('A', 'a'),
                InputPattern('B', 'b'),
                InputPattern('C', 'c'),
            ])
            
            program = p.compile()

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:
                
                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state)     == True )
            self.assertTrue( vm_state['threads'][0]['r0'] ==  0 )   
            self.assertTrue( vm_state['threads'][1]['r0'] == -1 )   
            self.assertTrue( vm_state['threads'][2]['r0'] == -1 )   
        
        def test_AlternativePattern2(self): 
            
            input_sequence = [
                ('z', 'abc'),
            ]
            
            p = AlternativePattern('Alternative', [
                InputPattern('A', 'a'),
                InputPattern('B', 'b'),
                InputPattern('C', 'c'),
            ])
            
            program = p.compile()
            
            

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:
                
                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state) == True   )
            self.assertTrue( vm_state['threads'][0]['r0'] == -1 )   
            self.assertTrue( vm_state['threads'][1]['r0'] == -1 )   
            self.assertTrue( vm_state['threads'][2]['r0'] == -1 )   
    

        #
        # SequencePattern
        #            
        def test_SequencePattern(self): 
            
            input_sequence = [
                ('a', 'a'),
                ('b', 'b'),
                ('c', 'c'),
            ]
            
            p = SequencePattern('S', [
                InputPattern('A', 'a'),
                InputPattern('B', 'b'),
                InputPattern('C', 'c'),
            ])
            
            program = p.compile()
            
            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:
                
                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state) == True )
            self.assertTrue( vm_state['threads'][0]['r0']      == 0 )   


        #
        # SequencePattern
        #            
        def test_SequencePattern2(self): 
            
            input_sequence = [
                ('b', 'a'),
                ('a', ''),
                ('c', ''),
            ]
            
            p = SequencePattern('S', [
                InputPattern('A', 'a'),
                InputPattern('B', 'b'),
                InputPattern('C', 'c'),
            ])
            
            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:

                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state) == True  )
            self.assertTrue( vm_state['threads'][0]['r0'] == -1 )   

            

        #
        # InputWithTimer
        #            
        def test_AlternativePattern3(self): 
            
            input_sequence = [
                ('z', 'abc'),
            ]
            
            p = AlternativePattern('Alternative', [
                InputWithTimer('A', 5, 'a'),
                InputWithTimer('B', 6, 'b'),
                InputPattern  ('C', 'c'),
            ])
            
            program = p.compile()
            
            DEBUG_FORMAT_PROGRAM(program)
            
            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            t = 0
            
            while t < 10:

                DEBUG(str(t) + "-" * 80)

                vm_set_clock(vm_state, t)

                if t >= 4:      
                    vm_set_input(vm_state, 'b')

                vm_run_all_threads(vm_state, program)
                
                t+=1
                
            self.assertTrue( vm_is_finished(vm_state) == True   )
            #self.assertTrue( vm_state['threads'][0]['r0'] == -1 )   
            #self.assertTrue( vm_state['threads'][1]['r0'] == -1 )   
            #self.assertTrue( vm_state['threads'][2]['r0'] == -1 )   
        
        #
        # OptionalPattern
        #            
        def test_OptionalPattern1(self): 
            
            input_sequence = [
                ('b', 'a'),
            ]
            
            p = OptionalPattern('Optional', 
                InputPattern('A', 'a'),
            )
            
            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:

                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state) == True   )
            self.assertTrue( vm_state['threads'][0]['r0'] == -1 )   
            self.assertTrue( vm_state['threads'][1]['r0'] == 0  )   

        #
        # OptionalPattern
        #            
        def test_OptionalPattern2(self): 
            
            input_sequence = [
                ('b', 'a'),
            ]
            
            p = OptionalPattern('Optional', 
                InputPattern('A', 'a'),
            )
            
            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            t = 0
            
            while t < 10:

                DEBUG(str(t) + "-" * 80)

                vm_set_clock(vm_state, t)

                if t >= 4:      
                    vm_set_input(vm_state, 'c')

                vm_run_all_threads(vm_state, program)
                
                t+=1
                
            self.assertTrue( vm_is_finished(vm_state) == True   )
            self.assertTrue( vm_state['threads'][0]['r0'] == -1 )   
            self.assertTrue( vm_state['threads'][1]['r0'] == 0  )  

        #
        # RepetitionPattern
        #            
        def test_RepetitionPattern1(self): 
            
            input_sequence = [
                ('a', 'a'),
            ]
            
            p = RepetitionPattern('Repetition', 
                InputPattern('A', 'a'),
            )
            
            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:

                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state) == False   )
            self.assertTrue( vm_state['threads'][0]['state'] == THREAD_TERMINATED )   
            self.assertTrue( vm_state['threads'][1]['state'] == THREAD_WAIT_IO  )   

        #
        # RepetitionPattern
        #            
        def test_RepetitionPattern2(self): 
            
            input_sequence = [
                ('a', 'a'),
            ]
            
            p = RepetitionPattern('Repetition', 
                InputWithTimer('A', 4, 'a'),
            )
            
            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            t = 0
            
            while t < 20:

                DEBUG(str(t) + "-" * 80)

                vm_set_clock(vm_state, t)

                if t == 2:      
                    vm_set_input(vm_state, 'a')

                vm_run_all_threads(vm_state, program)
                
                if vm_is_finished(vm_state):
                    break
                
                t+=1
                
            self.assertTrue( vm_is_finished(vm_state) == True   )

            self.assertTrue ( vm_state['threads'][0]['state'] == THREAD_TERMINATED )   
            self.assertTrue ( vm_state['threads'][0]['r0'   ] == 0 )   
            self.assertTrue ( vm_state['threads'][1]['state'] == THREAD_TERMINATED  )   
            self.assertFalse( vm_state['threads'][1]['r0'   ] == 0 )   


        #
        # StarRepetitionPattern
        #            
        def test_StarRepetitionPattern1(self): 
            
            input_sequence = [
                ('c', 'a'),
            ]
            
            p = StarRepetitionPattern('Star', 
                InputPattern('A', 'a'),
            )
            
            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:

                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state) == True   )
            self.assertTrue( vm_state['threads'][0]['state'] == THREAD_TERMINATED )   
            self.assertTrue( vm_state['threads'][1]['state'] == THREAD_TERMINATED )   

        def test_StarRepetitionPattern2(self): 
            
            input_sequence = [
                ('a', 'a'),
            ]
            
            p = StarRepetitionPattern('Star', 
                InputPattern('A', 'a'),
            )
            
            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:

                expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                
                self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            self.assertTrue( vm_is_finished(vm_state) == False   )
            self.assertTrue( vm_state['threads'][0]['state'] == THREAD_TERMINATED )   
            self.assertTrue( vm_state['threads'][1]['state'] == THREAD_TERMINATED )   
            self.assertTrue( vm_state['threads'][2]['state'] == THREAD_WAIT_IO )   


        def test_MinMaxRepetitionPattern(self): 

            input_sequence = [
                ('a', 'a'),
                ('a', 'a'),
                ('a', 'a'),
                ('a', 'a'),
                ('a', 'a'),
            ]
            
            p = MinMaxRepetitionPattern('Star', 
                2,  #min
                4,  #max
                InputPattern('A', 'a'),
            )

            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for c, expected_input in input_sequence:

                #expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                #expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                #self.assertTrue( expected_input_from_machine == expected_input)
                
                vm_set_input(vm_state, c)
                vm_run_all_threads(vm_state, program)
                
            #self.assertTrue( vm_is_finished(vm_state) == True   )
            for t in vm_state['threads']:
                DEBUG("Thread: %s -> status=%s ret=%s" % (t['id'], t['state'], t['r0']))


        def test_timestamp_test(self): 

            ts = 0

            input_sequence = [
                (ts+1, 'a'),
                (ts+2, 'a'),
                (ts+3, 'a'),
                (ts+4, 'a'),
                (ts+5, 'a'),
            ]
            
            p = MinMaxRepetitionPattern('Star', 
                2,  #min
                4,  #max
                InputPattern('A', 'a'),
            )

            program = p.compile()

            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            for ts, input_data in input_sequence:
                DEBUG("*" * 80)
                DEBUG("%s" % (ts))
                DEBUG("*" * 80)
                vm_set_clock(vm_state, ts)
                vm_set_input(vm_state, input_data)

                vm_run_all_threads(vm_state, program)
                
                for t in vm_state['threads']:
                    DEBUG("\t", "Thread: %s -> status=%s ret=%s" % (t['id'], t['state'], t['r0']))

        #
        # InputWithTimer
        #            
        def test_InputWithTimer(self): 
            
            
            input_sequence = [
                 # input , expected_input
                ('a', 'a'),
            ]
            
            p  = InputWithTimer('A', 5, 'a')
            program = p.compile()
            
            DEBUG_PRINT_PROGRAM(program)

            vm_state = VM_STATE()
            vm_init(vm_state, program)    
            
            ts = 0
            
            #for c, expected_input in input_sequence:
            while ts < 10:
                DEBUG("*" * 80)
                DEBUG("%s" % (ts))
                DEBUG("*" * 80)
                
                #expected_input_from_machine = get_machine_expected_inputs(vm_state, program )
                
                #expected_input_from_machine = ''.join(sorted(expected_input_from_machine))
                #self.assertTrue( expected_input_from_machine == expected_input)

                if ts < 3:
                    vm_set_input(vm_state, str(ts))
                if ts == 4:
                    vm_set_input(vm_state, 'a')

                vm_set_clock(vm_state, ts)
                vm_run_all_threads(vm_state, program)
                
                
                ts += 1
                
            self.assertTrue( vm_is_finished(vm_state) == True )
            self.assertTrue( vm_state['threads'][0]['r0'] == 0 )



    unittest.main()


    sys.exit(-1)
