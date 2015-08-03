# -*- coding:utf-8 -*-


def get_string_val(num):
    _n = str(num)
    return '+%s(%s)%s-%s-%s' % (_n[0], _n[1:4], _n[4:7], _n[7:9], _n[9:])


def check_phone(val):
    import re
    plus_pattern = '[^\w]'
    code_pattern = '^8'
    res = re.sub(plus_pattern, '', val)
    return re.sub(code_pattern, '7', res)
