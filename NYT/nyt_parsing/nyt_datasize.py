import sys, os
import numpy as np
import matplotlib.pyplot as plt
#sys.path.insert( 0, os.path.abspath(os.path.join(sys.path[0], os.pardir)) )     #To reach parent directory
from ExternalDict import ExternalDict
from idfCalculator import idfCalculator

'''
1. Get number of entries in count.dict
2. Get number of entries discounting all values < 5
3. Get number of entries discounting all values < 100
'''

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False


def sort_dict_by_value(dic):
  '''Given a dictionary, sorts its items from least to greatest and returns a 
  list of these sorted key:value tuples.'''
  try:
    return sorted(dic.items(), key = lambda item:float(item[1]))
  except:
    return sorted(dic.items(), key = lambda item:item[1])


def secondElem_greater_than(num, tup):
  '''Given a number and a tuple, returns whether the second element in the tuple
  is greater than the provided number.
  post: returns True or False.'''
  return float(tup[1]) > num


def num_entries(count, minimum=0):
  '''Given a count.dict ExternalDict and and a minimum, returns the number of 
  entries in count that have a value greater than the provided minimum value.'''
  if minimum == 0 or minimum == 1:
    return int(count['totNumDocs']) - 1
  else:
    if 'totNumDocs' in count:
      del count.dict["totNumDocs"]
    items = sort_dict_by_value(count)
    matching = filter(lambda tup: secondElem_greater_than(minimum, tup), items)
    return len(matching)


def main():
  count = ExternalDict('count.dict')
  totNumDocs = count['totNumDocs']
  #entriesTot = num_entries(count)
  #entries5 = num_entries(count, 5)
  #entries100 = num_entries(count, 100)
  count['totNumDocs'] = totNumDocs
  #print entriesTot, entries5, entries100
  
main()