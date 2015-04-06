import sys

import trepan.inout.stringarray
from trepan import debugger as Mdebugger
from trepan.inout import stringarray as Mstringarray


def strarray_setup(debugger_cmds):
    ''' Common setup to create a debugger with stringio attached '''
    stringin                = Mstringarray.StringArrayInput(debugger_cmds)
    stringout               = Mstringarray.StringArrayOutput()
    d_opts                  = {'input' : stringin,
                               'output': stringout}
    d                       = Mdebugger.Trepan(d_opts)
    d.settings['basename']  = True
    d.settings['different'] = False
    d.settings['autoeval']  = False
    d.settings['highlight'] = 'plain'
    return d

import re
trepan_prompt = re.compile(r'^.. \d+.*\n\(trepan3k(:.+)?\) ')
trepan_loc    = re.compile(r'^\(.+:\d+\): ')


def filter_line_cmd(a):
    '''Return output with source lines prompt and command removed'''
    # Remove extra leading spaces.
    # For example:
    # -- 42         y = 5
    # becomes
    # -- y = 5
    a1 = [re.sub(r'^(..) \d+\s+', r'\1 ', s) for s in a
         if re.match(r'^.. \d+\s+', s)]
    # Remove debugger prompts
    # For example:
    #  (trepan3k)
    a2 = [re.sub(r'\n\(trepan3k\) .*', '', s) for s in a1]

    # Remove locations (test-next.py:41): test_next_between_fn
    a3 = [re.sub(r'\n\(.*:\d+\):.*', '', s) for s in a2]
    return a3


def get_lineno():
    """Return the caller's line number"""
    caller = sys._getframe(1)
    return caller.f_lineno


def compare_output(obj, right, d, debugger_cmds):
    got = filter_line_cmd(d.intf[-1].output.output)
    if got != right:
        for i in range(len(got)):
            if i < len(right) and got[i] != right[i]:
                print("! ", got[i])
            else:
                print("  ", got[i])
                pass
            pass
        print('-' * 10)
        for i in range(len(right)):
            if i < len(got) and got[i] != right[i]:
                print("! ", right[i])
            else:
                print("  ", right[i])
                pass
            pass
        pass
    obj.assertEqual(right, got)
    return

# Demo it
if __name__=='__main__':
    print(get_lineno())
    pass
