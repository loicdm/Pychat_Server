#!/usr/bin/env python
# coding: utf-8
from functions import *

check_cfg()
check_db()


class ClientThread(threading.Thread):
    def __init__(self, ip, port, clientsocket):
        threading.Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.clientsocket = clientsocket

    def run(self):
        print("Connection de %s %s" % (self.ip, self.port,))
        r = self.clientsocket.recv(1024)
        received_message = pickle.loads(r)
        print("Reçu {}".format(received_message))
        command = str(received_message[0])
        if command == "login":
            login(received_message, self)
        if command == "register":
            register(received_message, self)
        if command == "sendmsg":
            sendmsg(received_message, self)
        if command == "loadidslist":
            loadidslist(received_message, self)
        if command == "get_msg":
            get_msg(received_message, self)
        if command == "connexion_channel":
            channel = received_message[1]
            tablename = "channel_" + channel
            password = received_message[2]
            a = check_channel(tablename, self)
            b = check_password_channel(channel, password, self)
            if a is True and b is True:
                self.clientsocket.send(pickle.dumps(True))
            elif a is False or b is False:
                self.clientsocket.send(pickle.dumps(False))
        if command == "used_channel":
            channel = received_message[1]
            tablename = "channel_" + channel
            check_channel(tablename, self)
        if command == "new_channel":
            new_channel(received_message, self)
        if command == "get_chan_name":
            get_chan_name(received_message, self)
        if command == "del_channel":
            del_channel(received_message, self)
        if command == "clear_channel":
            clear_channel(received_message, self)


tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((readcfg(['SOCKET', 'host']), int(readcfg(['SOCKET', 'port']))))

while True:
    tcpsock.listen(10)
    (clientsocket, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsocket)
    newthread.start()
