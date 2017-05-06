#!/usr/bin/env python3
'Unit test for trepan.lib.file'
import os, stat, sys, tempfile, unittest

from trepan.lib import file as Mfile


class TestLibFile(unittest.TestCase):

    def test_lookupmodule(self):
        m, f = Mfile.lookupmodule('os.path')
        self.assertTrue(f)
        self.assertTrue(m)
        m, f = Mfile.lookupmodule(__file__)
        self.assertTrue(f)
        self.assertEqual(None, m)
        self.assertEqual((None, None), Mfile.lookupmodule('fafdsafdsa'))
        return

    if sys.platform != 'win32':
        def test_readable(self):
            self.assertFalse(Mfile.readable('fdafdsa'))
            for mode, can_read in [(stat.S_IRUSR, True),
                                   (stat.S_IWUSR, False)]:
                f = tempfile.NamedTemporaryFile()
                os.chmod(f.name, mode)
                self.assertEqual(can_read, Mfile.readable(f.name))
                f.close()
                pass
            return
        pass

    pass

if __name__ == '__main__':
    unittest.main()
