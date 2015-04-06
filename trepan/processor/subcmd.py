# -*- coding: utf-8 -*-
#   Copyright (C) 2006-2010, 2013-2015 Rocky Bernstein
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Handles gdb-like subcommand processing."""


class Subcmd:
    """Gdb-like subcommand handling """
    def __init__(self, name, cmd_obj):
        self.name    = name
        self.cmd_obj = cmd_obj
        self.subcmds = {}
        self.cmdlist = []
        return

    def lookup(self, subcmd_prefix):
        """Find subcmd in self.subcmds"""
        for subcmd_name in list(self.subcmds.keys()):
            if subcmd_name.startswith(subcmd_prefix) \
               and len(subcmd_prefix) >= \
               self.subcmds[subcmd_name].__class__.min_abbrev:
                return self.subcmds[subcmd_name]
            pass
        return None

    def short_help(self, subcmd_cb, subcmd_name, label=False):
        """Show short help for a subcommand."""
        entry = self.lookup(subcmd_name)
        if entry:
            if label:
                prefix = entry.name
            else:
                prefix = ''
                pass
            if hasattr(entry, 'short_help'):
                if prefix: prefix += ' -- '
                self.cmd_obj.msg(prefix + entry.short_help)
                pass
            pass
        else:
            self.undefined_subcmd("help", subcmd_name)
            pass
        return

    def add(self, subcmd_cb):
        """Add subcmd to the available subcommands for this object.
        It will have the supplied docstring, and subcmd_cb will be called
        when we want to run the command. min_len is the minimum length
        allowed to abbreviate the command. in_list indicates with the
        show command will be run when giving a list of all sub commands
        of this object. Some commands have long output like "show commands"
        so we might not want to show that.
        """
        subcmd_name = subcmd_cb.name
        self.subcmds[subcmd_name] = subcmd_cb

        # We keep a list of subcommands to assist command completion
        self.cmdlist.append(subcmd_name)

    def run(self, subcmd_name, arg):
        """Run subcmd_name with args using obj for the environent"""
        entry=self.lookup(subcmd_name)
        if entry:
            entry['callback'](arg)
        else:
            self.cmdproc.undefined_cmd(entry.__class__.name, subcmd_name)
            pass
        return

    # Note: format of help is compatible with ddd.
    def help(self, *args):
        """help for subcommands."""

        print(args)
        subcmd_prefix = args[0]
        if not subcmd_prefix or len(subcmd_prefix) == 0:
            self.msg(self.doc)
            self.msg("""
List of %s subcommands:
""" % (self.name))
            for subcmd_name in self.list():
                self._subcmd_helper(subcmd_name, self, True, True)
            return

        entry = self.lookup(subcmd_prefix)
        if entry and hasattr(entry, 'help'):
            entry.help(args)
        else:
            self.cmd_obj.errmsg("Unknown 'help %s' subcommand %s"
                                % (self.name, subcmd_prefix))

    def list(self):
        l = list(self.subcmds.keys())
        l.sort()
        return l

    def undefined_subcmd(self, cmd, subcmd):
        """Error message when a subcommand doesn't exist"""
        self.cmd_obj.errmsg('Undefined "%s" command: "%s". Try "help".' %
                         (cmd, subcmd,))
        return
    pass

# When invoked as main program, invoke the debugger on a script
if __name__ == '__main__':

    from trepan.processor.command import mock as Mmock
    from trepan.processor.command import base_cmd as Mbase_cmd

    class TestCommand(Mbase_cmd.DebuggerCommand):
        '''Doc string for testing'''

        category = 'data'
        min_args = 0
        max_args = 5
        name = 'test'

        def __init__(self):
            self.name  = 'test'
            return

        def run(self, args): print('test command run')

    class TestTestingSubcommand:
        '''Doc string for test testing subcommand'''

        def __init__(self):
            self.name  = 'testing'
            return

        short_help = 'This is short help for test testing'
        min_abbrev = 4
        in_list    = True

        def run(self, args): print('test testing run')
        pass

    d = Mmock.MockDebugger()
    testcmd    = TestCommand()
    testcmd.debugger = d
    testcmd.proc     = d.core.processor
    testcmdMgr = Subcmd('test', testcmd)
    testsub = TestTestingSubcommand()
    testcmdMgr.add(testsub)

    for prefix in ['tes', 'test', 'testing', 'testing1']:
        x = testcmdMgr.lookup(prefix)
        if x: print(x.name)
        else: print('None')
        pass

    testcmdMgr.short_help(testcmd, 'testing')
    testcmdMgr.short_help(testcmd, 'test', True)
    testcmdMgr.short_help(testcmd, 'tes')
    print(testcmdMgr.list())
    testsub2 = TestTestingSubcommand()
    testsub2.name = 'foobar'
    testcmdMgr.add(testsub2)
    print(testcmdMgr.list())
    pass
