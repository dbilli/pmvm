
from pmvm.vm import INPUT
from pmvm.vm import MATCH
from pmvm.vm import SPLIT
from pmvm.vm import JUMP
from pmvm.vm import VM_STATE
from pmvm.vm import run_machine


#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class BasePatternMachine(object):

	def __init__(self, name):
		self.name = name

	def compile(self, start_pos=0, end_program=True):
		raise Exception("Not implemented")

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

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

class MinMaxRepetitionPattern(BasePatternMachine):
	"""
	Pattern:
	        A+{min,max} 
	        
	        A A A  A A A
		-min-> -max->
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
		for n in xrange(self.min):
			compiled = self.pattern.compile(start_pos=start_pos, end_program=False)
			program += compiled
			start_pos += len(compiled)

		#
		#  : SPLIT(LE,LM)
		LM_pos = start_pos + 1
		LE_pos = LM_pos + (2 * (self.max-self.min)) - 1

		program.append( SPLIT([LE_pos, LM_pos]) )
		start_pos += 1

		#  : code A
		#
		#  : SPLIT(+1,LE)
		
		for n in xrange(self.max-self.min):
			compiled = self.pattern.compile(start_pos=start_pos, end_program=False)
			program += compiled
			start_pos += len(compiled)

			if n < (self.max-self.min-1):
				program.append( SPLIT([LE_pos, start_pos + 1]) )

		if end_program == True:
			program.append( MATCH() )

		return program

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __name__ == "__main__":

	def PRINT(p):
		for n, r in enumerate(p):
			print n, r

	import pprint

	p1 = SinglePattern('A', 'a')
	p2 = SinglePattern('B', 'b')
	p3 = SinglePattern('C', 'c')
	#
	#p = AlternativePattern('Alternative', [p1,p2,p3])

	#p = RepetitionPattern('R', p1)
	#p = SequencePattern('S', [p3, p])
	#p = StarRepetitionPattern('*', p1)
	p = MinMaxRepetitionPattern('minmax', p1, 2, 4)
	
	p = SequencePattern('S', [p, p3])

	
	program = p.compile()

	PRINT(program)

	state = VM_STATE()
	run_machine(state, program, 'a')
	#run_machine(state, program, 'a')
	#run_machine(state, program, 'c')
	#run_machine(state, program, 'a')
	#run_machine(state, program, 'a')
	#run_machine(state, program, 'a')
	run_machine(state, program, 'c')

	print state['matched']
