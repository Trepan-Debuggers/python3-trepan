#!/usr/bin/env python3
'Unit test for trepan.lib.thread'
import sys, _thread, threading, unittest

from trepan.lib import thred as Mthread

class BgThread(threading.Thread):
    def __init__(self, id_name_checker):
        threading.Thread.__init__(self)
        self.id_name_checker = id_name_checker
        return

    def run(self):
        self.id_name_checker()
        return
    pass


class TestLibThread(unittest.TestCase):

    def id_name_checker(self):
        '''Helper for testing map_thread_names and id2thread'''
        name2id = Mthread.map_thread_names()
        for thread_id, f in list(sys._current_frames().items()):
            self.assertEqual(thread_id,
                             name2id[Mthread.id2thread_name(thread_id)])
            # FIXME: use a better test
            self.assertNotEqual(f, Mthread.find_debugged_frame(f))
            pass

    def test_current_thread_name(self):
        self.assertEqual('MainThread', Mthread.current_thread_name())
        return

    def test_id2thread_name(self):
        '''Test map_thread_names and id2thread'''
        thread_id = _thread.get_ident()
        self.assertEqual('MainThread', Mthread.id2thread_name(thread_id))
        self.id_name_checker()

        background = BgThread(self.id_name_checker)
        background.start()
        background.join()    # Wait for the background task to finish
        return
    pass

if __name__ == '__main__':
    unittest.main()
