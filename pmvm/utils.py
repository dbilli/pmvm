
class DictInput(object):

	def __init__(self, data):
		self.data = data

	def __eq__(self, other):
		return self.data == other
		#print "__cmd__", self.data, other
		#if   self.data < other: return -1
		#elif self.data > other: return 1
		#else                  : return 0
	
	def __repr__(self):
		return "<DictInput(%s)>" % (self.data)
	def __str__(self):
		return "DATA(%s)" % (self.data)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __name__ == "__main__":
	
	from pmvm.vm import VM_STATE
	from pmvm.vm import run_machine	
	
	from pmvm.patterns import *

	def PRINT(p):
		for n, r in enumerate(p):
			print n, r

	import pprint

	pa = SinglePattern('A', DictInput({'key': 'a'}) )
	pb = SinglePattern('B', DictInput({'key': 'b'}) )
	p = MinMaxRepetitionPattern("minmax", pa, 2, 4)
	p = SequencePattern('S', [ p, pb ])

	program = p.compile()

	PRINT(program)

	state = VM_STATE()
	run_machine(state, program, {'key': 'a'} )
	run_machine(state, program, {'key': 'a'} )
	run_machine(state, program, {'key': 'a'} )
	#run_machine(state, program, {'key': 'a'} )
	#run_machine(state, program, {'key': 'a'} )
	run_machine(state, program, {'key': 'b'} )
	#run_machine(state, program, 'a')
	#run_machine(state, program, 'c')
	#run_machine(state, program, 'a')
	#run_machine(state, program, 'a')
	#run_machine(state, program, 'a')
	#run_machine(state, program, 'c')

	print state['matched']
