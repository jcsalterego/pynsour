"""Parser class"""

from pprint import pprint
import botcode

class Parser:
    """Parses buffers
    """
    def __init__(self):
        """Constructor
        """
        self.buffer = []
        self.buffer_complete = True

    def append(self, incoming):
        """Appends incoming data to buffer

        Splits incoming by CRLF and keeps track of whether trailing
        line is complete or otherwise. If the buffer is incomplete
        to begin with, the first line of the incoming data is appended
        to the last line of the existing data. Then, buffer completeness
        is reevaluated based on incoming data.
        """
        lines = incoming.split("\r\n")

        if self.buffer_complete:
            self.buffer += lines
        else:
            # if the last line in incomplete, then the whole
            # buffer is incomplete. thus, we want to append
            # the first line of the incoming to the last line
            # of the buffer

            self.buffer[-1] += lines[0]
            if len(lines) > 1:
                self.buffer += lines[1:]

        self.buffer_complete = (lines[-1] == "")

    def parse(self):
        """Parses lines in buffer

        Returns a list of op codes using the botcode module.
        """
        ops = []

        if self.buffer_complete:
            buffer = self.buffer
        else:
            buffer = self.buffer[:-1]
        
        for line in buffer:
            if not line or line[0] == ":":
                continue

            first, second = line.split(":", 1)
            words = first.strip().split(" ") + [second]

            if words[0] == "PING":
                ops += (botcode.OP_PONG, words[1]),
            else:
                # ignore
                pass

        if self.buffer_complete:
            self.buffer = []
        else:
            # keep the last element
            self.buffer = self.buffer[-1:]
        
        return ops
