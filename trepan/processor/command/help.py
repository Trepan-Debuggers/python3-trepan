# -*- coding: utf-8 -*-
#   Copyright (C) 2009, 2012-2013, 2015 Rocky Bernstein
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.
import glob, os, re

# Our local modules
from trepan.processor.command import base_cmd as Mbase_cmd
from trepan.processor import cmdproc as Mcmdproc
from trepan.lib import complete as Mcomplete
from trepan import misc as Mmisc


categories = {
    'breakpoints' : 'Making the program stop at certain points',
    'data'        : 'Examining data',
    'files'       : 'Specifying and examining files',
    'running'     : 'Running the program',
    'status'      : 'Status inquiries',
    'support'     : 'Support facilities',
    'stack'       : 'Examining the call stack',
    'syntax'      : 'Debugger command syntax'
    }

class HelpCommand(Mbase_cmd.DebuggerCommand):
    """**help** [*command* [*subcommand*]|*expression*]

Without argument, print the list of available debugger commands.

When an argument is given, it is first checked to see if it is command
name.

If the argument is an expression or object name, you get the same
help that you would get inside a Python shell running the built-in
*help()* command.

If the environment variable *$PAGER* is defined, the file is
piped through that command.  You'll notice this only for long help
output.

Some commands like `info`, `set`, and `show` can accept an
additional subcommand to give help just about that particular
subcommand. For example `help info line` give help about the
info line command.

See also:
---------

`examine` and `whatis`.
"""
    aliases       = ('?',)
    category      = 'support'
    min_args      = 0
    max_args      = None
    name          = os.path.basename(__file__).split('.')[0]
    need_stack    = False
    short_help    = 'Print commands or give help for command(s)'
    HELP_DIR      = os.path.join(os.path.dirname(__file__), 'help')
    RST_EXTENSION = '.rst'

    def complete(self, prefix):
        proc_obj = self.proc
        matches = Mcomplete.complete_token(list(categories.keys())
                                           + ['*', 'all'] +
                                           list(proc_obj.commands.keys()),
                                           prefix)
        aliases = Mcomplete.complete_token_filtered(proc_obj.aliases, prefix,
                                                    matches)
        return sorted(matches + aliases)

    def run(self, args):
        # It does not make much sense to repeat the last help
        # command. Also, given that 'help' uses PAGER, the you may
        # enter an extra CR which would rerun the (long) help command.
        self.proc.last_command=''

        if len(args) > 1:
            cmd_name = args[1]
            if cmd_name == '*':
                self.section("List of all debugger commands:")
                m = self.columnize_commands(list(self.proc.commands.keys()))
                self.msg_nocr(m)
                return
            elif cmd_name == 'aliases':
                self.show_aliases()
                return
            elif cmd_name == 'macros':
                self.show_macros()
                return
            elif cmd_name == 'syntax':
                self.show_command_syntax(args)
                return
            elif cmd_name in list(categories.keys()):
                self.show_category(cmd_name, args[2:])
                return

            command_name = Mcmdproc.resolve_name(self.proc, cmd_name)
            if command_name:
                instance = self.proc.commands[command_name]
                if hasattr(instance, 'help'):
                    return instance.help(args)
                else:
                    doc = instance.__doc__ or instance.run.__doc__
                    doc = doc.rstrip('\n')
                    self.rst_msg(doc.rstrip("\n"))
                    aliases = [key for key in self.proc.aliases
                               if command_name == self.proc.aliases[key]]
                    if len(aliases) > 0:
                        self.msg('')
                        msg = Mmisc.wrapped_lines('Aliases:',
                                                  ', '.join(aliases) + '.',
                                                  self.settings['width'])
                        self.msg(msg)
                        pass
                    pass
            else:
                cmds = [cmd for cmd in list(self.proc.commands.keys())
                        if re.match('^' + cmd_name, cmd) ]
                if cmds is None:
                    self.errmsg("No commands found matching /^%s/. "
                                "Try \"help\"." % cmd_name)
                elif len(cmds) == 1:
                    self.msg("Pattern '%s' matches command %s..." %
                             (cmd_name, cmds[0],))
                    args[1] = cmds[0]
                    self.run(args)
                else:
                    self.section("Command names matching /^%s/:" % cmd_name)
                    self.msg_nocr(self.columnize_commands(cmds))
                    pass
            return
        else:
            self.list_categories()
            pass

        return False

    def list_categories(self):
        """List the command categories and a short description of each."""
        self.section("Classes of commands:")
        cats = list(categories.keys())
        cats.sort()
        for cat in cats:  # Foo! iteritems() doesn't do sorting
            self.msg("  %-13s -- %s" % (cat, categories[cat]))
            pass
        final_msg = """
Type `help` followed by a class name for a list of commands in that class.
Type `help aliases` for a list of current aliases.
Type `help macros` for a list of current macros.
Type `help syntax *item*` for help on syntax *item*
Type `help *` for the list of all commands.
Type `help` *regexp* for the list of commands matching /^#{*regexp*}/
Type `help` *category* `*` for the list of all commands in category *category*
Type `help` followed by command name for full documentation.
"""
        for line in re.compile('\n').split(final_msg.rstrip('\n')):
            self.rst_msg(line)
            pass
        return

    def show_category(self, category, args):
        """Show short help for all commands in `category'."""
        n2cmd = self.proc.commands
        names = list(n2cmd.keys())
        if len(args) == 1 and args[0] == '*':
            self.section("Commands in class %s:" % category)
            cmds = [cmd for cmd in names if category == n2cmd[cmd].category]
            cmds.sort()
            self.msg_nocr(self.columnize_commands(cmds))
            return

        self.msg("%s.\n" % categories[category])
        self.section("List of commands:")
        names.sort()
        for name in names:  # Foo! iteritems() doesn't do sorting
            if category != n2cmd[name].category: continue
            self.msg("%-13s -- %s" % (name, n2cmd[name].short_help,))
            pass
        return

    def syntax_files(self):
        path = os.path.join(self.HELP_DIR, ("*%s" % self.RST_EXTENSION))
        files = glob.glob(path)
        return [os.path.basename(name).split('.')[0] for
                name in files]

    def show_aliases(self):
        self.section('All alias names:')
        m = self.columnize_commands(list(sorted(self.proc.aliases.keys())))
        self.msg_nocr(m)

    def show_macros(self):
        self.section('All macro names:')
        m = self.columnize_commands(list(sorted(self.proc.macros.keys())))
        self.msg_nocr(m)

    def init_syntax_summary_help(self):
        self.syntax_summary_help = {}
        self.syntax_help = {}
        for name in self.syntax_files():
            path = os.path.join(self.HELP_DIR, "%s%s" %
                                (name, self.RST_EXTENSION))
            self.syntax_help[name] = ''.join(open(path).
                                             readlines())
            self.syntax_summary_help[name] = open(path).\
                                             readline().strip()
            pass
        return

    def show_command_syntax(self, args):
        if not hasattr(self, 'syntax_summary_help'):
            self.init_syntax_summary_help()
            pass
        if len(args) == 2 or len(args) == 3 and args[2] == '*':
            self.section("List of syntax help")
            for name, help in self.syntax_summary_help.items():
                self.msg("  %-8s -- %s" % (name, help))
                pass
        else:
            for name in args[2:]:
                if name in self.syntax_files():
                    self.rst_msg(self.syntax_help[name])
                else:
                    self.errmsg("No syntax help for %s" % name)
                pass
            pass
        return
    pass


if __name__ == '__main__':
    from trepan.processor.command import mock
    d, cp = mock.dbg_setup()
    command = HelpCommand(cp)
    # print('-' * 20)
    # command.run(['help'])
    # print('-' * 20)
    # command.run(['help', '*'])
    # print('-' * 20)
    # command.run(['help', 'quit'])
    # print('-' * 20)
    # command.run(['help', 'stack'])
    # print('-' * 20)
    # command.run(['help', 'breakpoints'])
    # print('-' * 20)
    # command.run(['help', 'breakpoints', '*'])
    # print('-' * 20)
    # command.run(['help', 'c.*'])
    # print('-' * 20)
    command.show_command_syntax(['help', 'syntax'])
    command.show_command_syntax(['help', 'syntax', 'command'])
    pass
