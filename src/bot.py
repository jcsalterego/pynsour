"""Bot class"""

import os
import socket

from parser import Parser
from logger import Logger
import botcode

MAX_CONSOLE_LEN = 50
BUFFER_SIZE = 1024
STATE_DISCONNECTED = 0
STATE_CONNECTING = 1
STATE_HANDSHAKE = 2
STATE_CONNECTED = 3
STATE_ONLINE = 4

class Bot:

    def __init__(self):
        """Constructor
        """
        self.__state = STATE_DISCONNECTED
        self.__load_defaults()
        self.parser = Parser()
        self.logger = Logger()

    def __load_defaults(self):
        """Loads default settings
        """
        self.username = os.getlogin()
        self.password = None
        self.nicks = ["nick", "altnick"]
        self.realname = "Default pynsour user"
        self.handlers = []
        self.localhost = 'localhost'
        self.on_connect = []
        self.ops = []

    def asDict(self):
        """Return object as dictionary

        Ignores doc variables
        """
        info = {}
        for attr in dir(self):
            if attr[0] == "_" or attr[:2] == "__":
                continue

            i = getattr(self, attr)
            if type(i).__name__ == "instancemethod":
                continue
            else:
                info[attr] = i
        return info

    def connect(self):
        """Connect the bot to the IRC server
        """
        self.__state = STATE_CONNECTING
        self.__connection = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM)
        self.logger.console("+++ Connecting to %s:%s" %
                            (self.hostname, self.port))
        self.__connection.connect((self.hostname, self.port))

    def event(self):
        """Event fire
        """
        if self.__state == STATE_DISCONNECTED:
            return
        elif self.__state == STATE_CONNECTING:
            if self.password:
                self.write("PASS %s" % self.password)
            self.write("NICK %s" % self.nicks[0])
            self.write("USER %s %s %s :%s" %
                       (self.username,
                        self.localhost,
                        self.hostname,
                        self.realname))

            self.__state = STATE_HANDSHAKE
        elif self.__state == STATE_HANDSHAKE:
            pass

        self.read()
        self.ops += self.parser.parse()
        self.execute()
    
    def execute(self):
        """Execute botcode
        """
        ops = []

        # Expand meta-ops, e.g. connect events
        for operation in self.ops[:]:
            if operation[0] == botcode.OP_EVENT_CONNECT:
                ops += self.on_connect
            else:
                ops.append(operation)

        for operation in ops:
            if operation[0] == botcode.OP_PONG:
                self.write("PONG :%s" % operation[1])
            elif operation[0] == botcode.OP_JOIN:
                self.write("JOIN %s" % operation[1])
            elif operation[0] == botcode.OP_MODE:
                self.write("MODE %s" % operation[1])

        self.ops = []

    def read(self):
        """Reading from connection
        """
        if self.__state > STATE_DISCONNECTED:
            incoming = self.__connection.recv(BUFFER_SIZE)
            self.parser.append(incoming)

            read_bytes = len(incoming)

            first_line = incoming.split("\n")[0]
            if len(first_line) > MAX_CONSOLE_LEN:
                first_line = "%s..." % first_line[:MAX_CONSOLE_LEN]
            self.logger.console(" IN [%4d] %s" % (read_bytes,
                                                  first_line))

    def write(self, outgoing):
        """Writing to connection
        """
        first_line = outgoing

        outgoing = "".join((outgoing, "\r\n"))
        write_bytes = len(outgoing)

        if len(first_line) > MAX_CONSOLE_LEN:
            first_line = "%s..." % first_line[:MAX_CONSOLE_LEN]
        self.logger.console("OUT [%4d] %s" % (write_bytes,
                                              first_line))
        self.__connection.send(outgoing)
