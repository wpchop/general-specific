#-------------------------------------------------------------------------------
# Name:        idfCalculator.py
# Purpose: Class for idfCalculator that spits out calculations for a provided
#          word, using a count.dict ExternalDict.
# Authors: Bridget O'Daniel
# Created: 11/06/2015
# Acknowledgements:
#-------------------------------------------------------------------------------
from ExternalDict import ExternalDict
from math import log


class idfCalculator():
  
  def __init__(self):
    '''Creates an idfCalculator object that spits out idf calculations according
    to a count.dict ExternalDict file.'''
    self.count = ExternalDict("NYT/count.dict")
    self.tot_docs = self.count["totNumDocs"]
    del self.count['totNumDocs']
  
  def __getitem__(self, key): #idfCalc[key]
    '''Gets the value to match the given provided key.'''
    return self.idf(key)
    
  def __contains__(self, key): #key in idfCalc?
    '''Checks to see if idfCalculator contains the given key. Returns True or False.'''
    return (key in self.count)
    
  #---------------- Get Methods ------------------------------------------------
    
  def get_tot_docs(self):
    '''Returns the total number of documents the idf takes into account.'''
    return self.tot_docs
    
  def get_idf_dict(self):
    '''Returns a dictionary {wordID:idf}, as it currently stands.'''
    idf_dict = {}
    for wordID in self.count:
      idf_dict[wordID] = self.idf(wordID)
    return idf_dict
    
  #---------------- IDF Methods ------------------------------------------------
    
  def idf(self, wordID):
    '''When given a wordID, returns the idf of that word.
    pre: wordID is an int representing a word.
    post: Returns a float.'''
    tot = self.get_tot_docs()
    count = self.count[wordID] if wordID in self.count else 0                   #If word is in our dict, use its count. Else, we HAVE seen it 0 times.
    return self.__idf(tot, count)
    
  def __idf(self, num_docs, num_with_term):
    '''Actually calculates the idf.'''
    return log(int(num_docs)/(float(num_with_term)+1))  #+1 for smoothing in case of word not in count.dict