import logging


class MyLogger:

    def print(self, level,   message):
        print("%s - %s" % (level, message))

    def debug(self, message):
        self.print("DBUG", message)

    def info(self, message):
        self.print("INFO", message)

    def failed(self, message):
        self.print("FAIL", message)

    def passed(self, message):
        self.print("PASS", message)

    def skipped(self, message):
        self.print("SKIP", message)

    def error(self, message):
        self.print("ERRS", message)

    def warning(self, message):
        self.print("WRNG", message)


logging.addLevelName(27, 'SKIP')
logging.addLevelName(26, 'FAIL')
logging.addLevelName(25, 'PASS')


class FileLogger:
    def __init__(self, path):
        self.logger = logging.getLogger('LOGGER')
        self.path = path
        self.file_handler = logging.FileHandler(self.path, mode='w', encoding='ascii')
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.DEBUG)

    def debug(self, message):
        self.logger.debug('DBUG - ' + message)

    def info(self, message):
        self.logger.info('INFO - ' + message)

    def failed(self, message, *args, **kwargs):
        self.logger._log(26, 'FAIL - ' + message, args, kwargs)

    def passed(self, message, *args, **kwargs):
        self.logger._log(25, 'PASS - ' + message, args, kwargs)

    def skipped(self, message, *args, **kwargs):
        self.logger._log(27, 'SKIP - ' + message, args, kwargs)

    def error(self, message):
        self.logger.error('ERRS - ' + message)

    def warning(self, message):
        self.logger.warning('WRNG - ' + message)

