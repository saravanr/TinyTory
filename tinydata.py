#!/usr/bin/python
import web
import config
import mydb

urls = ( '/.*', 'data',)

class data:
    def GET(self):
        db = mydb()

        cursor = db.query("SELECT * from TWITTER", None)
        rows = cursor.fetchall()

        for row in rows:
            print row

application = web.application(urls, globals()).wsgifunc()
