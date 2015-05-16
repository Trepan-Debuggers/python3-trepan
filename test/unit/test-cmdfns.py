#!/usr/bin/env python3
'Unit test for trepan.processor.command.cmdfns'
import unittest

from trepan.processor import cmdfns as Mcmdfns


class TestCommandHelper(unittest.TestCase):

    def setUp(self):
        self.errors = []
        return

    def errmsg(self, msg):
        self.errors.append(msg)
        return

    def test_get_an_int(self):
        self.assertEqual(0, Mcmdfns.get_an_int(self.errmsg, '0', 'foo', 0))
        self.assertEqual(0, len(self.errors))
        self.assertEqual(6, Mcmdfns.get_an_int(self.errmsg, '6*1', 'foo', 5))
        self.assertEqual(0, len(self.errors))
        self.assertEqual(None, Mcmdfns.get_an_int(self.errmsg, '0',
                                                  '0 is too small', 5))
        self.assertEqual(1, len(self.errors))
        self.assertEqual(None, Mcmdfns.get_an_int(self.errmsg, '4+a',
                                                  '4+a is invalid', 5))
        self.assertEqual('4+a is invalid', self.errors[-1])
        return

    def test_get_int(self):
        self.assertEqual(1, Mcmdfns.get_int(self.errmsg, '1', 5))
        self.assertEqual(3, Mcmdfns.get_int(self.errmsg, '1+2', 5))
        self.assertEqual(5, Mcmdfns.get_int(self.errmsg, None, 5))
        self.assertEqual(1, Mcmdfns.get_int(self.errmsg, None))
        self.assertRaises(ValueError, Mcmdfns.get_int,
                          *(self.errmsg, 'Foo', 5))
        return

    def test_get_onoff(self):
        for arg in ('1', 'on'):
            self.assertEqual(True, Mcmdfns.get_onoff(self.errmsg, arg))
            pass
        for arg in ('0', 'off'):
            self.assertEqual(False, Mcmdfns.get_onoff(self.errmsg, arg))
            pass
        for result in (True, False):
            self.assertEqual(result, Mcmdfns.get_onoff(self.errmsg, None,
                                                       result))
            pass
        self.assertRaises(ValueError, Mcmdfns.get_onoff, *(self.errmsg,
                                                           'Foo'))
        return

    def test_want_different_line(self):
        for cmd, default, expected in [
        ('s+', False, True),
        ('s-', True,  False),
        ('s',  False, False),
        ('n',  True,  True) ]:
            self.assertEqual(expected,
                             Mcmdfns.want_different_line(cmd, default),
                             cmd)
            pass
        return
    pass

if __name__ == '__main__':
    unittest.main()
