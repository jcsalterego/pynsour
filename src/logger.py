"""Logger facility"""

from datetime import datetime

class Logger:

    def __init__(self, **kwargs):
        self.facility = {}

        if 'file' in kwargs:
            self.file_ = kwargs['file']
            self.facility['file'] = FileLogger(self.file_)
        else:
            self.file_ = None

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

    def write(self, data):
        """Write data"""
        timestamp = datetime.now().strftime('%Y%m%d.%H%M%S')
        print "[%s] %s" % (timestamp, data)

class FileLogger:

    def __init__(self, file_):
        """Constructor

        @param takes a filename
        """
        self.file_ = file(file_, 'a')

    def write(self, data):
        """Write to file"""
        timestamp = datetime.now().strftime('%Y%m%d.%H%M%S')
        self.file_.write("[%s] %s\n" % (timestamp, data))
