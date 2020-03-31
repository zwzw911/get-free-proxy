#! /usr/bin/env python3

# -*- coding:utf-8 -*-


class ResponseException(Exception):
    CodeMatchMsg = {
        404: '404，页面不存在'
    }

    def __init__(self, code):
        self.code = code
        if code in ResponseException.CodeMatchMsg:
            self.msg = ResponseException.CodeMatchMsg[self.code]
        else:
            self.msg = '错误代码%d没有匹配的错误信息' % self.code
        super().__init__(ResponseException.CodeMatchMsg[self.code])

    def __str__(self):
        return '错误代码: %d，%s' % (self.code, self.msg)


class InvalidFieldException(Exception):
    def __init__(self, field_name):
        super().__init__()
        self.msg = '字段%s不存在' % field_name

    def __str__(self):
        return '错误：%s' % self.msg
