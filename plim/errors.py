# -*- coding: utf-8 -*-



class SlimError(Exception):
    def __str__(self):
        return self.__unicode__().encode('utf-8')


class SlimSyntaxError(SlimError):
    def __init__(self, msg, line):
        super(SlimSyntaxError, self).__init__()
        self.msg = msg
        self.line = line

    def __unicode__(self):
        return u"{msg}: {line}".format(msg=self.msg, line=self.line)


class ParserNotFound(SlimError):
    def __init__(self, lineno, line):
        super(ParserNotFound, self).__init__()
        self.lineno = lineno
        self.line = line

    def __unicode__(self):
        return u"Invalid syntax at line {lineno}: {line}".format(
            lineno=self.lineno, line=self.line)
