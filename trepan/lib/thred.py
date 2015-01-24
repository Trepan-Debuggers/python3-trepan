# -*- coding: utf-8 -*-
#   Copyright (C) 2008-2009, 2013-2014 Rocky Bernstein <rocky@gnu.org>
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
"""Routines related to threading. Assumes Python 2.5 or greater"""

import threading


def current_thread_name():
    return threading.currentThread().getName()


def find_debugged_frame(frame):
    """Find the first frame that is a debugged frame. We do this
    Generally we want traceback information without polluting it with
    debugger frames. We can tell these because those are frames on the
    top which don't have f_trace set. So we'll look back from the top
    to find the fist frame where f_trace is set.
    """
    f_prev = f = frame
    while f is not None and f.f_trace is None:
        f_prev = f
        f = f.f_back
        pass
    if f_prev:
        val = f_prev.f_locals.get('tracer_func_frame')
        if val == f_prev:
            if f_prev.f_back:
                f_prev = f_prev.f_back
                pass
            pass
        pass
    else:
        return frame
    return f_prev


def id2thread_name(thread_id):
    return threading.Thread.getName(threading._active[thread_id])


def map_thread_names():
    '''Invert threading._active'''
    name2id = {}
    for thread_id in list(threading._active.keys()):
        thread = threading._active[thread_id]
        name = thread.getName()
        if name not in list(name2id.keys()):
            name2id[name] = thread_id
            pass
        pass
    return name2id

# Demo this masterpiece:
if __name__ == '__main__':
    import sys
    print('=' * 10)

    def showit():
        print('Current thread: %s' % current_thread_name())
        print('All threads:')
        for thread_id, f in list(sys._current_frames().items()):
            print('  %s %s' % (id2thread_name(thread_id),
                               find_debugged_frame(f)))
            pass
        print('-' * 10)
        print('Thread->id map:')
        print(map_thread_names())
        print('=' * 10)
    showit()

    class BgThread(threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
            return

        def run(self):
            showit()
            return
        pass

    background = BgThread()
    background.start()
    background.join()    # Wait for the background task to finish
    pass
