#!/usr/bin/env python3
'Unit test for trepan.misc'
import unittest

from trepan import misc as Mmisc


class TestMisc(unittest.TestCase):

    def test_option_set(self):
        TEST_OPTS = {'a': True, 'b': 5, 'c': None}
        get_option = lambda key: Mmisc.option_set(opts, key, TEST_OPTS)
        opts={'d': 6, 'a': False}
        for opt, expect in [('a', False), 
                            ('b', 5),
                            ('c', None),
                            ('d', 6)]:
            self.assertEqual(expect, get_option(opt))
        opts=None
        for opt, expect in [('a', True), 
                            ('b', 5),
                            ('c', None),
                            ('d', None)]:
            self.assertEqual(expect, get_option(opt))
        pass

    def test_wrapped_msg(self):
        """Test misc.wrapped_lines()"""
        self.assertEqual('hi there', Mmisc.wrapped_lines('hi', 'there', 80))
        self.assertEqual('hi\n\tthere', Mmisc.wrapped_lines('hi', 'there', 5))
        return
    
    pass

if __name__ == '__main__':
    unittest.main()
