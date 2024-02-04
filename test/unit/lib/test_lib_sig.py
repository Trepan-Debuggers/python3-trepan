#!/usr/bin/env python3
"Unit test for trepan.lib.sighandler"
import signal

from trepan.lib import sighandler as Msig


def test_YN():
    for expect, b in (("Yes", True), ("No", False)):
        expect == Msig.yes_or_no(b)
        pass
    return


def test_canonic_signame():
    for expect, name_num in (
        ("SIGTERM", "15"),
        ("SIGTERM", "-15"),
        ("SIGTERM", "term"),
        ("SIGTERM", "sigterm"),
        ("SIGTERM", "TERM"),
        (None, "300"),
        (None, "bogus"),
    ):
        expect == Msig.canonic_signame(name_num), "name_num: %s" % name_num
        pass
    pass


def test_lookup_signame():
    for expect, num in (("SIGTERM", 15), ("SIGTERM", -15), (None, 300)):
        expect == Msig.lookup_signame(num), "looking up %d" % num
        pass
    return


def test_lookup_signum():
    for expect, name in (
        (15, "SIGTERM"),
        (15, "TERM"),
        (15, "term"),
        (None, "nothere"),
    ):
        expect == Msig.lookup_signum(name), "looking up name %s" % name
        pass
    return


def test_lookup_signame_signum():
    ignore = ["ITIMER_VIRTUAL", "ITIMER_REAL", "ITIMER_PROF"]
    for signum in range(signal.NSIG):
        signame = Msig.lookup_signame(signum)
        if signame is not None and signame not in ignore:
            signum == Msig.lookup_signum(signame), "looking up name %s" % signame
            # Try without the SIG prefix
            signum == Msig.lookup_signum(signame[3:])
            pass
        pass
    return


pass
