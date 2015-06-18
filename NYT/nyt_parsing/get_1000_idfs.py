import sys, os
sys.path.insert( 0, os.path.abspath(os.path.join(sys.path[0], os.pardir)) )     #To reach ExternalDict.py in parent directory

from ExternalDict import ExternalDict
from idfCalculator import idfCalculator

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False

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
  word_tups = sorted(word_dict.items(), key = lambda item:float(item[1]))
  new_tups = []
  for tup in lst:
    if is_number(tup[0]):
      word = word_tups[ int(tup[0]) - ExternalDict.STARTING_VALUE ][0]
      new_tups.append( (word, tup[1]) )
  return new_tups

def find_longest_word(tups):
  '''Given the list of tups, compares the length of tup[0] for each tuple, returning
  the max length found (int).'''
  lst = sorted(tups, key= lambda tup:len(tup[0]), reverse=True)
  return len(lst[0][0])

def calc_spaces(s, mx):
  '''Given the string to print and the length of the longest word to output, will 
  return a string with the desired number of spaces for even output.'''
  return " "*((mx - len(s)) + 1)

def output_tups(tups, filename):
  '''Given a list of tuples, outputs them into a text file named <filename>.
  WARNING: Will overwrite files of the same name.'''
  outFile = open(filename,"w")
  num_tups_digits = len(str(len(tups)))                                            #Number of digits in the length of tups: If 1000 tups, it equals 4.
  mx = find_longest_word(tups)                                                     #Max word length
  for i, tup in enumerate(tups):
    s = " "*( num_tups_digits - len(str(i+1)) )                                    #s = correct number of spaces for formatting
    outFile.write( str(i+1)+'.'+s+tup[0]+calc_spaces(tup[0], mx)+"{0:.5f}".format(tup[1])+'\n' )                    #1. the:    0.03234
  print filename+" written."
  outFile.close()

def main():
  words, idfs = get_dicts()
  sort = sort_dict_by_value(idfs)
  low_idfs = sublist(sort,0,1001)
  noIDs = match_ids(words, low_idfs)
  output_tups(noIDs, "low_nyt_idfs.txt")

main()

'''
lst = [('a', 0), ('bid', 1), ('ec', 2)]
print find_longest_word(lst)
'''