#!/usr/bin/env python3
'Unit test for trepan.lib.sighandler'
import signal, unittest

from trepan.lib import sighandler as Msig


class TestLibSigHandle(unittest.TestCase):

    def test_YN(self):
        for expect, b in (('Yes', True), ('No', False)):
            self.assertEqual(expect, Msig.YN(b))
            pass
        return

    def test_canonic_signame(self):
        for expect, name_num in (('SIGTERM',  '15'),
                                 ('SIGTERM', '-15'),
                                 ('SIGTERM', 'term'),
                                 ('SIGTERM', 'sigterm'),
                                 ('SIGTERM', 'TERM'),
                                 (None, '300'),
                                 (False, 'bogus')):
            self.assertEqual(expect, Msig.canonic_signame(name_num),
                             'name_num: %s' % name_num)
            pass
        pass

    def test_lookup_signame(self):
        for expect, num in (('SIGTERM', 15), ('SIGTERM', -15),
                          (None, 300)):
            self.assertEqual(expect, Msig.lookup_signame(num), "looking up %d" % num)
            pass
        return

    def test_lookup_signum(self):
        for expect, name in ((15, 'SIGTERM'), (15, 'TERM'),
                             (15, 'term'), (None, 'nothere')):
            self.assertEqual(expect, Msig.lookup_signum(name),
                             "looking up name %s" % name)
            pass
        return

    def test_lookup_signame_signum(self):
        ignore = ['ITIMER_VIRTUAL', 'ITIMER_REAL', 'ITIMER_PROF']
        for signum in range(signal.NSIG):
            signame = Msig.lookup_signame(signum)
            if signame is not None and signame not in ignore:
                self.assertEqual(signum, Msig.lookup_signum(signame),
                                 "looking up name %s" % signame)
                # Try without the SIG prefix
                self.assertEqual(signum, Msig.lookup_signum(signame[3:]))
                pass
            pass
        return

    pass

if __name__ == '__main__':
    unittest.main()
