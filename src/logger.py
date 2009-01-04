"""Logger facility"""

from datetime import datetime

DEFAULT_FMT = (("IN", "\033[1;32mIN\033[0m", 1),
               ("OUT", "\033[1;31mOUT\033[0m", 1))

class Logger:

    def __init__(self, **kwargs):
        self.facility = {}

        if 'file' in kwargs:
            self.file_ = kwargs['file']
            self.facility['file'] = FileLogger(self.file_)
        else:
            self.file_ = None

        if 'fmt' in kwargs:
            self.facility['console'] = ConsoleLogger(fmt=kwargs['fmt'])
        else:
            self.facility['console'] = ConsoleLogger()

    def file(self, data):
        """Write to the file

        Falls back to console if file logging facility is unavailable
        """

        if not self.file_:
            # default to console
            facility = self.facility['console']
        else:
            facility = self.facility['file']

        facility.write(data)

    def console(self, data):
        """Write to the console
        """
        self.facility['console'].write(data)

class ConsoleLogger:

    def __init__(self, **kwargs):
        if 'fmt' in kwargs:
            self.fmt = kwargs['fmt']
        else:
            self.fmt = DEFAULT_FMT

    def write(self, data):
        """Write data"""
        if self.fmt:
            for (find, repl, limit) in self.fmt:
                data = data.replace(find, repl, limit)

        timestamp = datetime.now().strftime('%Y%m%d.%H%M%S')
        print "%s %s" % (timestamp, data)

class FileLogger:

    def __init__(self, file_):
        """Constructor

        @param takes a filename
        """
        self.file_ = file(file_, 'a')

    def write(self, data):
        """Write to file"""
        timestamp = datetime.now().strftime('%Y%m%d.%H%M%S')
        self.file_.write("%s %s\n" % (timestamp, data))
