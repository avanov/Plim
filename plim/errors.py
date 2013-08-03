# -*- coding: utf-8 -*-
from .util import as_unicode



class PlimError(Exception):
    def __str__(self):
        return self.__unicode__().encode('utf-8')


class PlimSyntaxError(PlimError):
    def __init__(self, msg, line):
        super(PlimSyntaxError, self).__init__()
        self.msg = msg
        self.line = line

    def __unicode__(self):
        return as_unicode('{msg} | at line(pos) "{line}"').format(msg=self.msg, line=self.line)


class ParserNotFound(PlimError):
    def __init__(self, lineno, line):
        super(ParserNotFound, self).__init__()
        self.lineno = lineno
        self.line = line

    def __unicode__(self):
        return as_unicode("Invalid syntax at line {lineno}: {line}").format(
            lineno=self.lineno, line=self.line)
