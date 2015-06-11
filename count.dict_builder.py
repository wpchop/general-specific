#-------------------------------------------------------------------------------
# Name:        count.dict_builder.py
# Purpose: Uses an ExternalDict to store found count values for words in many
#          documents. Helpful for idf calculation. The dictionary is:
#          - wordID : #documents-appeared-in
#          - "totNumDocs" : #documents-used     <- SPECIAL KEY
# Authors: Bridget O'Daniel, Wenli Zhao, Lily Wu
# Created: 11/06/2015
# Acknowledgements:
#-------------------------------------------------------------------------------

import math
from sets import Set
from gather import gather_data
from ExternalDict import ExternalDict

#--------------------- String Business -----------------------------------------

def list_to_words(sentences):
  '''Turns a list of sentences (strings) into a list of words and returns them.'''
  return " ".join(sentences).lower().split()


def get_words(string):
  '''Turns a string into a list of words.'''
  return string.lower().split()


def get_strings(data_dict):
  '''Given a data dictionary (output from gather()), combs for all sentences and returns
  a simple list containing the strings of the sentences.'''
  sentences = []
  for data in data_dict.values():
    if type(data) is list:
      map(sentences.append, [tup[1] for tup in data])
    else:
      map(sentences.append, [sent for sent in data.get_sentences_as_strings()])
  return sentences

#--------------------- Word Dictionary -----------------------------------------

def find_new_words(sentences, word_dict):
  '''Adds any new words in the sentences into the word_dictionary with unique ids.'''
  words = Set(list_to_words(sentences))  #gets all words with no duplicates as a set
  new = []
  for word in words:
    if word not in word_dict:
      new.append(word)
  return new


def add_new_words(sentences, word_dict):
  '''Adds all words in sentences but not yet in the word_dict to word_dict and returns it.'''
  new = find_new_words(sentences, word_dict)
  word_dict.add_list(new)
  return word_dict

#--------------------- Update Count Dict ---------------------------------------

def __update_count_dict(docs, count_dict, word_dict):
  '''Takes in a list of tokenized documents and two dictionaries. Updates the first dictionary,
  associating each word's ID with the number of documents that contains it.
  pre: docs is a list of strings, count_dict and word_dict are ExternalDicts,
  {wordID:int} and {"word":wordID}, respectively.
  WARNING: All words in docs MUST be in word_dict. Use add_new_words() before 
  calling this function.
  post: Returns a dictionary {wordID:int}'''
  for doc in docs:
    doc = get_words(doc)                    #string -> list of terms
    words = Set(doc)                        #Removes duplicate words
    for word in words:                      #For each word in the doc,
      if word_dict[word] in count_dict:       #If it's been seen in another doc, add 1
        count_dict[ word_dict[word] ] += 1
      else:                                   #If it's not been seen, add its ID as a key
        count_dict[ word_dict[word] ] = 1
  return count_dict
  
  
def update_count_dict(docs, count_dict, word_dict):
  '''Updates the count_dict to reflect the new documents.
  pre: docs is a list of tokenized documents (strings), count_dict and word_dict 
  are ExternalDicts, {wordID:int} and {"word":wordID}, respectively.
  WARNING: All words in docs MUST be in word_dict. Use add_new_words() before 
  calling this function.
  post: Returns an ExternalDict count_dict.'''
  count_dict = update_num_docs(count_dict, len(docs))
  return __update_count_dict(docs, count_dict, word_dict)
  
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
  
#--------------------- Main ----------------------------------------------------

def main():
  docs = get_strings( gather_data() )                     #Docs is a list of all sentences (strings)
  count_dict = ExternalDict("count.dict")                 #count_dict special key: "totNumDocs":total number of docs accounted for
  word_dict = ExternalDict("word.dict")
  
  word_dict = add_new_words(docs, word_dict)
  count_dict = update_count_dict(docs, count_dict, word_dict)
  word_dict.save()
  count_dict.save()
  
main()