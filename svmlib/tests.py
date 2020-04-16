if __name__ == "__main__":

    import sys
    import unittest
    
    from pmvm.opcodes import *
    from pmvm.vm import *

    class BaseTests(unittest.TestCase):

        def test_0(self): 

            program = []

            vm = VM_STATE()
            vm_init(vm, program)
            
            vm_run(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )

        def test_1_pass(self): 

            program = [
                PASS(),
            ]

            vm = VM_STATE()
            vm_init(vm, program)
            
            vm_run(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )

        def test_1_stop(self): 

            program = [
                STOP(0),
            ]

            vm = VM_STATE()
            vm_init(vm, program)
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['r0'] == 0 )

        def test_1_stop2(self): 

            program = [
                STOP(-1),
            ]

            vm = VM_STATE()
            vm_init(vm, program)
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['r0'] == -1 )

        def test_2_jump(self): 

            program = [
                PASS(),       # 0
                JUMP(3),      # 1
                PASS(),       # 2
                PASS(),       # 3
            ]

            vm = VM_STATE()
            vm_init(vm, program)
            
            vm_run_all_threads(vm, program)
            
            print(vm['threads'])
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['_stats']['op_count'] == 3)

        def test_2_jump2(self): 

            program = [
                JUMP(2),      # 1
                PASS(),       # 0
            ]
            
            vm = VM_STATE()

            with self.assertRaises(VMException):
                vm_init(vm, program)
                vm_run_all_threads(vm, program)
            
            self.assertFalse( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['_stats']['op_count'] == 1)


        def test_3_split(self): 

            program = [
                FORK([3,6]),   # 0
                PASS()   ,     # 1   Thread 0 (main)
                JUMP(10) ,     # 2

                PASS()   ,     # 3   thread 1
                PASS()   ,     # 4
                JUMP(10) ,     # 5   

                PASS()   ,     # 6   thread 2
                PASS()   ,     # 7
                PASS()   ,     # 8
                JUMP(10) ,     # 9

                PASS()   ,     # 10  END
            ]

            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( len(vm['threads']) == 3 )
            self.assertTrue( vm['threads'][0]['_stats']['op_count'] == 4 )
            self.assertTrue( vm['threads'][1]['_stats']['op_count'] == 5 )
            self.assertTrue( vm['threads'][2]['_stats']['op_count'] == 6 )




        def test_4_timer(self): 

            program = [
                SETTIMER(666),  # 1
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)
                
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['timer_clock'] == 666)

        '''
        def test_5_input_match(self): 

            program = [
                SET('a'),
                INPUT(None),  # 1
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_set_input(vm, 'a')
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['r0'] == 1 )

        def test_5_input_not_match(self): 

            program = [
                SET('a'),
                INPUT('a'),  # 1
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_set_input(vm, 'b')
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertFalse( vm['threads'][0]['r0'] == 1 )


        def test_6_1_pushstack(self): 

            program = [
                STACKPUSHV(666),  # 1
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['stack'] == [666,] )

        def test_6_2_stackpop(self): 

            program = [
                STACKPUSHV(1),  # 1
                STACKPUSHV(2),  # 1
                STACKPUSHV(3),  # 1
                STACKPUSHV(4),  # 1
                STACKPOP(1),
                STACKPOP(1),
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['stack'] == [1,2] )

        def test_6_3_stackset(self): 

            program = [
                STACKPUSHV(1),  # 1
                STACKPUSHV(2),  # 1
                STACKPUSHV(3),  # 1
                STACKPUSHV(4),  # 1
                STACKSETV(0, 11),
                STACKSETV(1, 12),
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['stack'] == [11,12,3,4] )

        def test_6_4_stackget(self): 

            program = [
                STACKPUSHV('a'),  # 0
                STACKPUSHV('b'),  # 1
                STACKPUSHV('c'),  # 2
                STACKPUSHV('d'),  # 3
                STACKGET(2),
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]["r0"] == 'c' )

        def test_6_5_stackget(self): 

            program = [
                STACKPUSHV('a'),  # 0
                STACKPUSHV('b'),  # 1
                STACKPUSHV('c'),  # 2
                STACKPUSHV('d'),  # 3
                STACKGET(-1),
            ]
         
            vm = VM_STATE()
            vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]["r0"] == 'd' )
        '''

    unittest.main()
