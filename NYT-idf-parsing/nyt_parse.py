import os, sys
from sets import Set
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.abspath(os.path.join(sys.path[0], os.pardir)))       #Inserting parent directory into path to reach ExternalDict
from ExternalDict import ExternalDict


outer_path = "/project/cis/nlp/data/corpora/nytimes/data"

#------------------ Folder Navigation ------------------------------------------

def get_immediate_folders(a_dir):
  '''Returns a list of all the subfolders within the current one, as a list of 
  strings.'''
  names = []
  for name in os.listdir(a_dir):
    if os.path.isdir(os.path.join(a_dir, name)):
      names.append(name)
  return names


def add2path(folder, path):
  '''Given two strings, the folder name and the current path, adds the folder to
  the path, returning the combined string.'''
  return path+"/"+folder


#------------------ Parsing XML Docs -------------------------------------------
#Body xmlPath: /nitf/body/body.content/block[@class="full_text]

def xml_tree(filename):
  '''Takes in a .xml filename (extension included) and returns the xml tree's 
  root and tree as a tuple (tree, root).'''
  tree = ET.parse(filename)
  return ( tree, tree.getroot() )

def get_text(tree, root):
  '''Given an xml tree and the root at the highest node, returns the body of the
  article as a string. Enjoy.'''
  text = ""
  for body in root.iter("body.content"):
    for cls in body:
      if cls.get("class") == 'full_text':
        for paragraph in cls:
          text += paragraph.text+"\n"
        break
  return text

def is_not_number(s):
  try:
    float(s)
    return False
  except ValueError:
    return True

def tokenize(string):
  '''Given a string, deletes all the punctuation in it.'''
  noPunct = ""
  last_char = "q"
  for char in string:
    if char == '-':
      char = ' '
    if not char.isalnum() and not char.isspace():
      pass
    elif char.isspace() and last_char.isspace():
      pass
    else:
      noPunct += char
      last_char = char
  noPunct = noPunct.lower().split()
  tokens = filter(is_not_number, noPunct)
  return tokens


#--------------------- Word Dictionary -----------------------------------------

def find_new_words(doc, word_dict):
  '''Adds any new words in the doc into the word_dictionary with unique ids.
  pre: doc is a list of tokens and word_dict is an ExternalDict'''
  words = Set(doc)  #gets all words with no duplicates as a set
  new = []
  for word in words:
    if word not in word_dict:
      new.append(word)
  return new


def add_new_words(doc, word_dict):
  '''Adds all words in doc but not yet in the word_dict to word_dict and returns it.'''
  new = find_new_words(doc, word_dict)
  word_dict.add_list(new)
  return word_dict


#--------------------- Update Count Dict ---------------------------------------

def __update_count_dict(doc, count_dict, word_dict):
  '''Takes in a tokenized document and two dictionaries. Updates the first dictionary,
  associating each word's ID with the number of documents that contains it.
  pre: docs is a list of tokens, count_dict and word_dict are ExternalDicts,
  {wordID:int} and {"word":wordID}, respectively.
  WARNING: All words in docs MUST be in word_dict. Use add_new_words() before 
  calling this function.
  post: Returns a dictionary {wordID:int}'''
  words = Set(doc)                        #Removes duplicate words
  for word in words:                      #For each word in the doc,
    if word_dict[word] in count_dict:       #If it's been seen in another doc, add 1
      count_dict[ word_dict[word] ] += 1
    else:                                   #If it's not been seen, add its ID as a key
      count_dict[ word_dict[word] ] = 1
  return count_dict
  
  
def update_count_dict(doc, count_dict, word_dict):
  '''Updates the count_dict to reflect the new document.
  pre: doc is a list of tokens, count_dict and word_dict 
  are ExternalDicts, {wordID:int} and {"word":wordID}, respectively.
  WARNING: All words in docs MUST be in word_dict. Use add_new_words() before 
  calling this function.
  post: Returns an ExternalDict count_dict.'''
  count_dict = update_num_docs(count_dict, 1)
  return __update_count_dict(doc, count_dict, word_dict)
  
  
#--------------------- Total Document Calculations -----------------------------

def get_count_tot_docs(count_dict):
  '''The count_dict has a special string key "totNumDocs" that is associated with the number of docs the dictionary has analyzed.
  Returns the int value of this key. If it is a blank count_dict, returns 0.'''
  if "totNumDocs" in count_dict:
    return count_dict["totNumDocs"]
  return 0
  

def update_num_docs(count_dict, num_new_docs):
  '''Updates the special key "totNumDocs" with the new documents being analyzed.
  pre: count_dict is a dictionary {wordID:int} and num_new_docs is int.
  post: returns the updated count_dict.'''
  if "totNumDocs" in count_dict:
    count_dict["totNumDocs"] += num_new_docs
  else:
    count_dict["totNumDocs"] = num_new_docs
  return count_dict
  
  
#------------------ MAIN -------------------------------------------
#/nitf/body/body.content/block[@class="full_text"]


'''CLOUD9 TESTING
count_dict = ExternalDict("count.dict")                 #count_dict special key: "totNumDocs":total number of docs accounted for
word_dict = ExternalDict("word.dict")
  
for folder in get_immediate_folders(os.getcwd()):
  path = add2path(folder, os.getcwd())
  for file in os.listdir(path):
    tree, root = xml_tree( add2path(file, path) )
    tokens = tokenize( get_text(tree,root) )
    
    word_dict = add_new_words(tokens, word_dict)
    count_dict = update_count_dict(tokens, count_dict, word_dict)
    
word_dict.save()
count_dict.save()
 '''
    
def main():
  count_dict = ExternalDict("count.dict")                 #count_dict special key: "totNumDocs":total number of docs accounted for
  word_dict = ExternalDict("word.dict")
  
  
  for year_folder in os.listdir(outer_path):                  #1987
    year_path = add2path(year_folder, outer_path)
    
    for month_folder in get_immediate_folders(year_path):     #month (has .tzg files in here)
      month_path = add2path(month_folder, year_path)
      
      for day_folder in get_immediate_folders(month_path):    #day
        day_path = add2path(day_folder, month_path)
        #.xml files are here
        for file in os.listdir(day_path):
          file_path = add2path(file, day_path) 
          print file_path
          tree, root = xml_tree( file_path )
          tokens = tokenize( get_text(tree,root) )
          
          word_dict = add_new_words(tokens, word_dict)
          count_dict = update_count_dict(tokens, count_dict, word_dict)
          
          
  word_dict.save()
  count_dict.save()
  
#main()