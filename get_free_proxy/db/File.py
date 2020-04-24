#! /usr/bin/env python3
# -*- coding:utf-8 -*-

import json

def save_proxies(file_path, proxies):
    with open(file_path, 'w') as f:
        f.write(json.dumps(proxies))

