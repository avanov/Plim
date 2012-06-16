# -*- coding: utf-8 -*-
from . import lexer



def preprocessor(source):
    return lexer.compile_plim_source(source)
