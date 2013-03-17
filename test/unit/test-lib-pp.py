#!/usr/bin/env python
'Unit test for trepan.lib.pp'
import inspect, os, sys, unittest
from import_relative import import_relative

Mpp = import_relative('lib.pp', '...trepan')

class TestLibPrint(unittest.TestCase):

    def setUp(self):
        self.msgs = []
        return

    def msg_nocr(self, msg):
        if len(self.msgs) > 0:
            self.msgs[-1] += msg
        else:
            self.msgs += msg
            pass
        return
    def msg(self, msg):
        self.msgs += [msg]
        return

    def test_lib_pprint_simple_array(self):
        def msg_nocr(self, m):
            sys.stdout.write(m)
            return
        import sys
        def msg(self, m): print(m)
        data = [i for i in range(50)]
        Mpp.pprint_simple_array(data, 50, self.msg_nocr, self.msg)
        self.assertEqual(
            ['[ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11', '',
             ' 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23',
             ' 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35',
             ' 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47',
             ' 48, 49]'],
            self.msgs)
        return

    pass

if __name__ == '__main__':
    unittest.main()
