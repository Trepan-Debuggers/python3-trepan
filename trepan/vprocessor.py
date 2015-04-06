# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2010, 2012-2013, 2015 Rocky Bernstein <rocky@gnu.org>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
NotImplementedMessage = "This method must be overriden in a subclass"

from pygments.console import colorize

__all__ = ['Processor']


class Processor:
    """A processor is the thing that handles the events that come to
    the debugger.  It has it's own I/O mechanism and a way to handle
    the events.
    """
    def __init__(self, core_obj):
        self.core = core_obj
        self.debugger = core_obj.debugger
        return

    # Note for errmsg, msg, and msg_nocr we don't want to simply make
    # an assignment of method names like self.msg = self.intf.msg,
    # because we want to allow the interface (intf) to change
    # dynamically. That is, the value of self.debugger may change
    # in the course of the program and if we made such an method assignemnt
    # we wouldn't pick up that change in our self.msg
    def errmsg(self, message, opts={}):
        """ Convenience short-hand for self.intf[-1].errmsg """
        if 'plain' != self.debugger.settings['highlight']:
            message = colorize('standout', message)
            pass
        return(self.intf[-1].errmsg(message))

    def msg(self, msg, opts={}):
        """ Convenience short-hand for self.debugger.intf[-1].msg """
        return(self.intf[-1].msg(msg))

    def msg_nocr(self, msg, opts={}):
        """ Convenience short-hand for self.debugger.intf[-1].msg_nocr """
        return(self.intf[-1].msg_nocr(msg))

    def event_processor(self, frame, event, arg):
        raise NotImplementedError(NotImplementedMessage)

    def rst_msg(self, text, opts={}):
        """Convert ReStructuredText and run through msg()"""
        from trepan.lib.format import rst_text
        text = rst_text(text,
                        'plain' == self.debugger.settings['highlight'],
                        self.debugger.settings['width'])
        return self.msg(text)

    def section(self, message, opts={}):
        if 'plain' != self.settings('highlight'):
            message = colorize('bold', message)
            pass
        return self.msg(message, opts)

    def settings(self, setting):
        return self.core.debugger.settings[setting]
    pass
