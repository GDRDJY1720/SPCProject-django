# _*_ coding:utf-8 _*_

import hashlib


def md5(md5_str: str, salt):
    if type(salt) == list:
        tmp_salt = ''.join(salt)
    else:
        try:
            tmp_salt = str(salt)
        except Exception:
            raise Exception('md5 error')

    m = hashlib.md5(bytes(md5_str, encoding='utf8'))
    m.update(bytes(tmp_salt, encoding='utf8'))
    return m.hexdigest()
