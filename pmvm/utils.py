
class DictInputMatcher(object):

    def __init__(self, data):
        self.data = data

    def __eq__(self, other):
        return self.data == other
        #print "__cmd__", self.data, other
        #if   self.data < other: return -1
        #elif self.data > other: return 1
        #else                  : return 0
    
    def __repr__(self):
        return "<%s(%s)>" % (self.__class__.__name__, self.data)
    def __str__(self):
        return "DATA(%s)" % (self.data)

#----------------------------------------------------------------------#
#                                                                      #
#----------------------------------------------------------------------#

if __name__ == "__main__":
    
    from pmvm.vm import VM_STATE
    from pmvm.vm import vm_run    
    
    from pmvm.patterns import *
    from pmvm.utils import DictInputMatcher

    def PRINT(p):
        for n, r in enumerate(p):
            print(n, r)

    import pprint


    #
    # A{2,4}+ B  <EOF>
    #
    p = SequencePattern('S', [ 
        MinMaxRepetitionPattern("minmax", 2, 4, 
            SinglePattern('A', DictInputMatcher({'key': 'a'}) )
        ), 
        SinglePattern('B', DictInputMatcher({'key': 'b'}) ) 
    ])
    
    print(p)

    program = p.compile()

    print("*" * 80)
    print("PROGRAM")
    print("*" * 80)
    PRINT(program)

    print("*" * 80)
    print("EXECUTION")
    print("*" * 80)
    
    input_pattern = [
        {'key': 'a'},
        {'key': 'a'},
        {'key': 'a'},
        #{'key': 'a'},
        #{'key': 'a'},
        #{'key': 'a', 'key2': 666},
        {'key': 'c'},
    ]
    
    

    state = VM_STATE()
    vm_init(state, program)
    
    for i in input_pattern:
        vm_run(state, program, i )
        print("-------------------------" + str(state['matched']))
    
    #vm_run(state, program, {'key': 'a'} )
    ##run_machine(state, program, {'key': 'a', 'key2': 666} )
    #vm_run(state, program, {'key': 'a', 'key2': 666} )
    ##vm_run(state, program, {'key': 'a'} )
    ##vm_run(state, program, {'key': 'a'} )
    ##run_machine(state, program, {'key': 'a'} )
    ##run_machine(state, program, {'key': 'a'} )
    #vm_run(state, program, {'key': 'b'} )
    ##run_machine(state, program, 'a')
    ##run_machine(state, program, 'c')
    ##run_machine(state, program, 'a')
    ##run_machine(state, program, 'a')
    ##run_machine(state, program, 'a')
    ##run_machine(state, program, 'c')


    print("*" * 80)
    print("RESULT")
    print("*" * 80)
    print(state['matched'])
