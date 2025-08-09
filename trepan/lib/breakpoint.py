# -*- coding: utf-8 -*-
#   Copyright (C) 2015, 2017, 2020, 2024-2025 Rocky Bernstein <rocky@gnu.org>
"""Breakpoints as used in a debugger.

This code is a rewrite of the stock python bdb.Breakpoint"""

__all__ = ["BreakpointManager", "Breakpoint"]

import os.path as osp
from collections import defaultdict
from types import CodeType, ModuleType
from typing import Optional
from xdis import load_module


class Breakpoint:
    """Breakpoint class implements temporary breakpoints, ignore
    counts, disabling and (re)-enabling breakpoints and breakpoint
    conditionals.

    When matching an offset, if offset is None, the offset value is not
    considered in a match. If offset is -1, we are at a "call" event;
    the first offset in bytecode is 0.
    """

    def __init__(
        self,
        number,
        filename,
        line,
        temporary=False,
        condition=None,
        code=None,
        offset=None,
    ):
        self.offset = offset
        self.condition = condition
        self.enabled = True

        self.filename = filename
        if filename:
            self.filename = osp.realpath(filename)

        # Needed if funcname is not None.
        self.func_first_executable_line = None
        self.code = code

        # Number of time breakpoint has been hit
        self.hits = 0

        # Number of times to ignore breakpoint before stopping
        self.ignore = 0

        self.line = line
        self.number = number

        # Delete breakpoint after hitting it.
        self.temporary = temporary
        return

    def __str__(self):
        if self.temporary:
            disp = "del  "
        else:
            disp = "keep "
        if self.enabled:
            disp = disp + "yes  "
        else:
            disp = disp + "no   "
        if self.offset is None:
            offset_str = " any"
        else:
            offset_str = "%4d" % self.offset
        if self.offset is None:
            offset_str = " any"
        else:
            offset_str = "%4d" % self.offset
        if self.line is None:
            line_str = ""
        else:
            line_str = ":%d" % self.line

        msg = "%-4dbreakpoint   %s %s at %s%s" % (
            self.number,
            disp,
            offset_str,
            self.filename,
            line_str,
        )
        if self.condition:
            msg += f"\n\tstop only if {self.condition}"
        if self.ignore:
            msg += f"\n\tignore next {self.ignore} hits"
        if self.hits:
            ss = "" if self.hits > 1 else "s"
            msg += f"\n\tbreakpoint already hit {self.hits} time{ss}"
        return msg

    def enable(self):
        self.enabled = True
        return self.enabled

    def disable(self):
        self.enabled = False
        return self.enabled

    def icon_char(self) -> str:
        """Return a one-character "icon" giving the state of the breakpoint
        't': temporary breakpoint
        'B': enabled breakpoint
        'b': disabled breakpoint
        """
        if self.temporary:
            return "t"
        elif self.enabled:
            return "B"
        return "b"

    pass  # end of Breakpoint class


class BreakpointManager:
    """Manages the list of Breakpoints.

    Breakpoints are indexed by number in the `bpbynumber' list, and
    through a (file,line) tuple which is a key in the `bplist'
    dictionary. If the breakpoint is a function it is in `code_list' as
    well.  Note there may be more than one breakpoint per line which
    may have different conditions associated with them.
    """

    def __init__(self):

        # self.reset()

        # The below duplicates self.reset(). However we include it here,
        # to assist linters which as of 2014 largely do not grok attributes of
        # class unless it is put inside __init__

        self.bpbynumber: list = [None]
        self.bplist = defaultdict(list)
        self.code_list = defaultdict(list)
        return

    def bpnumbers(self):
        """Returns a list of strings of breakpoint numbers"""
        return ["%d" % bp.number for bp in self.bpbynumber if bp is not None]

    def get_breakpoint(self, i) -> tuple:
        if isinstance(i, str):
            try:
                i = int(i)
            except ValueError:
                return (False, f"Breakpoint value {i!r} is not a number.", None)
            pass
        if 1 == len(self.bpbynumber):
            return (False, "No breakpoints set.", None)
        elif i >= len(self.bpbynumber) or i <= 0:
            return (
                False,
                "Breakpoint number %d out of range 1..%d."
                % (i, len(self.bpbynumber) - 1),
                None,
            )
        bp = self.bpbynumber[i]
        if bp is None:
            return (False, "Breakpoint %d previously deleted." % i, None)
        return (True, None, bp)

    def add_breakpoint(
        self,
        filename: Optional[str],
        lineno: Optional[int] = None,
        offset: int = -1,
        temporary: bool = False,
        condition: Optional[str] = None,
        func_or_code=None,
    ):
        """
        Add a breakpoint in ``filename`` at line number ``lineno``.
        If ``offset`` is given and not -1, then it we must also be at that offset in order to stop.
        ``temporary`` specifies whether the breakpoint will be removed once it is hit.
        `condition`` specifies that a string Python expression to be evaluated to determine
        whether the breakpoint is hit or not.
        """
        bpnum = len(self.bpbynumber)
        if filename:
            filename = osp.realpath(filename)

        assert (
            isinstance(filename, str) or func_or_code is not None
        ), "You must either supply a filename or give a line number"

        if isinstance(func_or_code, CodeType):
            code = func_or_code
        elif isinstance(func_or_code, ModuleType):
            if hasattr(func_or_code, "__cached__"):
                # FIXME: we can probably do better hooking into importlib
                # or something lower-level
                _, _, _, code, _, _, _ = load_module(
                    func_or_code.__cached__, fast_load=True, get_code=True
                )
            else:
                print(f"Don't know what to do with frozen module {func_or_code}")
                return
        elif hasattr(func_or_code, "__code__"):
            code = func_or_code.__code__
        elif hasattr(func_or_code, "f_code"):
            code = func_or_code.f_code
        else:
            print(f"Don't know what to do with {func_or_code}, {type(func_or_code)}")
            return
        brkpt = Breakpoint(bpnum, filename, lineno, temporary, condition, code, offset)

        # Build the internal lists of breakpoints
        self.bpbynumber.append(brkpt)
        self.bplist[filename, lineno].append(brkpt)
        if func_or_code and offset in [None, -1]:
            self.code_list[code].append(brkpt)
        return brkpt

    def delete_all_breakpoints(self) -> str:
        """
        Delete all breakpoints. Return a message indicating
        what was deleted.
        """
        bp_list = []
        for bp in self.bpbynumber:
            if bp:
                bp_list.append(str(bp.number))
                self.delete_breakpoint(bp)
                pass
        if not bp_list:
            return "There are no breakpoints"
        return f"Deleted breakpoints {', '.join(bp_list)}"

    def delete_breakpoint(self, bp: Breakpoint) -> bool:
        "remove breakpoint `bp'"
        bpnum = bp.number
        self.bpbynumber[bpnum] = None  # No longer in list
        index = (bp.filename, bp.line)
        if index not in self.bplist:
            return False
        self.bplist[index].remove(bp)
        if not self.bplist[index]:
            # No more breakpoints for this file:line combo
            del self.bplist[index]
        return True

    def delete_breakpoint_by_number(self, bpnum: int) -> tuple:
        "Remove a breakpoint given its breakpoint number."
        success, msg, bp = self.get_breakpoint(bpnum)
        if not success:
            return False, msg
        self.delete_breakpoint(bp)
        return (True, "")

    def en_disable_all_breakpoints(self, do_enable=True):
        "Enable or disable all breakpoints."
        bp_list = [bp for bp in self.bpbynumber if bp]
        bp_nums = []
        if do_enable:
            endis = "en"
        else:
            endis = "dis"
            pass
        if not bp_list:
            return f"No breakpoints to {endis}able"
        for bp in bp_list:
            bp.enabled = do_enable
            bp_nums.append(str(bp.number))
            pass
        return f"Breakpoints {endis}abled: {', '.join(bp_nums)}"

    def en_disable_breakpoint_by_number(self, bpnum: int, do_enable=True) -> tuple:
        "Enable or disable a breakpoint given its breakpoint number."
        success, msg, bp = self.get_breakpoint(bpnum)
        if not success:
            return success, msg
        if do_enable:
            endis = "en"
        else:
            endis = "dis"
            pass
        if bp.enabled == do_enable:
            return (
                False,
                (f"Breakpoint ({str(bpnum)!r}) previously {endis}abled"),
            )
        bp.enabled = do_enable
        return (True, "")

    def delete_breakpoints_by_lineno(self, filename: str, lineno: int):
        """Removes all breakpoints at a give filename and line number.
        Returns a list of breakpoints numbers deleted.
        """
        if (filename, lineno) not in self.bplist:
            return []
        breakpoints = self.bplist[(filename, lineno)]
        bpnums = [bp.number for bp in breakpoints]
        for bp in list(breakpoints):
            self.delete_breakpoint(bp)
        return bpnums

    def find_bp(self, filename: str, lineno: int, frame):
        """Determine which breakpoint for this file:line is to be acted upon.

        Called only if we know there is a bpt at this
        location.  Returns breakpoint that was triggered and a flag
        that indicates if it is ok to delete a temporary breakpoint.

        """
        possibles = self.bplist[filename, lineno]
        for i in range(0, len(possibles)):
            b = possibles[i]
            if not b.enabled:
                continue
            if not checkfuncname(b, frame):
                continue
            # Count every hit when bp is enabled
            b.hits += 1
            if not b.condition:
                # If unconditional, and ignoring, go on to next, else
                # break
                if b.ignore > 0:
                    b.ignore = b.ignore - 1
                    continue
                else:
                    # breakpoint and marker that's ok to delete if
                    # temporary
                    return (b, True)
            else:
                # Conditional bp.
                # Ignore count applies only to those bpt hits where the
                # condition evaluates to true.
                try:
                    val = eval(b.condition, frame.f_globals, frame.f_locals)
                    if val:
                        if b.ignore > 0:
                            b.ignore = b.ignore - 1
                            # continue
                        else:
                            return (b, True)
                    # else:
                    #   continue
                except Exception:
                    # if eval fails, most conservative thing is to
                    # stop on breakpoint regardless of ignore count.
                    # Don't delete temporary, as another hint to user.
                    return (b, False)
                pass
            pass
        return (None, None)

    def last(self):
        return len(self.bpbynumber) - 1

    def reset(self):
        """A list of breakpoints by breakpoint number.  Each entry is
        None or an instance of Breakpoint.  Index 0 is unused, except
        for marking an effective break .... see effective()."""
        self.bpbynumber = [None]

        # A list of breakpoints indexed by (file, lineno) tuple
        self.bplist = {}
        self.code_list = {}

        return

    pass  # BreakpointManager


def checkfuncname(brkpt: Breakpoint, frame):
    """
    Check whether we should break at `frame` because the frame's
    code object matches `brkpt.code`.
    """
    if not brkpt.code:
        # Breakpoint was set via line number.
        if brkpt.line != frame.f_lineno:
            # Breakpoint was set at a line with a def statement and the function
            # defined is called: don't break.
            return False
        return True

    # Breakpoint set via function code object

    if frame.f_code != brkpt.code:
        # It's not a function call, but rather execution of def statement.
        return False

    # We are in the right frame.
    if not brkpt.func_first_executable_line:
        # The function is entered for the 1st time.
        brkpt.func_first_executable_line = frame.f_lineno

    if brkpt.func_first_executable_line != frame.f_lineno:
        # But we are not at the first line number: don't break.
        return False
    return True


# Demo

if __name__ == "__main__":

    def foo(bp, bpmgr):
        frame = inspect.currentframe()
        assert frame
        print(f"Stop at bp2: {checkfuncname(bp, frame)}")
        # frame.f_lineno is constantly updated. So adjust for the
        # line difference between the add_breakpoint and the check.
        bp3 = bpmgr.add_breakpoint(__file__, 0, frame.f_lineno + 1, func_or_code=foo)
        print(f"Stop at bp3: {checkfuncname(bp3, frame)}")
        return

    def bar() -> int:
        frame = inspect.currentframe()
        assert frame is not None
        return frame.f_lasti

    bpmgr = BreakpointManager()
    print(bpmgr.last())
    line_number = foo.__code__.co_firstlineno
    bp = bpmgr.add_breakpoint(__file__, line_number, func_or_code=foo)
    assert bp
    print(bp.icon_char())
    print(bpmgr.last())
    print(repr(bp))
    print(str(bp))
    bp.disable()
    print(str(bp))
    import xdis

    bp = bpmgr.add_breakpoint(xdis.__file__, offset=0, func_or_code=xdis)
    print(bp)
    for i in 10, 1:
        status, msg = bpmgr.delete_breakpoint_by_number(i)
        print(f"Delete breakpoint {i}: {status} {msg}")
    import inspect

    frame = inspect.currentframe()
    assert bp
    print(f"Stop at bp: {checkfuncname(bp, frame)}")

    bp2 = bpmgr.add_breakpoint(None, None, -1, False, None, foo)
    foo(bp2, bpmgr)
    bp3 = bpmgr.add_breakpoint(
        __file__, line_number, 0, temporary=True, func_or_code=foo
    )
    assert bp3
    print(bp3.icon_char())
    print(bpmgr.bpnumbers())

    line_number = bar.__code__.co_firstlineno
    bp = bpmgr.add_breakpoint(__file__, line_number, 0, func_or_code=bar)
    assert bp
    filename = bp.filename
    assert filename
    line_number = bar()
    for i in range(3):
        bp = bpmgr.add_breakpoint(None, None, line_number, func_or_code=bar)
    print(bpmgr.delete_breakpoints_by_lineno(filename, line_number))
    print(bpmgr.delete_breakpoints_by_lineno(filename, line_number))
    print(bpmgr.bpnumbers())
