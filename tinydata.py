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
        user_data = web.input()
        data_id = int(web.websafe(user_data.data_id))
        cursor = db.query("select * from twitter where id > %s limit 100", data_id) 
        rows = cursor.fetchall()

        db.close()
        web.header('Content-Type', 'application/json')
        result = {}
        for row in rows:
            index = row[0]
            result[index] ={}
            result[index]['s'] = row[2]
            result[index]['lo'] = row[3]
            result[index]['la'] = row[4]
        return json.dumps(result, default=json_encode_decimal)


application = web.application(urls, globals()).wsgifunc()

