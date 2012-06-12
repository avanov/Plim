# -*- coding: utf-8 -*-
import lexer



def preprocessor(source):
    return lexer.compile_slim_source(source)
