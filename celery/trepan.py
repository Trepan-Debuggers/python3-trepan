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

import errno
import os
import socket
import sys
import trepan

from billiard import current_process

from celery.five import range

__all__ = ['CELERY_TREPAN_HOST', 'CELERY_TREPAN_PORT', 'default_port',
           'RemoteTrepan', 'debugger', 'debug']

default_port = 6898

CELERY_TREPAN_HOST = os.environ.get('CELERY_TREPAN_HOST') or '127.0.0.1'
CELERY_TREPAN_PORT = int(os.environ.get('CELERY_TREPAN_PORT') or default_port)

#: Holds the currently active debugger.
_current = [None]

_frame = getattr(sys, '_getframe')

NO_AVAILABLE_PORT = """\
{self.ident}: Couldn't find an available port.

Please specify one using the CELERY_TREPAN_PORT environment variable.
"""

BANNER = """\
{self.ident}: Please telnet into {self.host} {self.port}.

Type `exit` in session to continue.

{self.ident}: Waiting for client...
"""

SESSION_STARTED = '{self.ident}: Now in session with {self.remote_addr}.'
SESSION_ENDED = '{self.ident}: Session with {self.remote_addr} ended.'


class RemoteTrepan():
    me = 'Remote Trepan Debugger'
    _prev_outs = None
    _sock = None

    def __init__(self, host=CELERY_TREPAN_HOST, port=CELERY_TREPAN_PORT,
                 port_search_limit=100, port_skew=+0, out=sys.stdout):
        self.active = True
        self.out = out

        self._prev_handles = sys.stdin, sys.stdout

        # self._sock, this_port = self.get_avail_port(
        #     host, port, port_search_limit, port_skew,
        # )

        self.host = host
        self.port = port
        self.ident = '{0}:{1}'.format(self.me, port)

        from trepan.interfaces import server as Mserver
        connection_opts={'IO': 'TCP', 'PORT': port}
        self.intf = Mserver.ServerInterface(connection_opts=connection_opts)
        self.dbg_opts = {'interface': self.intf}
        self.remote_addr = '???'
        return

    def get_avail_port(self, host, port, search_limit=100, skew=+0):
        try:
            _, skew = current_process().name.split('-')
            skew = int(skew)
        except ValueError:
            pass
        this_port = None
        for i in range(search_limit):
            _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            this_port = port + skew + i
            try:
                _sock.bind((host, this_port))
            except socket.error as exc:
                if exc.errno in [errno.EADDRINUSE, errno.EINVAL]:
                    continue
                raise
            else:
                return _sock, this_port
        else:
            raise Exception(NO_AVAILABLE_PORT.format(self=self))

    def say(self, m):
        print(m, file=self.out)

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self._close_session()

    def _close_session(self):
        self.stdin, self.stdout = sys.stdin, sys.stdout = self._prev_handles
        if self.active:
            if self._handle is not None:
                self._handle.close()
            if self._client is not None:
                self._client.close()
            if self._sock is not None:
                self._sock.close()
            self.active = False
            self.say(SESSION_ENDED.format(self=self))

    # def do_continue(self, arg):
    #     self._close_session()
    #     self.set_continue()
    #     return 1
    # do_c = do_cont = do_continue

    # def do_quit(self, arg):
    #     self._close_session()
    #     self.set_quit()
    #     return 1
    # do_q = do_exit = do_quit

    # def set_quit(self):
    #     # this raises a BdbQuit exception that we are unable to catch.
    #     sys.settrace(None)


def debugger():
    """Return the current debugger instance (if any),
    or creates a new one."""
    dbg = _current[0]
    if dbg is None or not dbg.active:
        dbg = _current[0] = RemoteTrepan()
    return dbg


def debug(frame=None):
    """Set breakpoint at current location, or a specified frame"""
    # ???
    if frame is None:
        frame = _frame().f_back

    dbg = RemoteTrepan()
    dbg.say(BANNER.format(self=dbg))
    dbg.say(SESSION_STARTED.format(self=dbg))
    trepan.api.debug(dbg_opts=dbg.dbg_opts)
    dbg._handle = sys.stdin = sys.stdout = dbg._client.makefile('rw')
    # return debugger().set_trace(frame)
