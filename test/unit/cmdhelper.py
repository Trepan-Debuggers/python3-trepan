# -*- coding: utf-8 -*-
""" Mock classes used for testing which in turn really come from 
trepan.processor.command.mock """

import os
from import_relative import *

default   = import_relative('lib.default', '...trepan') # Default settings
mock      = import_relative('processor.command.mock', '...trepan')

dbg_setup = mock.dbg_setup
