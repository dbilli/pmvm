
import time

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def DEBUG(*args):
	#pass 
	print ' '.join([str(a) for a in args])

def DEBUG_SLEEP():
	#pass
	time.sleep(1)

#----------------------------------------------------------------------#
# OPCODES                                                              #
#----------------------------------------------------------------------#

OP_CODE_INPUT = 'INPUT'

def INPUT(input):
	return (OP_CODE_INPUT, input)

#----------------------------------------------------------------------#

OP_CODE_MATCH = 'MATCH'

def MATCH():
	return (OP_CODE_MATCH, None)

#----------------------------------------------------------------------#

OP_CODE_SPLIT = 'SPLIT'

def SPLIT(addresses):
	return ( OP_CODE_SPLIT, addresses )

#----------------------------------------------------------------------#

OP_CODE_JUMP  = 'JUMP'

def JUMP(addr):
	return ( OP_CODE_JUMP , addr )

#----------------------------------------------------------------------#
# Virtual Machine state                                                #
#----------------------------------------------------------------------#

_tid = 0

def VM_THREAD(program_counter=0):
	
	global _tid
	
	thread = {
		'id'             : _tid,
		'stopped'        : False,
		'program_counter': program_counter,
	}
	_tid += 1

	return thread

def VM_STATE():

	state = {
		'threads': {},
		'matched': False,
	}

	main_thread = VM_THREAD()
	state['threads'][ main_thread['id'] ] = main_thread

	return state

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

def run_machine( vm_run_state, program, input_to_process):

	input_consumed = False

	DEBUG("-----------------")
	DEBUG("RUN", input_to_process)

	for t in vm_run_state['threads'].values():
		t['stopped'] = False 

	while True:

		threads_to_execute = [ t for t in vm_run_state['threads'].values() if t['stopped'] != True ]
		if not threads_to_execute:
			break

		DEBUG("TURN", len(threads_to_execute))
		for t in threads_to_execute:
			DEBUG("\t", t)

		DEBUG( "" )

		for thread in threads_to_execute:

			DEBUG("\t", "THREAD", thread['id'])

			pc = thread['program_counter']

			#DEBUG( "\t", "\t", pc, len(program), instruction )

			opcode, params = program[pc]
			DEBUG( "\t", "\t", pc, len(program), opcode, params )

			if opcode == OP_CODE_INPUT:
				if input_consumed:
					thread['stopped'] = True
					continue

			if opcode == OP_CODE_INPUT:

				input_match = params
				
				if input_to_process == input_match:

					#
					#onmatch = instruction['onmatch']
					#if onmatch:
					#	onmatch()

					input_consumed = True

					DEBUG( "\t", "\t", "CONSUMED" )
						
					thread['consumed'] = True
					
					pc += 1
					thread['program_counter'] = pc

				else:
					DEBUG( "\t", "\t", "NOT MACHED" )
					del vm_run_state['threads'][thread['id']]

			elif opcode == OP_CODE_MATCH:

				vm_run_state['matched'] = True

				DEBUG( "\t", "\t", "FINISH" )

				del vm_run_state['threads'][thread['id']]

			elif opcode == OP_CODE_JUMP:

				pc = params

				thread['program_counter'] = pc

			elif opcode == OP_CODE_SPLIT:

				addresses = params

				thread['program_counter'] = addresses[0]

				for jump in addresses[1:]:

					thread = VM_THREAD(jump)

					vm_run_state['threads'][thread['id']] = thread

			DEBUG( "\t", "----" )

	return vm_run_state['matched']

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __name__ == "__main__":

	#import unittest
	#
	#class TestStringMethods(unittest.TestCase):
	#
	#	def test_upper(self):
	#		self.assertEqual('foo'.upper(), 'FOO')
	#
	#	def test_isupper(self):
	#		self.assertTrue('FOO'.isupper())
	#		self.assertFalse('Foo'.isupper())
	#
	#	def test_split(self):
	#		s = 'hello world'
	#		self.assertEqual(s.split(), ['hello', 'world'])
	#		# check that s.split fails when the separator is not a string
	#		with self.assertRaises(TypeError):
	#			s.split(2)
	#			
	
	#unittest.main()

	#
	# a
	#
	
	program = [
		INPUT('c'),
		MATCH(),
	]

	#
	# a | b | c
	#
	program = [
		SPLIT([1,3,5]),
			INPUT('a'),
		JUMP(6),   #2
			INPUT('b'),
		JUMP(6),   #4
			INPUT('c'),
		MATCH(),
	]

	#
	# a?
	#
	program = [
		SPLIT([1,2]),   
			INPUT('a'),
		MATCH(),
	]



	#
	# A+B
	#
	program = [
		# A
		INPUT('a'),
		SPLIT( [0,2] ),
		# B
		INPUT('b'),
		MATCH(),
	]

	#
	# A*
	#
	program = [
		SPLIT([1,3]),
		# A
		INPUT('a'),
		JUMP(0),
		# B
		MATCH(),
	]

	#
	# a+
	#
	program = [
		INPUT('a'), 
		SPLIT([0,2]),
		MATCH(),
	]

	state = VM_STATE()
	matched = run_machine(state, program, 'a')
	matched = run_machine(state, program, 'a')
	matched = run_machine(state, program, 'c')
	matched = run_machine(state, program, 'a')
	matched = run_machine(state, program, 'b')
	matched = run_machine(state, program, 'c')

	print "----------------"
	print matched
