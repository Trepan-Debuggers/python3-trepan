#!/usr/bin/env python3
'Unit test for trepan.bytecode'
import inspect, sys, unittest

from trepan.lib import bytecode as Mcode


class TestByteCode(unittest.TestCase):

    def test_contains_make_function(self):
        def sqr(x):
            return x * x
        frame = inspect.currentframe()
        co = frame.f_code
        lineno = frame.f_lineno
        self.assertTrue(Mcode.stmt_contains_opcode(co, lineno-4,
                                                   'MAKE_FUNCTION'))
        self.assertFalse(Mcode.stmt_contains_opcode(co, lineno,
                                                    'MAKE_FUNCTION'))
        return

    def test_op_at_frame(self):
        frame = inspect.currentframe()
        IS_PYPY = '__pypy__' in sys.builtin_module_names
        if IS_PYPY:
            self.assertEqual('CALL_METHOD', Mcode.op_at_frame(frame))
        else:
            self.assertEqual('CALL_FUNCTION', Mcode.op_at_frame(frame))
        return

    def test_is_def_frame(self):
        # Not a "def" statement because frame is wrong spot
        frame = inspect.currentframe()
        self.assertFalse(Mcode.is_def_stmt('foo(): pass', frame))
        return

if __name__ == '__main__':
    unittest.main()
