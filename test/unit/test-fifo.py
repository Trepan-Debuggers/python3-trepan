#!/usr/bin/env python3
'Unit test for trepan.ionout.fifo*'
import os
if hasattr(os, 'mkfifo'):

    import unittest

    from trepan.inout import fifoserver as Mserver, fifoclient as Mclient

    class TestFIFO(unittest.TestCase):
        """Tests FIFOServer and FIFOClient"""

        def test_client_server(self):
            Mserver.FIFOServer(opts={'open': True})
            Mclient.FIFOClient(opts={'open': os.getpid()})
            self.assertTrue(True, 'FIXME: need to add a test here.')
            # FIXME need to use threading or forking
    #         for line in ['one', 'two', 'three']:
    #             server.writeline(line)
    #             self.assertEqual(line, client.readline())
    #             pass
    #         for line in ['four', 'five', 'six']:
    #             client.writeline(line)
    #             self.assertEqual(line, server.readline())
    #             pass
            return

    if __name__ == '__main__':
        unittest.main()
        pass
    pass
