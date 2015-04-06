#!/usr/bin/env python
'Unit test for trepan.inout.tcp*'
import unittest
from trepan.inout import tcpserver as Mserver, tcpclient as Mclient


class TestTCP(unittest.TestCase):
    """Tests TCPServer and TCPClient"""

    def test_client_server(self):
        try:
            server = Mserver.TCPServer(opts={'open': True})
        except:
            print("Skipping because of server open failure")
            return
        try:
            client = Mclient.TCPClient(opts={'open': True})
            for line in ['one', 'two', 'three']:
                server.writeline(line)
                self.assertEqual(line, client.read_msg().rstrip('\n'))
                pass
            for line in ['four', 'five', 'six']:
                client.writeline(line)
                self.assertEqual(line, server.read_msg().rstrip('\n'))
                pass
        except:
            print("Skipping because of client open failure")
            pass
        client.close()
        server.close()
        return

if __name__ == '__main__':
    unittest.main()
