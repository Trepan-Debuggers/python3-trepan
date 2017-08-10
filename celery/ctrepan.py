# -*- coding: utf-8 -*-
"""
celery.contrib.trepan
=====================

Remote debugger for Celery tasks running in multiprocessing pool workers.
Inspired by celery.contrib.rdb

**Usage**

.. code-block:: python

    from celery.contrib import trepan
    from celery import task

    @task()
    def add(x, y):
        result = x + y
        trepan.debug()
        return result


**Environment Variables**

.. envvar:: CELERY_TREPAN_HOST

    Hostname to bind to.  Default is '127.0.01', which means the socket
    will only be accessible from the local host.

.. envvar:: CELERY_TREPAN_PORT

    Base port to bind to.  Default is 6899.
    The debugger will try to find an available port starting from the
    base port.  The selected port will be logged by the worker.

"""
from __future__ import absolute_import, print_function

import os
import sys
import trepan.api

__all__ = ['CELERY_TREPAN_HOST', 'CELERY_TREPAN_PORT', 'default_port',
           'RemoteCeleryTrepan', 'debugger', 'debug']

default_port = 6898

CELERY_TREPAN_HOST = os.environ.get('CELERY_TREPAN_HOST') or '127.0.0.1'
CELERY_TREPAN_PORT = int(os.environ.get('CELERY_TREPAN_PORT') or default_port)

#: Holds the currently active debugger.
_current = [None]

_frame = getattr(sys, '_getframe')

is_python3 = sys.version_info[0] == 3
if is_python3:
    trepan_client = 'trepan3kc'
else:
    trepan_client = 'trepan2c'

NO_AVAILABLE_PORT = """\
{self.ident}: Couldn't find an available port.

Please specify one using the CELERY_TREPAN_PORT environment variable.
"""

BANNER = """\
{self.ident}: Please run "%s --host {self.host} --port {self.port}".

Type `exit` in session to continue.

{self.ident}: Waiting for client...
""" % trepan_client

SESSION_STARTED = '{self.ident}: Now in session with {self.remote_addr}.'
SESSION_ENDED = '{self.ident}: Session with {self.remote_addr} ended.'


class RemoteCeleryTrepan():
    me = 'Remote Trepan Debugger'
    _prev_outs = None

    def __init__(self, host=CELERY_TREPAN_HOST, port=CELERY_TREPAN_PORT,
                 out=sys.stdout):
        self.active = True
        self.out = out

        self.ident = '{0}:{1}'.format(self.me, port)

        from trepan.interfaces import server as Mserver
        connection_opts={'IO': 'TCP', 'PORT': port}
        self.intf = Mserver.ServerInterface(connection_opts=connection_opts)
        host = self.intf.inout.HOST
        self.host = host if host else '<hostname>'
        from trepan.api import debug; debug()
        self.port = self.intf.inout.PORT
        self.dbg_opts = {'interface': self.intf}
        return

    def say(self, m):
        print(m, file=self.out)

def debugger():
    """Return the current debugger instance (if any),
    or creates a new one."""
    dbg = _current[0]
    if dbg is None or not dbg.active:
        dbg = _current[0] = RemoteCeleryTrepan()
    return dbg


def debug(frame=None):
    """Set breakpoint at current location, or a specified frame"""
    # ???
    if frame is None:
        frame = _frame().f_back

    dbg = RemoteCeleryTrepan()
    dbg.say(BANNER.format(self=dbg))
    # dbg.say(SESSION_STARTED.format(self=dbg))
    trepan.api.debug(dbg_opts=dbg.dbg_opts)
    # return debugger().set_trace(frame)
