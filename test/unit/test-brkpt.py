#!/usr/bin/env python3
'Unit test for the debugger lib breakpoint'
import re, unittest

from trepan.lib import breakpoint as Mbreakpoint


class TestBreakpoint(unittest.TestCase):

    def test_breakpoint(self):
        'Test breakpoint'
        bpmgr = Mbreakpoint.BreakpointManager()
        self.assertEqual(0, bpmgr.last())
        bp = bpmgr.add_breakpoint('foo', 10, 5)

        # FIXME:
        # self.assertFalse(not
        #                  re.search('1   breakpoint   keep yes .* at .*foo:5',
        #                            str(bp)), str(bp))
        self.assertEqual('B', bp.icon_char())
        self.assertEqual(True, bp.enabled)
        bp.disable()
        # self.assertFalse(not
        #                  re.search('1   breakpoint   keep no .* at .*foo:5',
        #                  str(bp)))
        self.assertEqual(False, bp.enabled)
        self.assertEqual('b', bp.icon_char())
        self.assertEqual(1, bpmgr.last())
        self.assertEqual((False, 'Breakpoint number 10 out of range 1..1.'),
                         bpmgr.delete_breakpoint_by_number(10))
        self.assertEqual(['1'], bpmgr.bpnumbers(),
                         "Extracting disabled breakpoint-numbers")
        self.assertEqual((True, ''), bpmgr.delete_breakpoint_by_number(1))
        self.assertEqual((False, 'Breakpoint 1 previously deleted.'),
                          bpmgr.delete_breakpoint_by_number(1))
        bp2 = bpmgr.add_breakpoint('foo', 5, 10, temporary=True)
        self.assertEqual('t', bp2.icon_char())
        self.assertEqual(['2'], bpmgr.bpnumbers(),
                         "Extracting breakpoint-numbers")

        count = 3
        for i in range(count):
            bp = bpmgr.add_breakpoint('bar', 10, 6)
        filename = bp.filename
        # self.assertEqual(count, len(bpmgr.delete_breakpoints_by_lineno(filename, 6)),
        #                  "delete_breakpoints_by_line when there are some")
        self.assertEqual(0, len(bpmgr.delete_breakpoints_by_lineno(filename, 6)),
                         "delete_breakpoints_by_line when there are none")
        self.assertNotEqual(0, len(bpmgr.bplist),
                            "There should still be some breakpoints before reset")
        bpmgr.reset()
        self.assertEqual(0, len(bpmgr.bplist),
                         "reset should remove all breakpoints")
        return

    def test_checkfuncname(self):
        'Test breakpoint.checkfuncname()'
        import inspect
        frame = inspect.currentframe()

        bpmgr = Mbreakpoint.BreakpointManager()
        bp    = bpmgr.add_breakpoint('foo', -1, 5)

        # FIXME:
        # self.assertEqual(False, Mbreakpoint.checkfuncname(bp, frame))

        def foo(bp, bpmgr):
            frame = inspect.currentframe()
            # self.assertEqual(True, Mbreakpoint.checkfuncname(bp, frame))
            # frame.f_lineno is constantly updated. So adjust for line
            # the difference between the add_breakpoint and the check.
            bp3 = bpmgr.add_breakpoint('foo', -1, frame.f_lineno+1)
            # self.assertEqual(True, Mbreakpoint.checkfuncname(bp3, frame))
            self.assertEqual(False, Mbreakpoint.checkfuncname(bp3, frame))
            return

        bp2 = bpmgr.add_breakpoint(None, None, False, None, 'foo')
        foo(bp2, bpmgr)
        return

if __name__ == '__main__':
    unittest.main()
