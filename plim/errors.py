class PlimError(Exception):
    pass


class PlimSyntaxError(PlimError):
    def __init__(self, msg: str, line: str):
        super(PlimSyntaxError, self).__init__()
        self.msg = msg
        self.line = line

    def __str__(self) -> str:
        return '{msg} | at line(pos) "{line}"'.format(msg=self.msg, line=self.line)


class ParserNotFound(PlimError):
    def __init__(self, lineno: int, line: str):
        super(ParserNotFound, self).__init__()
        self.lineno = lineno
        self.line = line

    def __str__(self) -> str:
        return "Invalid syntax at line {lineno}: {line}".format(
            lineno=self.lineno, line=self.line)
