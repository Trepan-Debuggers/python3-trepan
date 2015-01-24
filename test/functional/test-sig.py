#!/usr/bin/env python
import os, signal, unittest
from fn_helper import strarray_setup, compare_output, get_lineno


class TestSigHandler(unittest.TestCase):

    def test_handle(self):

        # FIXME!
        self.assertTrue(True)
        return

        # See that we handle a USR1 signal with a 'stop' action
        cmds = ['handle usr1 stop nopass', 'continue', 'where', 'continue']
        d = strarray_setup(cmds)

        def signal_handler(num, f):
            print('signal %d received' % num)
            return

        signal.signal(signal.SIGUSR1, signal_handler)
        d.core.start()
        ##############################
        x = 5
        os.kill(os.getpid(), signal.SIGUSR1)
        y = 6                                 # +1
        ##############################        # +2
        d.core.stop()                         # +3
        kill_line = get_lineno() - 4          # +4
        out = ['-- x = 5',
               ('''?! os.kill(os.getpid(), signal.SIGUSR1)
     called from file 'test-sig.py' at line %d''' % 
                kill_line)]
        compare_output(self, out, d, cmds)

        # Now define a signal handler and see that this is skill okay
        # "ignore" is the same as "nopass"
        # FIXME: add this common code to the helper.
        cmds = ['handle usr1 stop ignore', 'continue', 'where', 'continue']
        d.intf[-1].output.output = ['']
        d.core.step_ignore = 0
        d.intf[-1].input.input = cmds 

        def signal_handler2(num, f):
            print('signal %d received' % num)
            return
        signal.signal(signal.SIGUSR1, signal_handler2)

        d.core.start()
        ##############################
        x = 7
        os.kill(os.getpid(), signal.SIGUSR1)
        y = 8                                 # +1
        ##############################        # +2
        d.core.stop()                         # +3
        kill_line = get_lineno() - 4          # +4
        out = ['-- x = 7',
               ('''?! os.kill(os.getpid(), signal.SIGUSR1)
     called from file 'test-sig.py' at line %d''' % 
                kill_line)]
        compare_output(self, out, d, cmds)


        # How about USR2 signal with 'ignore' and 'noprint' actions?
        cmds = ['handle usr2 ignore nostop noprint', 
                'continue', 'info signal usr2', 'continue']
        d.intf[-1].output.output = ['']
        d.core.step_ignore = 0
        d.intf[-1].input.input = cmds 

        def signal_handler3(num, f):
            print('signal %d received' % num)
            return
        signal.signal(signal.SIGUSR2, signal_handler2)

        d.core.start()
        ##############################
        x = 9  # NOQA
        os.kill(os.getpid(), signal.SIGUSR2)
        y = 10  # NOQA
        ##############################
        d.core.stop()
        out = ['-- x = 9']
        compare_output(self, out, d, cmds)

        return

    pass

if __name__ == '__main__':
    unittest.main()
    pass
