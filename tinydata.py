#!/usr/bin/python
import sys, os
sys.path.append('/home/joy/TinyTory')
import web
import json
import config
import decimal

from mydb import mydb
from time import time

urls = ( '/.*', 'data',)

def json_encode_decimal(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError(repr(obj) + " is not JSON serializable")

class data:
    def GET(self):
        db = mydb()
        start = time()
        # Return last 60 seconds worth of data
        start = start - 60
        cursor = db.query("select * from twitter where tweeted_at > %d", start)
        rows = cursor.fetchall()

        db.close()

        return json.dumps(rows, default=json_encode_decimal)

application = web.application(urls, globals()).wsgifunc()

