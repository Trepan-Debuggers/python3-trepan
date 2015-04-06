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
# """ Copyright (C) 2008, 2009, 2013 Rocky Bernstein <rocky@gnu.org> """
__import__('pkg_resources').declare_namespace(__name__)

import glob, os

# FIXME: Is it really helpful to "privatize" variable names below?
# The below names are not part of the standard pre-defined names like
# __name__ or __file__ are.

# Get the name of our directory.
__command_dir__ = os.path.dirname(__file__)

# A glob pattern that will get all *.py files but not __init__.py
__py_files__    = glob.glob(os.path.join(__command_dir__, '[a-z]*.py'))

# Take the basename of the filename and drop off '.py'. That minus the
# files in exclude_files and tha becomes the list of modules that
# commands.py will use to import
exclude_files = ['mock.py']
__modules__ = [ os.path.basename(filename[0:-3]) for
                filename in __py_files__
                if os.path.basename(filename) not in exclude_files]
__all__ =  __modules__  + exclude_files
