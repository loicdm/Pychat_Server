#!/usr/bin/env python
# -*- coding: utf-8 -*-
import configparser
import os.path
import pickle
from time import *
import threading
import socket
import socketserver
import mysql.connector


def login(userinput, self):
    login = str(userinput[1])
    password = str(userinput[2])
    if check_login(login, self) is True and check_password_user(login, password, self) is True:
        self.clientsocket.send(pickle.dumps(True))
    else:
        self.clientsocket.send(pickle.dumps(False))


def sendmsg(userinput, self):
    username = str(userinput[1])
    id = str(userinput[2])
    tablename = "channel_" + id
    password = str(userinput[3])
    msg = str(userinput[4])
    time = strftime('%Y-%m-%d %H:%M:%S')
    if len(msg) <= 140:
        try:
            cnx = connect_db(0)
            cursor = cnx.cursor()
            is_password_valid = check_password_channel(id, password, self)
            if is_password_valid is True:
                query = ("INSERT INTO " + tablename + "(username, msg, time) VALUES("
                         + "'" + username + "'" + ", " + "'" + msg + "'" + ", " + "'" + time + "'" + ")")
                cursor.execute(query)
                cnx.commit()
                cursor.close()
                cnx.close()
                self.clientsocket.send(pickle.dumps(True))
            else:
                cursor.close()
                cnx.close()
        except mysql.connector.Error as err:
            print(err)
            self.clientsocket.send(pickle.dumps("err3"))
        else:
            self.clientsocket.send(pickle.dumps(False))


def loadidslist(userinput, self):
    channel = str(userinput[1])
    password = str(userinput[2])
    tablename = "channel_" + channel
    is_password_valid = check_password_channel(channel, password, self)
    if is_password_valid is True:
        try:
            cnx = connect_db(0)
            cursor = cnx.cursor()
            query = "SELECT id FROM " + tablename + " ORDER BY id ASC"
            cursor.execute(query)
            data = cursor.fetchall()
            cnx.commit()
            cursor.close()
            if data != "":
                self.clientsocket.send(pickle.dumps(data))
            else:
                self.clientsocket.send(pickle.dumps("nomessages"))
        except mysql.connector.Error as err:
            print(err)
            self.clientsocket.send(pickle.dumps("err3"))


def get_msg(userinput, self):
    id = str(userinput[1])
    channel = str(userinput[2])
    tablename = "channel_" + channel
    password = str(userinput[3])
    try:
        is_password_valid = check_password_channel(channel, password, self)
        if is_password_valid is True:
            cnx = connect_db(0)
            cursor = cnx.cursor()
            query = "SELECT username FROM " + tablename + " WHERE id ='" + id + "'"
            cursor.execute(query)
            username = cursor.fetchall()
            username = str(username[0])
            username = username[2:-3]
            query = "SELECT msg FROM " + tablename + " WHERE id ='" + id + "'"
            cursor.execute(query)
            msg = cursor.fetchall()
            msg = str(msg[0])
            msg = msg[2:-3]
            query = "SELECT time FROM " + tablename + " WHERE id ='" + id + "'"
            cursor.execute(query)
            time = cursor.fetchall()
            time = str(time[0])
            time = time[19:-3]
            time = time.split(", ")
            returnlist = [id, username, msg, time]
            self.clientsocket.send(pickle.dumps(returnlist))
    except mysql.connector.Error as err:
        print(err)
        self.clientsocket.send(pickle.dumps("err3"))


def register(userinput, self):
    username = str(userinput[1])
    password = str(userinput[2])
    first_name = str(userinput[3])
    last_name = str(userinput[4])
    email = str(userinput[5])
    is_login_used = check_login(username, self)
    is_email_used = check_email(email, self)
    if is_email_used is False and is_login_used is False:
        try:
            cnx = connect_db(1)
            cursor = cnx.cursor()
            query = "INSERT INTO users (password, username, first_name, last_name, email) VALUES(" + "'" + password + "'" + ", " + "'" + username + "'" + ", " + "'" + first_name + "'" + ", " + "'" + last_name + "'" + ", " + "'" + email + "'" + ")"
            cursor.execute(query)
            cnx.commit()
            cursor.close()
            cnx.close()
            self.clientsocket.send(pickle.dumps(True))
        except:
            self.clientsocket.send(pickle.dumps("err3"))
    elif is_email_used is True or is_login_used is True:
        self.clientsocket.send(pickle.dumps(False))


def check_login(login, self):
    try:
        cnx = connect_db(1)
        cursor = cnx.cursor()
        query = "SELECT username FROM users WHERE username ='" + login + "'"
        cursor.execute(query)
        data = cursor.fetchall()
        if data:
            cursor.close()
            cnx.close()
            return True
        else:
            return False
    except:
        self.clientsocket.send(pickle.dumps("err3"))


def check_email(email, self):
    try:
        cnx = connect_db(1)
        cursor = cnx.cursor()
        query = "SELECT username FROM users WHERE email ='" + email + "'"
        cursor.execute(query)
        data = cursor.fetchall()
        if data:
            cursor.close()
            cnx.close()
            return True
        else:
            return False
    except:
        self.clientsocket.send(pickle.dumps("err3"))


def check_channel(tablename, self):
    try:
        cnx = connect_db(0)
        cursor = cnx.cursor()
        query = "SHOW TABLES LIKE '" + tablename + "'"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        cnx.close()
        if data:
            return True
        else:
            return False
    except:
        self.clientsocket.send(pickle.dumps("err3"))


def get_channel_id(tablename):
    try:
        cnx = connect_db(0)
        cursor = cnx.cursor()
        query = "SELECT id FROM channels_infos WHERE channel_name = '" + tablename + "'"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        cnx.close()
        if data:
            return True
        else:
            return False
    except:
        return "err"


def get_chan_name(userinput, self):
    id = str(userinput[1])
    try:
        cnx = connect_db(0)
        cursor = cnx.cursor()
        query = "SELECT channel_name FROM channels_infos WHERE id = '" + id + "'"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        cnx.close()
        if data:
            msg = str(data[0])
            msg = msg[2:-3]
            self.clientsocket.send(pickle.dumps(msg))
        else:
            self.clientsocket.send(pickle.dumps("err5"))
    except mysql.connector.Error as err:
        print(err)
        self.clientsocket.send(pickle.dumps("err3"))


def new_channel(userinput, self):
    user = userinput[1]
    name = userinput[2]
    password = userinput[3]
    try:
        cnx = connect_db(0)
        cursor = cnx.cursor()
        SQL = (
            """INSERT INTO """ + readcfg(['DATABASE',
                                          'database_channels']) + """.channels_infos (password, channel_name, owner) VALUES ('""" + password + """', '""" + name + """', '""" + user + """');""")
        cursor.execute(SQL)
        cnx.commit()
        cursor.close()
        id = cursor.lastrowid
        tablename = "channel_" + str(id)
        cursor2 = cnx.cursor()
        SQL = ("""CREATE TABLE IF NOT EXISTS """ + tablename + """ (
        id int(11) NOT NULL,
          username varchar(32) COLLATE utf8_unicode_ci NOT NULL,
          msg varchar(140) COLLATE utf8_unicode_ci NOT NULL,
          time datetime NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

        ALTER TABLE """ + tablename + """
         ADD PRIMARY KEY (id);

        ALTER TABLE """ + tablename + """
        MODIFY id int(11) NOT NULL AUTO_INCREMENT;""")
        for query in cursor2.execute(SQL, multi=True):
            pass
        cnx.commit()
        cursor.close()
        cnx.close()
        returnlist = [True, id]
        self.clientsocket.send(pickle.dumps(returnlist))
    except mysql.connector.Error as err:
        print(err)
        self.clientsocket.send(pickle.dumps("err 3"))


def connect_db(mode):
    if mode == 0:
        cnx = mysql.connector.connect(host=readcfg(['DATABASE', 'host']),
                                      port=int(readcfg(['DATABASE', 'port'])),
                                      user=readcfg(['DATABASE', 'user']),
                                      password=readcfg(['DATABASE', 'password']),
                                      database=readcfg(['DATABASE', 'database_channels']))
        return cnx
    if mode == 1:
        cnx = mysql.connector.connect(host=readcfg(['DATABASE', 'host']),
                                      port=int(readcfg(['DATABASE', 'port'])),
                                      user=readcfg(['DATABASE', 'user']),
                                      password=readcfg(['DATABASE', 'password']),
                                      database=readcfg(['DATABASE', 'database_users']))
        return cnx
    else:
        print("invalid mode")


def del_channel(userinput, self):
    username = userinput[1]
    userpassword = userinput[2]
    channel = userinput[3]
    password = userinput[4]
    tablename = "channel_" + str(channel)
    if check_login(username, self) is True and check_password_user(username, userpassword,
                                                                   self) is True and check_password_channel(channel,
                                                                                                            password,
                                                                                                            self) is True and check_chan_owner(
        channel, username) is True:
        try:
            cnx = connect_db(0)
            cursor = cnx.cursor()
            SQL = ("""DELETE FROM """ + readcfg(
                ['DATABASE', 'database_channels']) + """.channels_infos WHERE channels_infos.id = '""" + str(channel) + """';
            DROP TABLE IF EXISTS """ + str(tablename) + """;""")
            for query in cursor.execute(SQL, multi=True):
                pass
            cnx.commit()
            cursor.close()
            cnx.close()
            self.clientsocket.send(pickle.dumps(True))
        except mysql.connector.Error as err:
            print(err)
            self.clientsocket.send(pickle.dumps("err3"))
    else:
        self.clientsocket.send(pickle.dumps(False))


def clear_channel(userinput, self):
    username = userinput[1]
    userpassword = userinput[2]
    channel = userinput[3]
    password = userinput[4]
    tablename = "channel_" + str(channel)
    if check_login(username, self) is True and check_password_user(username, userpassword,
                                                                   self) is True and check_password_channel(channel,
                                                                                                            password,
                                                                                                            self) is True and check_chan_owner(
        channel, username) is True:
        try:
            cnx = connect_db(0)
            cursor = cnx.cursor()
            SQL = ("""TRUNCATE """ + readcfg(['DATABASE', 'database_channels']) + """.""" + tablename + """;
            ALTER TABLE """ + tablename + """ AUTO_INCREMENT = 1;""")
            for query in cursor.execute(SQL, multi=True):
                pass
            cnx.commit()
            cursor.close()
            cnx.close()
            self.clientsocket.send(pickle.dumps(True))
        except mysql.connector.Error as err:
            print(err)
            self.clientsocket.send(pickle.dumps("err3"))
    else:
        self.clientsocket.send(pickle.dumps(False))


def check_chan_owner(id, username):
    try:
        cnx = connect_db(0)
        cursor = cnx.cursor()
        query = "SELECT owner FROM channels_infos WHERE id = '" + str(id) + "'"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
        cnx.close()
        if data:
            msg = str(data[0])
            msg = msg[2:-3]
            if msg == username:
                return True
            else:
                return False
        else:
            return False
    except mysql.connector.Error as err:
        print(err)
        return False


def check_password_user(login, password, self):
    try:
        cnx = connect_db(1)
        cursor = cnx.cursor()
        query = "SELECT password FROM users WHERE username ='" + login + "'"
        cursor.execute(query)
        data = cursor.fetchall()
        data = str(data)
        data = data[3:-4]
        if data == password:
            cursor.close()
            cnx.close()
            return True
        else:
            return False
    except:
        self.clientsocket.send(pickle.dumps("err3"))


def check_password_channel(channel, password, self):
    try:
        cnx = connect_db(0)
        cursor = cnx.cursor()
        query = "SELECT password FROM channels_infos WHERE id ='" + str(channel) + "'"
        cursor.execute(query)
        data = cursor.fetchall()
        data = str(data)
        data = data[3:-4]
        if data == password:
            cursor.close()
            cnx.close()
            return True
        else:
            return False
    except:
        self.clientsocket.send(pickle.dumps("err3"))


def readcfg(list):
    config = configparser.ConfigParser()
    config.read('server_config.ini')
    for item in list:
        config = config[item]
    return str(config)


def check_cfg():
    if os.path.exists("server_config.ini") is False:
        config = configparser.ConfigParser()
        config.read('server_config.ini')
        config['SOCKET'] = {'host': 'localhost',
                            'port': '1111'}
        config['DATABASE'] = {'host': '',
                              'port': '',
                              'user': '',
                              'password': '',
                              'database_users': '',
                              'database_channels': ''}
        with open('server_config.ini', 'w') as configfile:
            config.write(configfile)
    else:
        config = configparser.ConfigParser()
        config.read('server_config.ini')
        if ('SOCKET' in config) is False:
            config['SOCKET'] = {'host': 'localhost',
                                'port': '1111'}
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)

        if ('host' in config['SOCKET']) is False:
            config['SOCKET']['host'] = 'localhost'
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)

        if ('port' in config['SOCKET']) is False:
            config['SOCKET']['port'] = '1111'
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)

        if ('host' in config['DATABASE']) is False:
            config['DATABASE']['host'] = ''
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)

        if ('port' in config['DATABASE']) is False:
            config['DATABASE']['port'] = ''
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)

        if ('user' in config['DATABASE']) is False:
            config['DATABASE']['user'] = ''
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)

        if ('password' in config['DATABASE']) is False:
            config['DATABASE']['password'] = ''
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)

        if ('database_users' in config['DATABASE']) is False:
            config['DATABASE']['database_users'] = ''
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)
        if ('database_channels' in config['DATABASE']) is False:
            config['DATABASE']['database_channels'] = ''
            with open('server_config.ini', 'w') as configfile:
                config.write(configfile)


def check_db():
    try:
        cnx = mysql.connector.connect(host=readcfg(['DATABASE', 'host']),
                                      port=int(readcfg(['DATABASE', 'port'])),
                                      user=readcfg(['DATABASE', 'user']),
                                      password=readcfg(['DATABASE', 'password']))
        database_users = readcfg(['DATABASE', 'database_users'])
        cursor = cnx.cursor()
        SQL = """CREATE DATABASE IF NOT EXISTS """ + database_users + """ DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE """ + database_users + """;
CREATE TABLE IF NOT EXISTS users (
id int(11) NOT NULL,
  username text COLLATE utf8_unicode_ci NOT NULL,
  password text COLLATE utf8_unicode_ci NOT NULL,
  email text COLLATE utf8_unicode_ci NOT NULL,
  first_name text COLLATE utf8_unicode_ci NOT NULL,
  last_name text COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
ALTER TABLE users
 ADD PRIMARY KEY (id);
 ALTER TABLE users
MODIFY id int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;"""
        for query in cursor.execute(SQL, multi=True):
            pass
        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(err)
        return False
    try:
        cnx = mysql.connector.connect(host=readcfg(['DATABASE', 'host']),
                                      port=int(readcfg(['DATABASE', 'port'])),
                                      user=readcfg(['DATABASE', 'user']),
                                      password=readcfg(['DATABASE', 'password']))
        database_channels = readcfg(['DATABASE', 'database_channels'])
        cursor = cnx.cursor()
        SQL = """CREATE DATABASE IF NOT EXISTS """ + database_channels + """ DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;
USE """ + database_channels + """;
CREATE TABLE IF NOT EXISTS channels_infos (
id int(11) NOT NULL,
password text COLLATE utf8_unicode_ci NOT NULL,
channel_name text COLLATE utf8_unicode_ci NOT NULL,
owner text COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
ALTER TABLE channels_infos
ADD PRIMARY KEY (id);
ALTER TABLE channels_infos
MODIFY id int(11) NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;"""
        for query in cursor.execute(SQL, multi=True):
            pass
        cnx.commit()
        cursor.close()
        cnx.close()
    except mysql.connector.Error as err:
        print(err)
        return False
