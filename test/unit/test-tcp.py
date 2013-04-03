#!/usr/bin/env python
'Unit test for trepan.io.tcp*'
import unittest

from import_relative import import_relative
Mserver   = import_relative('trepan.io.tcpserver', '...', 'trepan')
Mclient   = import_relative('trepan.io.tcpclient', '...', 'trepan')
import_relative('interfaces', '...trepan', 'trepan')
Mcomcodes = import_relative('interfaces.comcodes', '...trepan', 'trepan')

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
