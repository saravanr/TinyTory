import config
import oauth2 as oauth
import urllib2 as urllib

class twitterclient:

    ##########
    _debug = 0
    ##########

    oauth_token    = oauth.Token(key=config.ACCESS_TOKEN_KEY, secret=config.ACCESS_TOKEN_SECRET)
    oauth_consumer = oauth.Consumer(key=config.CONSUMER_KEY, secret=config.CONSUMER_SECRET)
    signature_method_hmac_sha1 = oauth.SignatureMethod_HMAC_SHA1()
    http_method = "GET"
    http_handler  = urllib.HTTPHandler(debuglevel=_debug)
    https_handler = urllib.HTTPSHandler(debuglevel=_debug)

    '''
        Construct, sign, and open a twitter request
        using the hard-coded credentials above.
    '''
    def twitterreq(self, url, method, parameters):
        req = oauth.Request.from_consumer_and_token(self.oauth_consumer,
                token=self.oauth_token,
                http_method=self.http_method,
                http_url=url, 
                parameters=parameters)
    
        req.sign_request(self.signature_method_hmac_sha1, self.oauth_consumer, self.oauth_token)
        headers = req.to_header()
    
        if self.http_method == "POST":
            encoded_post_data = req.to_postdata()
        else:
            encoded_post_data = None
            url = req.to_url()
    
        opener = urllib.OpenerDirector()
        opener.add_handler(self.http_handler)
        opener.add_handler(self.https_handler)
    
        response = opener.open(url, encoded_post_data)
        return response
    

