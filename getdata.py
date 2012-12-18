#!/usr/bin/python

from mydb import mydb 
from twitterclient import twitterclient
from valence import valence
import time
from datetime import datetime
import json
from dateutil import parser

db = None

'''
    Saves tweet information into database
'''
def insertdb(tweet_time, sentiment, longitude, latitude):
    global db
    sql = 'INSERT into twitter(tweeted_at, sentiment, longitude, lattitude)\
           VALUES("%d", "%f", "%f", "%f")'
    db.query(sql, tweet_time, sentiment, longitude, latitude)
    db.commit()

'''
    Measures twitter mood for given number of hours
'''
def measure_mood(max_hours):
    url = "https://stream.twitter.com/1/statuses/sample.json"
    parameters = []
    tc = twitterclient()
    response = tc.twitterreq(url, "GET", parameters)

    # Estimate number of tweets for 5 minutes
    print "Waiting for " + str(max_hours) + " hours"

    start=time.time()
    vc = valence()

    for line in response:
        line = line.encode('ascii', 'replace')
        data = json.loads(line)

        if('text' in data):
            sentiment = vc.get_sentiment(data['text'])

            if(data['coordinates']):
                # Insert into db
                print data['user']['screen_name'] + '(' + str(sentiment) + ')'
                created_at = time.mktime(parser.parse(data['created_at'])
                                 .timetuple())
                insertdb(created_at, float(sentiment), \
                         float(data['coordinates']['coordinates'][0]),
                         float(data['coordinates']['coordinates'][1]))
        if(time.time() - start > 60 * 60 * max_hours):
            break
    return

def main():
    global db
    db = mydb()
#    try:
    measure_mood(24)

    db.close()
#    except:
#        pass

if __name__ == '__main__':
    main()
 
