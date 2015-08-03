# -*- coding:utf-8 -*-


def get_string_val(num):
    _n = str(num)
    return '+%s(%s)%s-%s-%s' % (_n[0], _n[1:4], _n[4:7], _n[7:9], _n[9:])


def check_phone(val):
    import re
    res = re.sub('[^\w]', '', val)
    res = re.sub('^8', '7', res)
    res = ('7' if not re.search('^7', res) else '') + res
    return res
