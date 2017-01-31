# -*- coding: utf-8 -*-
import hashlib
from datetime import datetime


def generate_key():
    md5 = hashlib.new('md5')
    md5.update(str(datetime.utcnow()))
    return md5.hexdigest()[:15]
