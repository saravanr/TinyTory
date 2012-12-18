import unicodedata


class valence:
    
    '''
        Loads the valence values from AFINN-111.txt into a dictionary
    
        Returns: Dictionary of valence values word->valence
    '''
    valence_dict = None
    def load_valence(self):
        self.valence_dict = {}
        file = open("AFINN-111.txt", "r")
    
        for row in file:       
           valence = row.split('\t')
           self.valence_dict[valence[0]] = int(valence[1])   
        return
    
    def get_sentiment(self, string):
        sentiment = 0.0
    
        #TODO - Damping factor
    
        for x in string.split():
            if(self.valence_dict.has_key(x)):                
                sentiment += self.valence_dict[x]
            
            # Hash tags need special treatment, no damping factor here
            if(x[0] == '#'):
                for key in self.valence_dict:
                    if(self.strip_accents(key) in x[0]):
                        sentiment += self.valence_dict[key]                
            
        return sentiment;             

    '''
    Used for stripping accent characters
    '''
    def not_combining(self, char):
        return unicodedata.category(char) != 'Mn'
    
    
    '''
        Strips accents from unicode strings
    '''
    def strip_accents(self, s):
        unicode_text = unicodedata.normalize('NFD', s.decode('cp1252'))
        return filter(self.not_combining, unicode_text).encode('ascii', 'ignore')

    def __init__(self):
        self.load_valence()
