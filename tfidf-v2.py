import collections
import math
import os.path
from sets import Set
from collections import OrderedDict

def get_input_file_lines(fname):
    """Returns a list of the lines from the given input file name, leaving off
    the first line of the file."""
    inputFile = open(fname, "r")
    inputlines = inputFile.readlines()              #reads lines
    inputFile.close()
    return inputlines

def lower(x):
  return x.lower()
"""
def calc_freq(input_lines, chars):
    words = {}
    frequency = {}
    string = ""
    for line in input_lines:
        count = {}
        document = str(line[3])
        document = document[1:-1]
        sent = document.split(" ")
        label = line[4]
        string+= label
        for word in sent:
            if word not in chars:
                if word in words.keys():
                    if words[word] in count.keys():
                        count[words[word]] += 1
                    else:
                        count[words[word]] = 1
                else:
                    words[word] = len(words)
                    count[words[word]] = 1
        od = collections.OrderedDict(sorted(count.items()))
        l = od.items()
        for pair in l:
            string += " " + str(pair[0]) + ":" + str(pair[1])
        string += "\n"
    return string
"""

#---------------------------------------------------------------------------------------
def is_word_dict_exist():
  '''Checks if a file named "word_dict.txt" exists and returns True or False.'''
  return os.path.isfile("word_dict.txt") 


def upload_word_dict():
  '''Looks for a file named "word_dict.txt" to upload that information to the dictionary.
  If no such file exists, assumes the dictionary is empty. Returns the filled word_dict
  and the highest id number found.
  post: Returns a tuple (word_dict, i) such that word_dict is a dictionary of the form
  "word":ID and i is the highest ID in the dictionary.'''
  if is_word_dict_exist():
    return read_word_dict_txt()
  else:
    return {}


def read_word_dict_txt():
  '''Reads a "word_dict.txt" file, building the dictionary it contains and returning
  that dictionary.
  post: Returns word_dict, a dictionary of the form "word":ID '''
  word_dict = {}
  dictFile = open("word_dict.txt", "r")
  items = dictFile.readlines()[0].strip().split("\t")
  for item in items:
    pair = item.split(">x<")
    word_dict[pair[0]] = int(pair[1])
  dictFile.close()
  return word_dict


def get_list_of_all_sentences(task_dict):
  '''Returns a list of all sentences from all tasks.'''
  sentences = []
  for task in task_dict.values():
    for sent in task.get_sentences():
      sentences.append( sent.get_sent() )
  return sentences


def get_word_set(word_dict, sentences):
  '''Takes in a list of sentences (strings) and returns a set of
  all words making up those sentences.
  pre: sentences is a list of strings
  post: returns an unordered, no-duplicates set of strings'''
  words_ls = " ".join(sentences).lower().split()#Makes a big string then breaks @ spaces
  words_ls.extend(word_dict.keys())             #Adds on words already in dictionary
  words_s = Set(words_ls)					              #Removes duplicates and randomizes order
  return words_s


def __build_word_dict(word_dict, sentences):
  '''Fills the given dictionary with the individual words in the given
  list of sentences, and returns the full dictionary.
  pre: word_dict = {} or {"word": wordID}, sentences = list of strings}
  post: Returns word_dict, in format above.'''
  words = get_word_set(word_dict, sentences)
  maxi = get_max_id(word_dict)
  for word in words:		    #For each word not already in it, adds it to the dictionary with a unique id
    if word in word_dict:
      pass
    else:
      maxi += 1               #Prepares for the id
      word_dict[word] = maxi
  return word_dict


def get_max_id(word_dict):
  '''Returns the maximum value of the dictionary's value set.'''
  if word_dict == {}:
    return -1                               #So that next id is 0
  else:
    return sorted(word_dict.values())[-1]   #Sort the IDs, get the highest from off the end


def update_word_dict(sentences, word_dict):
  '''Creates a word dictionary such that {"word": wordID (int)} from the provided
  dictionary of tasks, {taskID:Task}. Adds to a dictionary in a "word_dict.txt" file
  or if none, from scratch.
  post: Returns the updated word_dict.'''
  word_dict = __build_word_dict(word_dict, sentences)                 #Adds any new words
  return word_dict


def output_word_dict(word_dict):
  '''Outputs word_dict to a file for reuse in other data gathering ventures.
  pre: word_dict is a dictionary such that "word":wordID
  post: Outputs a file "word_dict.txt" where the words are listed--> word:ID\tword:ID...
  WARNING: Overwrites any file by the same name.'''
  outFile = open("word_dict.txt","w")
  for item in word_dict.items():
    outFile.write(item[0]+">x<"+str(item[1])+"\t")
  outFile.close()
#---------------------------------------------------------

def calc_freq(input_lines, chars):
    words = upload_word_dict()
    count = {}                           #map word number to frequency
    string = ""
    total = len(input_lines)             #total number of sentences
    termfreqlist = []
    labels = []
    sentences = []
    for line in input_lines:
        document = str(line[3])
        document = document[1:-1]
        sentences.append(document)
        sent = document.split(" ")
        termfreq = {}
        labels.append(line[4])
    words = update_word_dict(sentences, words)
    for sent in sentences:
        for word in sent.lower().split():
            if word not in chars:
                if words[word] in termfreq:
                    termfreq[words[word]]+= 1
                else:
                    termfreq[words[word]] = 1
        for word in Set(sent.lower().split()):
            if word not in chars:
              if words[word] in count:
                  count[words[word]] += 1
              else:
                  count[words[word]] = 1
            
        tf = collections.OrderedDict(sorted(termfreq.items()))
        termfreqlist.append(tf)
    od = collections.OrderedDict(sorted(count.items()))
    l = od.items()
    for i, termfreq in enumerate(termfreqlist):
        string+= labels[i]
        for term in termfreq:
            #print total/count[term]
            string+= " " + str(term) + ":" + str(termfreq[term]*math.log(1.0*total/count[term]))
        string+= "\n"
        """
        for word in sent:
	          if word not in chars:
	              print word + str(words[word]) + "count " + str(count[words[word]])
	              string+= " " + str(words[word]) + ":" + str(math.log10(total/count[words[word]]))
        string+= "\n"
        """
    write_idfs_to_file(total, count) #DELETE ME SOON
    output_word_dict(words) #Updates the output dictionary
    print find_one_freq(count)
    print len(count)
    return string
    
    
    
#---------------------IDF Collection-----------
def write_idfs_to_file(num_docs, wordID_to_total_freq): #WordID_to_total_freq = WordID : num docs in which it occurs
    outFile = open("idf_dict.txt","w")
    for item in wordID_to_total_freq.items():
      outFile.write(str(item[0])+">x<"+str(math.log((1.0*num_docs/item[1])+1))+"\t")
    outFile.close()
  
def get_idfs():
  idf_dict = {}
  idfFile = open("idf_dict.txt", "r")
  items = idfFile.readlines()[0].strip().split("\t")
  for item in items:
    pair = item.split(">x<")
    idf_dict[pair[0]] = int(pair[1])
  idfFile.close()
  return idf_dict
#-----------------------------------------------

def split_lines(input_lines):
    lines = []
    for line in input_lines:
        line = line.split("\t")
	lines.append(line)
    return lines
    
def find_one_freq(count):
    vals = count.values()
    cnt = 0
    for v in vals:
        if v > 5:
            cnt+=1
    return cnt   
         
def main():
    input_fname = raw_input("Enter the input file name: ")
    input_lines = get_input_file_lines(input_fname)                             #Get lines from .input file
    input_lines = split_lines(input_lines)
    chars = list("!@#$%^&*()_+-=[]{};:'\".>,</?\|")		#characters that should not be words
    frequencies = calc_freq(input_lines, chars)                                        
    outFile = open("trainingTEST.txt", "w")
    outFile.write(frequencies)
    outFile.close()
    return frequencies

main()
