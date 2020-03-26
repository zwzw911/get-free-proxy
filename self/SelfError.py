#! /usr/bin/env python3

# -*- coding:utf-8 -*-


class ResponseException(Exception):
    CodeMatchMsg = {
        '200': '错误'
    }

    def __init__(self, code):
        self.code = code
        self.msg = ResponseException.CodeMatchMsg[str(self.code)]
        super().__init__(ResponseException.CodeMatchMsg[str(self.code)])

    def __str__(self):
        return '错误代码: %d，%s' % (self.code, self.msg)