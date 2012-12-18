import MySQLdb
import config

class mydb:
    sql_conn = None

    def connect(self):
        try:
            self.sql_conn = MySQLdb.connect(config.SQLHOST, config.SQLUSER, \
                                            config.SQLPASSWORD, config.SQLDB)
        except (AttributeError, MySQLdb.OperationalError), e:
            print 'Sql exception: ', e
            raise e

    def query(self, sql, *params):
        try:
            cursor = self.sql_conn.cursor()
            cursor.execute(sql % params )
        except (AttributeError, MySQLdb.OperationalError), e:
            print 'Sql exception: ', e
        return cursor   
    
    def commit(self):
        try:
            if self.sql_conn:
                self.sql_conn.commit()
        except (AttributeError, MySQLdb.OperationalError), e:
            print 'Sql exception: ', e
            raise e   
                
    def close(self):
        try:
            if self.sql_conn:
                self.sql_conn.commit()
                self.sql_conn.close()
        except (AttributeError, MySQLdb.OperationalError), e:
            print 'Sql exception: ', e
            raise e   
    
    def __init__(self):
        self.connect()

