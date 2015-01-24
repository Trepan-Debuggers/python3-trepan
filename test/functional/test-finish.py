#!/usr/bin/env python3
import unittest
from fn_helper import compare_output, strarray_setup


class TestFinish(unittest.TestCase):
    def test_finish_same_level(self):
        print("test ", __file__, "finish_same_level skipped")
        return

        cmds = ['step 5', 'finish', 'continue']
        d = strarray_setup(cmds)
        d.core.start()

        def bar():
            x = 3  # NOQA
            return 1

        def foo():
            bar()
            x = 2  # NOQA
            return 5
        foo()
        d.core.stop()
        out = ['-- def foo():',
               '-- x = 3',
               '<- return 1',
               '<- return 5',  # FIXME this isn't right
               ]
        compare_output(self, out, d, cmds)

    # def test_finish_with_up(self):
    #     cmds = ['step 5', 'up', 'finish 2', 'continue']
    #     d = strarray_setup(cmds)
    #     d.core.start()
    #     def bar():
    #         x = 3
    #         return 1
    #     def foo():
    #         bar()
    #         x = 2
    #         return 5
    #     foo()
    #     d.core.stop()
    #     out = ['-- def foo():',
    #            '-- x = 3',
    #            '-- bar()',
    #            '<- return 5',
    #            ]
    #     compare_output(self, out, d, cmds)
    #     return

    pass

if __name__ == '__main__':
    unittest.main()
