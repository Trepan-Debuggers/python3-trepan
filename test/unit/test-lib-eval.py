#!/usr/bin/env python3
'Unit test for trepan.lib.eval'
import unittest

from trepan.lib import eval as Meval


class TestExtractExpression(unittest.TestCase):
    def test_extract_expression(self):
        for fragment, expect in (
            ('if condition(x):',     'condition(x)'),
            ('elif is_magic(name):', 'is_magic(name)'),
            ('while expression:',    'expression'),
            ('for i in range(3):',   'range(3)'),
            ('abc = 123',            '123'),
            ('assert True',          'True'),
            ('return return_value',  'return_value'),
            ('nothing_to_be.done',   'nothing_to_be.done'), ):
            self.assertEqual(expect , Meval.extract_expression(fragment))
            pass
        pass
    pass

if __name__ == '__main__':
    unittest.main()
