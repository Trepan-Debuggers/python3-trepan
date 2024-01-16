"""Unit test for trepan.inout.tcp*"""
from trepan.inout.tcpclient import TCPClient
from trepan.inout.tcpserver import TCPServer


def test_client_server():
    client = None
    server = None
    try:
        try:
            server = TCPServer(opts={"open": True})
        except Exception:
            print("Skipping because of server open failure")
            return
        print("Server port is %s" % server.PORT)
        try:
            client = TCPClient(opts={"open": True, "PORT": server.PORT})
        except IOError:
            print("Skipping because of client open failure")
            return
        for line in ["one", "two", "three"]:
            server.writeline(line)
            assert line == client.read_msg().rstrip("\n")
            pass

        for line in ["four", "five", "six"]:
            client.writeline(line)
            assert line == server.read_msg().rstrip("\n")
            pass

    finally:
        if client:
            client.close()
        if server:
            server.close()
    return
