if __name__ == "__main__":

    import sys
    import unittest
    
    from svmlib.opcodes import *
    from svmlib.vm import *

    class BaseTests(unittest.TestCase):

        def test_no_program(self): 

            program = []

            vm = vm_create()
                        
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )

        def test_1_pass(self): 

            program = [
                PASS(),
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )

        def test_STOP_1(self): 

            program = [
                STOP(0),
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 0 )




        def test_STOP_2(self): 

            program = [
                STOP(-1),
            ]

            vm = vm_create()

            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == -1 )



        def test_REGFLUSH(self): 

            program = [
                PASS(),
                PASS(),
                SET('foo'),
                REGFLUSH(),
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( len(vm['threads'][0]['regstack']) == 0 )

        def test_SET(self): 

            program = [
                SET(666),
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 666 )
            
        
        def test_CREATETUPLE(self): 

            program = [
                SET(1),
                SET(2),
                SET(3),
                CREATETUPLE(3),
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == (1,2,3) )

        #
        # Dicts
        #
        def test_CREATEDICT(self): 

            program = [
                CREATEDICT(),
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == {} )

        def test_DICTSETK(self): 

            program = [
                CREATEDICT(),
                SET('k'),
                SET(5),
                DICTSETK()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == {'k':5} )
            
         
        def test_REGSUM(self): 

            program = [
                SET(1),
                SET(2),
                REGSUM()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 3 )

        def test_REGSUB(self): 

            program = [
                SET(1),
                SET(2),
                REGSUB()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == -1 )

        #
        #
        #
        def test_REGMUL(self): 

            program = [
                SET(2),
                SET(2),
                REGMUL()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 4 )

        def test_REGDIV(self): 

            program = [
                SET(1),
                SET(2),
                REGDIV()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 0.5 )

        def test_REGMOD(self): 

            program = [
                SET(7),
                SET(2),
                REGMOD()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 1 )

        def test_REGPOW(self): 

            program = [
                SET(2),
                SET(10),
                REGPOW()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 1024 )



        def test_REGNEG(self): 

            program = [
                SET(10),
                REGNEG()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == -10 )

        def test_REGBITONE(self): 

            program = [
                SET(1),
                REGBITONE()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == ~1 )

        def test_REGNOT(self): 

            program = [
                SET(False),
                REGNOT()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == (not(False)) )

        def test_REGLSHIFT(self): 

            program = [
                SET(0x4),
                SET(1),
                REGLSHIFT()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 0x8 )
            
        def test_REGRSHIFT(self): 

            program = [
                SET(0x8),
                SET(3),
                REGRSHIFT()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 1 )


        #
        # bits
        #
        def test_REGBITAND(self): 

            program = [
                SET(0x1),
                SET(0x3),
                REGBITAND()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 0x1 )

        def test_REGBITXOR(self): 

            program = [
                SET(0x01),
                SET(0x03),
                REGBITXOR()
            ]

            vm = vm_create()
            
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 0x2 )   

        def test_REGBITOR(self): 

            program = [
                SET(0x1),
                SET(0x2),
                REGBITOR()
            ]

            vm = vm_create()
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 0x3 )   


        #
        #
        #
        def test_REGLT(self): 

            program = [
                SET(1),
                SET(1),
                REGLT()
            ]

            vm = vm_create()
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == False)  

        def test_REGLTE(self): 

            program = [
                SET(2),
                SET(2),
                REGLTE()
            ]

            vm = vm_create()
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == True )  

        def test_REGGT(self): 

            program = [
                SET(3),
                SET(3),
                REGGT()
            ]

            vm = vm_create()
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == False )  

        def test_REGGTE(self): 

            program = [
                SET(3),
                SET(3),
                REGGTE()
            ]

            vm = vm_create()
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == True )  

        #
        #
        #
        def test_REGEQ(self): 

            program = [
                SET(3),
                SET(3),
                REGEQ()
            ]

            vm = vm_create()
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == True )  

        def test_REGNEQ(self): 

            program = [
                SET(3),
                SET(3),
                REGNEQ()
            ]

            vm = vm_create()
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == False )  

        #
        # Symbols
        #

        def test_LOADSYM(self): 

            context = {
                'a': [1,2,3]
            }

            program = [
                SET('a'),
                LOADSYM()
            ]
            

            vm = vm_create(context)
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['context']['a'] == [1,2,3] )  


        def test_LOADSYMLV(self): 

            context = {
                'a':None
            }

            program = [
                SET('a'),
                LOADSYMLV(),
                SET(666),
                STORESYM()
            ]
            
            vm = vm_create(context)
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['context']['a'] == 666 )  

        #
        #
        #

        def test_GETATTR(self): 

            context = {
                'obj': { 'k1': 666 }
            }

            program = [
                SET('obj'),
                LOADSYM(),
                SET('k1'),
                GETATTR()
            ]
            
            vm = vm_create(context)
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 666 )  

        def test_GETATTRLV(self): 

            context = {
                'obj': { 'k1': 666 }
            }

            program = [

                SET('obj'),
                LOADSYMLV(),   # obj.

                SET('k1'),     
                GETATTRLV(),   # REF obj.k1
                                
                SET(777),
                
                STORESYM(),    # obj.k1 = 777
            ]
            
            vm = vm_create(context)
            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['context']['obj']['k1'] == 777 )  

        #
        # CALLS
        #
        def test_CALL_1(self): 

            def fun_sum(thread, *args, **kwargs):
                return sum(args) + sum(kwargs.values())

            context = {
                'sum': fun_sum
            }


            #
            #  print( 1+2, 4, param1=5)
            #
            program = [
                SET(1),        # push value 1
                SET(2),        # push value 2
                REGSUM(),      # sum params (1+2) and push result on the stack
                
                SET(4),
                
                SET('param1'),
                SET(5),
                CREATETUPLE(2),
                
                SET("sum"),  
                LOADSYM(),     # Load function symbol
                
                CALL(2,1),        # Execute function with parameters on the stack
                
                #STOP(0xABC),       # exit(0)
            ]

            vm = vm_create(context)

            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 12 )


        def test_CALL_NATIVE(self): 

            def fun_sum(thread, *args, **kwargs):
                return sum(args) + sum(kwargs.values())


            #
            #  print( 1+2, 4, param1=5)
            #
            program = [
                SET(1),        # push value 1
                SET(2),        # push value 2
                REGSUM(),      # sum params (1+2) and push result on the stack
                
                SET(4),
                
                SET('param1'),
                SET(5),
                CREATETUPLE(2),
                
                CALL_NATIVE(fun_sum, 2,1),        # Execute function with parameters on the stack
            ]

            vm = vm_create()

            vm_run_all_threads(vm, program)
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['regstack'][0] == 12 )

        '''
        def test_2_jump(self): 

            program = [
                PASS(),       # 0
                JUMP(3),      # 1
                PASS(),       # 2
                PASS(),       # 3
            ]

            vm = vm_create()
            #vm_init(vm, program)
            
            vm_run_all_threads(vm, program)
            
            print(vm['threads'])
            
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['_stats']['op_count'] == 3)

        def test_2_jump2(self): 

            program = [
                JUMP(2),      # 1
                PASS(),       # 0
            ]
            
            vm = vm_create()

            with self.assertRaises(VMException):
                #vm_init(vm, program)
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

            vm = vm_create()
            #vm_init(vm, program)

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
         
            vm = vm_create()
            #vm_init(vm, program)

            vm_run_all_threads(vm, program)
                
            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]['timer_clock'] == 666)
    '''
    
    '''
        def test_5_input_match(self): 

            program = [
                SET('a'),
                INPUT(None),  # 1
            ]
         
            vm = VM_STATE()
            #vm_init(vm, program)

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
            #vm_init(vm, program)

            vm_set_input(vm, 'b')
            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertFalse( vm['threads'][0]['r0'] == 1 )


        def test_6_1_pushstack(self): 

            program = [
                STACKPUSHV(666),  # 1
            ]
         
            vm = VM_STATE()
            #vm_init(vm, program)

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
            #vm_init(vm, program)

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
            #vm_init(vm, program)

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
            #vm_init(vm, program)

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
            #vm_init(vm, program)

            vm_run_all_threads(vm, program)

            self.assertTrue( vm_is_finished(vm) )
            self.assertTrue( vm['threads'][0]["r0"] == 'd' )
    '''

    unittest.main()
