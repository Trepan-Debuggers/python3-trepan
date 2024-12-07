# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017, 2020, 2023-2024 Rocky Bernstein
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

import inspect
import os.path as osp

import pyficache

from trepan.lib.stack import frame2file
from trepan.processor.parse.semantics import Location

INVALID_LOCATION = None


def resolve_location(proc, location):
    """Expand fields in Location namedtuple. If:
    '.':  get fields from stack
    function/module: get fields from evaluation/introspection
    location file and line number: use that
    """
    curframe = proc.curframe
    offset = None
    if location == ".":
        if not curframe:
            proc.errmsg("Don't have a stack to get location from")
            return INVALID_LOCATION
        filename = frame2file(proc.core, curframe, canonic=False)
        lineno = inspect.getlineno(curframe)
        offset = curframe.f_lasti
        return Location(filename, lineno, False, curframe.f_code, offset)

    assert isinstance(location, Location)
    is_address = location.is_address
    if proc.curframe:
        g = curframe.f_globals
        locals_dict = curframe.f_locals
    else:
        g = globals()
        locals_dict = locals()
        pass

    location_method = location.method
    filename = lineno = mod_func = None
    if location_method:
        # Validate arguments that can't be done in parsing
        if location_method == "<module>":
            filename = location.path
            if not filename:
                proc.errmsg("Can only resolve <module> if a path is given")
                return INVALID_LOCATION

            if osp.exists(filename):
                # from sys.modules, pick out those modules whose filename is "module_path".
                modules = [
                    module
                    for module in sys.modules.values()
                    if hasattr(module, "__file__") and module.__file__ == filename
                ]
                if len(modules):
                    # There is at least one matching module. (They all
                    # should be the same.)
                    mod_func = modules[0]
                else:
                    proc.errmsg("Cannot resolve <module> from a path %s" % filename)
                    return INVALID_LOCATION

        if mod_func is None:
            # [1] DRY similar code [2] below
            msg = "Object %s is not known yet as a function, " % location_method
            try:
                mod_func = eval(location_method, g, locals_dict)
            except Exception:
                proc.errmsg(msg)
                split_names = location_method.split(".")
                if len(split_names) > 1:
                    proc.msg('Try importing %s?' % ".".join(split_names[:-1]))

                return INVALID_LOCATION

            try:
                # Check if the converted string is a function or instance
                # method.  We don't want to test on attributes and not use
                # `inspect.isfunction()` so that we can accommodate
                # trepan-xpy() which has it's own type of compatible
                # Function, that would fail an `inspect.isfunction()`
                # test.
                if hasattr(mod_func, "__code__") or hasattr(mod_func, "im_func"):
                    offset = -1
                else:
                    proc.errmsg(msg)
                    return INVALID_LOCATION
            except Exception:
                proc.errmsg(msg)
                return INVALID_LOCATION
            filename = proc.core.canonic(mod_func.__code__.co_filename)

            # FIXME: we may want to check lineno and
            # respect that in the future
            lineno = mod_func.__code__.co_firstlineno

    elif location.path:
        filename = proc.core.canonic(location.path)
        lineno = location.line_number
        mod_func = None
        msg = "%s is not known as a file" % location.path
        if not osp.isfile(filename):
            # See if argument is a module
            try:
                mod_func = eval(location.path, g, locals_dict)
            except Exception:
                msg = (
                    "Don't see '%s' as a existing file or as an module" % location.path
                )
                proc.errmsg(msg)
                return INVALID_LOCATION
            pass
            is_address = location.is_address
            if inspect.ismodule(mod_func):
                if hasattr(mod_func, "__file__"):
                    filename = pyficache.resolve_name_to_path(mod_func.__file__)
                    filename = proc.core.canonic(filename)
                    if not lineno:
                        # use first line of module file
                        lineno = 1
                        offset = 0
                        is_address = False
                    return Location(filename, lineno, is_address, mod_func, offset)
                else:
                    msg = "module '%s' doesn't have a file associated with it"

            proc.errmsg(msg)
            return INVALID_LOCATION
        maxline = pyficache.maxline(filename)
        if maxline and lineno > maxline:
            # NB: we use the gdb wording here
            proc.errmsg(
                "Line number %d out of range; %s has %d lines."
                % (lineno, filename, maxline)
            )
            return INVALID_LOCATION
        offset = location.offset
        if offset is None:
            code_info, lineinfo = pyficache.code_line_info(filename, lineno)
            if lineinfo:
                offset = lineinfo[0].offsets[0]
                mod_func = code_info[lineinfo[0].name]
            else:
                return INVALID_LOCATION

    elif location.line_number:
        if curframe is None:
            proc.errmsg("Current frame is not set")
            return INVALID_LOCATION
        filename = frame2file(proc.core, curframe, canonic=False)
        lineno = location.line_number
        is_address = location.is_address
        mod_func = curframe.f_code
        if offset is None:
            code_info, lineinfo = pyficache.code_line_info(filename, lineno, include_offsets=True)
            if lineinfo:
                offset = lineinfo[0].offsets[0]
                mod_func_name = lineinfo[0].name
                if mod_func.co_name != mod_func_name:
                    print("FIXME: resolve_location needs update to pick out function")
                pass
            else:
                return INVALID_LOCATION
    elif location.offset is not None:
        filename = frame2file(proc.core, curframe, canonic=False)
        is_address = True
        lineno = None
        mod_func = None
        offset = location.offset
    return Location(filename, lineno, is_address, mod_func, offset)


def resolve_address_location(proc, location):
    """Expand fields in Location namedtuple. If:
    '.':  get fields from stack
    function/module: get fields from evaluation/introspection
    location file and line number: use that
    """
    curframe = proc.curframe
    if location == ".":
        filename = frame2file(proc.core, curframe, canonic=False)
        offset = curframe.f_lasti
        is_address = True
        return Location(filename, offset, False, None, offset)

    assert isinstance(location, Location)
    is_address = True
    if proc.curframe:
        g = curframe.f_globals
        locals_dict = curframe.f_locals
    else:
        g = globals()
        locals_dict = locals()
        pass
    if location.method:
        # Validate arguments that can't be done in parsing
        filename = offset = None
        msg = "Object %s is not known yet as a function, " % location.method
        try:
            mod_func = eval(location.method, g, locals_dict)
        except Exception:
            split_names = location_method.split(".")
            if len(split_names) > 1:
                proc.msg('Try importing %s?' % ".".join(split_names[:-1]))
            proc.errmsg(msg)
            return INVALID_LOCATION

        try:
            # Check if the converted string is a function or instance method
            if inspect.isfunction(mod_func) or hasattr(mod_func, "im_func"):
                pass
            else:
                proc.errmsg(msg)
                return INVALID_LOCATION
        except Exception:
            proc.errmsg(msg)
            return INVALID_LOCATION
        filename = proc.core.canonic(mod_func.func_code.co_filename)
        # FIXME: we may want to check offset and
        # respect that in the future
        offset = 0
    elif location.path:
        filename = proc.core.canonic(location.path)
        offset = location.line_number
        is_address = location.is_address
        mod_func = None
        msg = "%s is not known as a file" % location.path
        if not osp.isfile(filename):
            # See if argument is a module
            try:
                mod_func = eval(location.path, g, locals_dict)
            except Exception:
                msg = (
                    "Don't see '%s' as a existing file or as an module" % location.path
                )
                proc.errmsg(msg)
                return INVALID_LOCATION
            pass
            is_address = location.is_address
            if inspect.ismodule(mod_func):
                if hasattr(mod_func, "__file__"):
                    filename = pyficache.resolve_name_to_path(mod_func.__file__)
                    filename = proc.core.canonic(filename)
                    if not offset:
                        # use first offset of module file
                        offset = 0
                        is_address = True
                    return Location(filename, offset, is_address, mod_func, offset)
                else:
                    msg = (
                        "module '%s' doesn't have a file associated with it"
                        % location.path
                    )

            proc.errmsg(msg)
            return INVALID_LOCATION
        maxline = pyficache.maxline(filename)
        if maxline and offset > maxline:
            # NB: we use the gdb wording here
            proc.errmsg(
                "Line number %s out of range; %s has %s lines."
                % (offset, filename, maxline)
            )
            return INVALID_LOCATION
    elif location.line_number is not None:
        filename = frame2file(proc.core, curframe, canonic=False)
        offset = location.line_number
        is_address = location.is_address
        mod_func = proc.list_object
    else:
        proc.errmsg(
            "Location %s doesn't have enough information for a location." % location
        )
        return INVALID_LOCATION

    return Location(filename, offset, is_address, mod_func, offset)


# Demo it
if __name__ == "__main__":
    import sys

    from trepan.processor.cmdproc import CommandProcessor
    from trepan.processor.command.mock import MockDebugger

    d = MockDebugger()
    cmdproc = CommandProcessor(d.core)
    frame = cmdproc.frame = sys._getframe()
    cmdproc.setup()
    location = Location(__file__, frame.f_lineno, False, None, frame.f_lasti)
    print(resolve_location(cmdproc, location))
    location = Location(__file__, None, False, "resolve_location", frame.f_lasti)
    print(resolve_location(cmdproc, location))
    location = Location(__file__, None, False, "<module>", frame.f_lasti)
    print(resolve_location(cmdproc, location))
