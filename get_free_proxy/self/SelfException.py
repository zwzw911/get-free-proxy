#! /usr/bin/env python3
# -*- coding:utf-8 -*-

class InvalidFieldException(Exception):
    def __init__(self, field_name):
        super().__init__()
        self.msg = '字段%s不存在' % field_name

    def __str__(self):
        return '错误：%s' % self.msg
