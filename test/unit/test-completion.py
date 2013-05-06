#!/usr/bin/env python3
'Unit test for debugger command completion'

import unittest
from import_relative import import_relative
Mdebugger = import_relative('debugger', '...trepan')

line_buffer = ''
def get_line_buffer():
    return line_buffer

class TestCompletion(unittest.TestCase):

    def run_complete(self, line):
        global line_buffer
        line_buffer = line
        results = []
        i = 0
        # from trepan.api import debug; debug()
        got = self.dbgr.complete(line, i)
        while (got):
            results.append(got)
            i += 1
            got = self.dbgr.complete(line, i)
            pass
        return results

    def test_completion(self):

        self.dbgr = Mdebugger.Trepan()

        for line, expect_completion in [
                # FIXME:
                ['set basename ', ['off', 'on']],
                ['where', ['where']],  # Single alias completion
                ['sho', ['show']],  # Simple single completion
                ['un', ['unalias', 'undisplay']],  # Simple multiple completion
                ['show', ['show']], # Completion when word is complete
                ['python ', []],        # Don't add anything - no more
                ['set basename o', ['off', 'on']],
                ['set basename of', ['off']],

                # Multiple completion on two words
                ['set auto', ['autoeval', 'autolist', 'autopython']],

                # ['set auto eval ', '', ['off', 'on']], # Many 3-word completions
                # ['set auto ', ['eval', 'irb', 'list']], # Many two-word completions
                # ['set auto e', ['eval']],
                # ['disas', ['disassemble']], # Another single completion
                # ['help syn', ['syntax']],
                # ## FIXME:
                # ## ['help syntax co', ['command']],
                # ['help br', ['break', 'breakpoints']],
                ]:
            got = self.run_complete(line)
            self.assertEqual(expect_completion, got,
                             "Completion of '%s', expecting %s, got %s" %
                             (line, expect_completion, got))
            pass
        got = self.run_complete('')
        self.assertTrue(len(got) > 30,
                        'Initial completion should return more than 30 commands')
        return
    pass

if __name__ == '__main__':
    unittest.main()
    pass
