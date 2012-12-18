#!/usr/bin/python
import json
import oauth2 as oauth
import urllib2 as urllib
import unicodedata
import time
import numpy
from optparse import OptionParser
from time import time
import csv
from datetime import datetime

# App credentials
access_token_key = "30362328-SJiPXWJJhOqsAgDi9ub7TAxcnkiRaaBnBpsob1xC0"
access_token_secret = "KUVVur5jpvxRCMZztwCM0E8k9G9byZsFhcvc89frL8"
consumer_key = "mrr3DkdWp8HkfcS1Z4BNrA"
consumer_secret = "DKa3mJRcqbLEhnchDEneSgUMdJ3wKIPvozg7ZzJW0fU"

##########
_debug = 0
##########

oauth_token    = oauth.Token(key=access_token_key, secret=access_token_secret)
oauth_consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
http_method = "GET"
http_handler  = urllib.HTTPHandler(debuglevel=_debug)
https_handler = urllib.HTTPSHandler(debuglevel=_debug)


'''
    Construct, sign, and open a twitter request
    using the hard-coded credentials above.
'''
def twitterreq(url, method, parameters):
    req = oauth.Request.from_consumer_and_token(oauth_consumer,
            token=oauth_token,
            http_method=http_method,
            http_url=url, 
            parameters=parameters)

    req.sign_request(signature_method_hmac_sha1, oauth_consumer, oauth_token)
    headers = req.to_header()

    if http_method == "POST":
        encoded_post_data = req.to_postdata()
    else:
        encoded_post_data = None
        url = req.to_url()

    opener = urllib.OpenerDirector()
    opener.add_handler(http_handler)
    opener.add_handler(https_handler)

    response = opener.open(url, encoded_post_data)
    return response

'''
Used for stripping accent characters
'''
def not_combining(char):
    return unicodedata.category(char) != 'Mn'


'''
    Strips accents from unicode strings
'''
def strip_accents(s):
    unicode_text = unicodedata.normalize('NFD', s.decode('cp1252'))
    return filter(not_combining, unicode_text).encode('ascii', 'ignore')


'''
    Queries census API to get state from [longitude, lattitude] of location
'''
def get_state_from_coordinates(coordinates):
    base_url = "http://data.fcc.gov/api/block/find?format=json"
    query_url = base_url + "&latitude=" + str(coordinates[1]) + "&longitude=" + str(coordinates[0]) + "&showall=true"

    state = {};
    data = json.load(urllib.urlopen(query_url))
    if(data['status'] == 'OK'):
        state = data['State']['name']
    else:
        state = None
    return state

'''
    Save dictionary as CSV
'''
def save_as_csv(dictionary, filename):
    fh = open(filename, "w") 
    w = csv.writer(fh)
    for key, val in dictionary.items():
        w.writerow([key, val])
    fh.close()


'''
    Measures twitter mood for given number of hours
'''
def measure_mood(max_hours):
    url = "https://stream.twitter.com/1/statuses/sample.json"
    parameters = []
    valence_dict = load_valence()
    response = twitterreq(url, "GET", parameters)


    # Estimate number of tweets for 5 minutes
    print "Waiting for " + str(max_hours) + " hours"

    i=0
    start=time()
    filename="moods_" + str(start)
    print "Saving tweets to '" + filename + "'"

    fh = open(filename, "w")
    w = csv.writer(fh)
    for line in response:
        line = line.encode('ascii', 'replace')
        data = json.loads(line)

        if('text' in data):
            i = i + 1
            sentiment = get_sentiment(data['text'], valence_dict)        
            print data['user']['screen_name'] + '(' + str(sentiment) + ')'

            state = None
            if(data['coordinates']):
                # Try to infer state from coordinates
                state = get_state_from_coordinates(data['coordinates']['coordinates'])
           
            w.writerow([data['user']['screen_name'], str(sentiment), state, str(datetime.now())])

        if(time() - start > 60 * 60 * max_hours):
            break

    fh.close()
    return

'''
    Finds the happiest state
'''
def state_sentiment(max_tweets):
    url = "https://stream.twitter.com/1/statuses/sample.json"
    parameters = []
    valence_dict = load_valence()
    response = twitterreq(url, "GET", parameters)


    # Estimate number of tweets for 5 minutes
    print "Waiting for " + str(max_tweets) + " tweets"

    i=0
    state_happiness = {}
    tweets=0

    for line in response:
        line = line.encode('ascii', 'replace')
        data = json.loads(line)

        if('text' in data):
            i = i + 1
            sentiment = get_sentiment(data['text'], valence_dict)        

            #  If sentiment cannot be inferred, ignore the tweet
            if(sentiment == 0.0):
                 continue

            state = None
            if(data['coordinates']):
                # Try to infer state from coordinates
                state = get_state_from_coordinates(data['coordinates']['coordinates'])
                if(state is not None):
                   tweets = tweets + 1
                   print data['user']['screen_name'] + '(' + state + ') -> ' + data['text']
                   if(state in state_happiness):
                       state_happiness[state] = state_happiness[state] + sentiment
                   else:
                       state_happiness[state] = sentiment
        if(tweets > max_tweets):
            break

    filename = "state_happiness_" + str(time())
    save_as_csv(state_happiness, filename)

    for state, sentiment in state_happiness.iteritems():
        print state + " :" + str(sentiment)
    print "Happiest state: " + str(max(state_happiness, key=state_happiness.get))
    print "Saddest state: " + str(min(state_happiness, key=state_happiness.get))
    print "Results saved in '" + filename + "'"

'''
    Estimates tweets per second
'''
def tweets_per_second():
    url = "https://stream.twitter.com/1/statuses/sample.json"
    parameters = []
    response = twitterreq(url, "GET", parameters)

    start = time()
    i=0
    for line in response:
        line = line.encode('ascii', 'replace')
        data = json.loads(line)
        if('text' in data):
            i = i + 1
        if(time() - start > 60):
            break
    
    return i

'''
    Loads the valence values from AFINN-111.txt into a dictionary

    Returns: Dictionary of valence values word->valence
'''
def load_valence():
    valence_dict = {}
    file = open("AFINN-111.txt", "r")

    for row in file:       
       valence = row.split('\t')
       valence_dict[valence[0]] = int(valence[1])   

    return valence_dict


'''
    Gets the sentiment of a particular tweet.

    Returns: Sentiment value
'''
def get_sentiment(tweet, valence_dict):
    sentiment = 0.0

    #TODO - Damping factor

    for x in tweet.split():
        if(valence_dict.has_key(x)):                
            sentiment += valence_dict[x]
        
        # Hash tags need special treatment, no damping factor here
        if(x[0] == '#'):
            for key in valence_dict:
                if(strip_accents(key) in x[0]):
                    sentiment += valence_dict[key]                
        
    return sentiment;             


'''
    Problem 2:
    Calculates sentiment index for the given query and page count

    query - String to query
    page_count - Number of pages of tweets to process
'''
def calculate_sentiment(query, page_count):
    base_url ="http://search.twitter.com/search.json"    
    page_url = base_url + "?q=" + query
    valence_dict = load_valence()

    # We need to return sentiment from  page_count * tweets_per_page tweets
    num_of_tweets = page_count * get_num_of_results(query)

    i = 0
    ignored_tweets = 0
    user_hash = {}
    sentiment_list = []
    while True:
        data = json.load(urllib.urlopen(page_url))

        if('next_page' not in data):
            # Wait for a while and start from page 0
            print "Ran out of pages, waiting for 10 secs ..."
            time.sleep(10)
            page_url = base_url + "?q=" + query              
            continue
        else: 
            page_url = base_url + data['next_page']

        for j in data['results']:
            user = j['from_user']
            tweet = j['text']

            if(strip_accents(user) in user_hash):
                # Ignore repeated tweets by same user
                ignored_tweets = ignored_tweets + 1
                continue

            sentiment = get_sentiment(tweet, valence_dict)        

            if(sentiment == 0.0):
                # Ignore tweets where we cannot infer sentiment
                ignored_tweets = ignored_tweets + 1
                continue

            user_hash[strip_accents(user)] = 1
            sentiment_list.append(sentiment)

            print user + ':' + "-->" + str(sentiment)
            i = i + 1
            if(i >= num_of_tweets):
                 break

        if(i >= num_of_tweets):
            break 

    print "\nNumber of page: " + str(page_count)
    print "Number of tweets: " + str(i)
    print "Ignored tweets: " + str(ignored_tweets)

    numpy_array = numpy.array(sentiment_list)
    
    print "Mean sentiment: " + str(numpy.mean(numpy_array))
    print "Std of sentiment: " + str(numpy.std(numpy_array))
    return


'''
    Problem 0:
    Returns number of tweets for given query.

    querystr - String to query
'''
def get_num_of_results(querystr):
    base_url = "http://search.twitter.com/search.json"
    page_url = base_url + "?q=" + querystr
    data = json.load(urllib.urlopen(page_url))
    return len(data['results'])

def main():
    usage = "Usage: %prog [[-q] [-s] [-p] query_term] [-i number_of_tweets] [-m number_of_hours] [-h|--help]"
    parser = OptionParser(usage=usage)
    parser.add_option("-q", "--query", 
                      dest="query", type="string",
                      help="Problem0: Get number of tweets")
    parser.add_option("-s", "--sentiment",
                      dest="sentiment", type="string",
                      help="Problem2: Sentiment for query term")
    parser.add_option("-p","--tweets_per_second",
                      dest="tps", default=False, action="store_true",
                      help="Problem3: Tweets per second for query term")
    parser.add_option("-i","--state-sentiment",
                      dest="statesentiment", type="int", 
                      help="Problem4: Find happy and sad states for the given  number of tweets")
    parser.add_option("-m","--measure_mood",
                      dest="measuremood", type="int",
                      help="Problem5: Measure mood for given number of hours")

    (options, args) = parser.parse_args()

    if(options.query):
        print "Number of tweets for query '" + options.query + "': " + \
            str(get_num_of_results(options.query))
    elif(options.sentiment):
        calculate_sentiment(options.sentiment, 10)
    elif(options.tps):
        tps = tweets_per_second()
        print("Sample tweets per second : " + str(tps/60.0))
        print("Estimated tweets per second: " + str(tps*100.0/60.0))
    elif(options.statesentiment is not None):
        state_sentiment(options.statesentiment)
    elif(options.measuremood is not None):
        measure_mood(options.measuremood)
    else:
        parser.error("Specify an action or '-h' for options");

if __name__ == '__main__':
    main()
                      

