#-------------------------------------------------------------------------------
# Name:        ExternalDict.py
# Purpose: Creates ExternalDict objects for reading, using, and writing externally
#          stored dictionaries to store constants.
# Authors: Bridget O'Daniel, Wenli Zhao, Lily Wu
# Created: 10/06/2015
# Acknowledgements: Aaron Hall for merge_dicts: http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression
#-------------------------------------------------------------------------------
import os.path
from sets import Set


def merge_dicts(*dict_args):
    '''Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.'''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


class ExternalDict(object):
  '''Creates an ExternalDict object to handle a constant dictionary needed for the 
  creation of files to be read by the GenSpec classifier.'''
  
  def __init__(self, fname):
    '''Creates an ExternalDict object. Reads from a file "fname" if it exists, 
    otherwise the dictionary starts off empty.
    pre: fname is a string containing a filename. If a file exists by that name, it
    must be in the form of an ExternalDict file.
    ED form: "key>x<value\t" per entry in file -> key:value pair'''
    self.fname = fname
    self.dict = {}                  #Default
    self.upload()
    
#-------------------------- Operator Overloading ---------------------------------#

  def __len__(self):  #len(ED)
    '''Gets the current length of the External Dict object.'''
    return len(self.dict)
    
  def __str__(self):  #str(ED) and print ED
    '''Gets the string representation of the External Dict object.'''
    return "External Dict "+self.fname+": \n"+str(self.dict)
    
  def __getitem__(self, key): #ED[key]
    '''Gets the value to match the given provided key.'''
    return self.dict[key]
  
  def __setitem__(self, key, value): #ED[key] = new_value
    '''Sets the value at key in the External Dict.'''
    self.dict[key] = value

  def __iter__(self): #Allows for iteration
    '''Gets an interation object for the ED, over the keys.'''
    return self.dict.iterkeys()
    
  def __contains__(self, key): #key in ED?
    '''Checks to see if ED contains the given key. Returns True or False.'''
    return (key in self.dict)
    
#-------------------------- Basic Dictionary Tasks -------------------------------#

  def keys(self):
    '''Gets the ED's keys.'''
    return self.dict.keys()
    
  def values(self):
    '''Gets the ED's values.'''
    return self.dict.values()
    
  def items(self):
    '''Gets the ED's items.'''
    return self.dict.items()

#------------------------- Specific to External Dict -----------------------------#

#-------------Reading File
  def is_external_dict_exist(self):
    '''Checks if a file for the External Dict exists and returns True or False.'''
    return os.path.isfile(self.fname)


  def upload(self):
    '''Looks for an External Dict to upload that information to the dictionary.
    If no such file exists, assumes the dictionary is empty.
    post: Fills the ED's dictionary with any information in the file.'''
    if self.is_external_dict_exist():
      self.read_external_dict()
    else:
      self.dict = {}


  def read_external_dict(self):
    '''Reads the External Dict file, building the dictionary it contains into the ED
    object's dictionary. Merges with current key-value pairs in the ED, but overwites
    with newest information if the same key is found.'''
    ed = {}
    dictFile = open(self.fname, "r")
    lines = dictFile.readlines()
    items = lines[0].strip().split("\t")
    for item in items:
      pair = item.split(">x<")
      ed[pair[0]] = pair[1]
    dictFile.close()
    self.dict = merge_dicts(self.dict, ed)

#--------------Altering ED
  def add_pair(self, pair):
    '''Adds the key:value pair in the tuple to the ED.
    pre: pair is a tuple of length 2'''
    self.dict[pair[0]] = pair[1]
    
    
  def add_dict(self, dictionary):
    '''Takes in a dictionary and adds its key:value pairs to the ED. Combines with
    previus contents of ED, overwriting with any new values for a particular key.'''
    self.dict = merge_dicts(self.dict, dictionary)
    
    
  def add_list(self, lst):
    '''Takes in a list and adds each item as a key with a unique id as the value.
    WARNING: ID is only unique for items added through THIS METHOD. Manually adding a
    pair with the same value as another is still possible.'''
    for item in lst:  #For each item not already a key, add it with a unique ID
      if item in self:
        pass
      else:
        self[item] = len(self) + 1 #length of the dict at that point is the unique ID
    
    
  def empty_dict(self):
    '''Completely resets the dictionary to empty.'''
    self.dict = {}
    
    
  def get_key_set(self, lst=[]):
    '''Takes in a list of keys and returns a set of those keys AND those already in
    the ED with duplicates removed
    pre: string is a String
    post: returns an unordered, no duplicate set of strings'''
    return Set(lst.extend(self.keys()))                  #Adds on words already in dictionary, removes duplicates and randomizes order

#--------------Storing ED
  def save(self):
    '''Saves the External Dict to a file for reuse in other data gathering ventures.
    post: Outputs a file with the name of self.fname where the key:value pairs are 
    listed as follows: key:vakue\key:value...
    WARNING: Overwrites any file by the same name.'''
    outFile = open(self.fname,"w") #Empties whatever was previously in the file
    for item in self.items():
      outFile.write(str(item[0])+">x<"+str(item[1])+"\t")
    print self.fname+" written."
    outFile.close()