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
        msg_recu = pickle.loads(r)
        print("Reçu {}".format(msg_recu))
        command = str(msg_recu[0])
        if command == "login":
            login(msg_recu, self)
        if command == "register":
            register(msg_recu, self)
        if command == "sendmsg":
            sendmsg(msg_recu, self)
        if command == "loadidslist":
            loadidslist(msg_recu, self)
        if command == "get_msg":
            get_msg(msg_recu, self)
        if command == "connexion_channel":
            channel = msg_recu[1]
            tablename = "channel_" + channel
            password = msg_recu[2]
            a = check_channel(tablename)
            b = check_password_channel(channel, password)
            if a is True and b is True:
                self.clientsocket.send(pickle.dumps(True))
        if command == "used_channel":
            channel = msg_recu[1]
            tablename = "channel_" + channel
            self.clientsocket.send(pickle.dumps(check_channel(tablename)))
        if command == "new_channel":
            new_channel(msg_recu, self)
        if command == "get_chan_name":
            get_chan_name(msg_recu, self)
        if command == "del_channel":
            del_channel(msg_recu, self)

tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((readcfg(['SOCKET', 'host']), int(readcfg(['SOCKET', 'port']))))
print("en écoute")

while True:
    tcpsock.listen(10)
    (clientsocket, (ip, port)) = tcpsock.accept()
    newthread = ClientThread(ip, port, clientsocket)
    newthread.start()