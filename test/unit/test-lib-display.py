#!/usr/bin/env python3
'Unit test for trepan.lib.display'

import inspect, unittest

from trepan.lib import display as Mdisplay


class TestLibDisplay(unittest.TestCase):

    def test_display(self):

        mgr = Mdisplay.DisplayMgr()
        self.assertEqual(mgr.list, [], "Initial list empty")
        x = 1  # NOQA
        frame = inspect.currentframe()
        disp = mgr.add(frame, 'x > 1')
        self.assertEqual(disp.__class__, Mdisplay.Display,
                         "mgr.add should return display")
        self.assertEqual(len(mgr.list), 1, "display list with one item")
        disp = mgr.add(frame, 'x')
        self.assertEqual(disp.__class__, Mdisplay.Display,
                         "mgr.add should return another display")
        self.assertEqual(len(mgr.list), 2, "display list with two items")
        self.assertEqual(mgr.delete_index(1), True, "return True on ok delete")
        self.assertEqual(mgr.delete_index(1), False,
                         "return False on no delete")
        self.assertEqual(len(mgr.list), 1, "display list again with one item")
        return

    pass

if __name__ == '__main__':
    unittest.main()
    pass
