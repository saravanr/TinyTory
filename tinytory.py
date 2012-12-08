#!/usr/bin/python
import json
import oauth2 as oauth
import urllib2 as urllib

# See Assginment 6 instructions or README for how to get these credentials
access_token_key = "30362328-SJiPXWJJhOqsAgDi9ub7TAxcnkiRaaBnBpsob1xC0"
access_token_secret = "KUVVur5jpvxRCMZztwCM0E8k9G9byZsFhcvc89frL8"
consumer_key = "mrr3DkdWp8HkfcS1Z4BNrA"
consumer_secret = "DKa3mJRcqbLEhnchDEneSgUMdJ3wKIPvozg7ZzJW0fU"

_debug = 0

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

def fetchsamples():
  url = "https://stream.twitter.com/1/statuses/sample.json"
  parameters = []
  response = twitterreq(url, "GET", parameters)

  for line in response:
    print line.strip()


def load_valence():
    """
    Loads the valence values from AFINN-111.txt into a dictionary

    Returns: Dictionary of valence values word->valence
    """
    valence_dict = {}
    file = open("AFINN-111.txt", "r")

    for row in file:       
       valence = row.split('\t')
       valence_dict[valence[0]] = int(valence[1])   

    return valence_dict

def get_sentiment(tweet, valence_dict):
    """
    Gets the sentiment of a particular tweet.

    Returns: Sentiment value
    """
    sentiment = 0.0

    #TODO - Damping factor

    for x in tweet.split():
        if(valence_dict.has_key(x)):                
            sentiment += valence_dict[x]
        
        # Hash tags need special treatment, no damping factor here
        if(x[0] == '#'):
            for key in valence_dict:
                if(key in x[0]):
                    sentiment += valence_dict[key]                
        
    return sentiment;             

def process_tweets(query, page_count):

    base_url ="http://search.twitter.com/search.json"    
    page_url = base_url + "?q=" + query;
    valence_dict = load_valence()

    for i in range (0, page_count):
        data = json.load(urllib.urlopen(page_url))
        page_url = base_url + data['next_page']
        print "Number of tweets for query" + 
        "'" + query + "'" + str(len(data['results']))

        for j in data['results']:
            user = j['from_user']
            tweet = j['text']
            sentiment = get_sentiment(tweet, valence_dict)        
            print user + ':' + tweet + "-->" + str(sentiment)
    return


if __name__ == '__main__':
  #fetchsamples()  
  process_tweets('microsoft', 5)

