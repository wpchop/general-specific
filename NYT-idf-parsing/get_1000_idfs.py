import sys
import os

path = os.getcwd()[:''.join(os.getcwd()).rfind('/')+1]                          #To reach ExternalDict.py in parent directory
sys.path.insert(0, path)

from ExternalDict import ExternalDict
from idfCalculator import idfCalculator


def get_dicts():
  '''Gets the word and idf dictionaties from the appropriate files.
  This won't work if they don't exist, btw.'''
  words = ExternalDict("word.dict")
  idfCalc = idfCalculator()
  idfs = idfCalc.get_idf_dict()
  return words, idfs
  
def sort_dict_by_value(dic):
  '''Given a dictionary, returns a list of its items sorted by the values, least
  to greatest.'''
  sort = sorted(dic.items(), key = lambda item:item[1])                         #Sort items by the value in each item[1]
  return sort
  
def sublist(lst, index, num):
  '''Given a list, returns <num> elements starting from <index>.'''
  return lst[index:(num+index)]
  
def match_ids(word_dict, lst):
  '''Given the word_dict and a list of tuples where tuple[0] is a value in 
  word_dict, returns a new list of tuples such that the key for the word_dict
  value is now in tuple[0] instead.'''
  word_tups = sort_dict_by_value(word_dict)
  new_tups = []
  for tup in lst:
    word = word_tups[ tup[0] - ExternalDict.STARTING_VALUE ][0]
    new_tups.append( (word, tup[1]) )
  return new_tups

def output_tups(tups, filename):
  '''Given a list of tuples, outputs them into a text file named <filename>.
  WARNING: Will overwrite files of the same name.'''
  outFile = open(filename,"w")
  num_tups_digits = len(str(len(tups)))                                         #Number of digits in the length of tups: If 1000 tups, it equals 4.
  for i, tup in enumerate(tups):
    s = " "*( num_tups_digits - (len(str(i))-1) )                               #s = correct number of spaces for formatting
    outFile.write( str(i+1)+'.'+s+tup[0]+':\t'+str(tup[1]) )                    #1. the:    0.03234
  print filename+" written."
  outFile.close()

def main():
  words, idfs = get_dicts()
  sort = sort_dict_by_value(idfs)
  low_idfs = sublist(sort,0,1000)
  noIDs = match_ids(words, low_idfs)
  output_tups(noIDs, "low_nyt_idfs.txt")


main()

'''
w = ExternalDict("w.txt")
w.add_list(['a','b','c'])
lst = [(1, .2), (2, .1), (3, .6)]
print match_ids(w, lst)
'''