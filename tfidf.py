import math
import os.path
import collections
import ExternalDict
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

#----------------------------- Word Dict ---------------------------------------

def get_word_list(data):
  '''Gets a list of every word contained in the data's sentences. Returns the list.'''
  return (" ".join( data )).lower().split()

#-------------------------------------------------------------------------------

def calc_freq(input_lines, chars):
    idf_dict = get_idfs()
    words = ExternalDict("word_dict.txt") #Uploads the word dictionary, an ExternalDict object
    count = {}                            #map word number to frequency
    string = ""
    total = len(input_lines)              #total number of sentences
    termfreqlist = []
    labels = []
    sentences = []
    for line in input_lines:
        document = str(line[3])
        document = document[1:-1]
        sentences.append(document)
        sent = document.split(" ")
        labels.append(line[4])
    words.add_list( get_word_list(sentences) )
    for sent in sentences:
        termfreq = {}
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
    for i, termfreq in enumerate(termfreqlist):
        string+= labels[i]
        for term in termfreq:
            #print total/count[term]
            if term in idf_dict:
              string+= " " + str(term) + ":" + str(termfreq[term]*idf_dict[term])
            else:
              string+= " " + str(term) + ":" + str(termfreq[term]*math.log(1.0*total))
        string+= "\n"
        """
        for word in sent:
	          if word not in chars:
	              print word + str(words[word]) + "count " + str(count[words[word]])
	              string+= " " + str(words[word]) + ":" + str(math.log10(total/count[words[word]]))
        string+= "\n"
        """
    words.save() #Updates the output dictionary
    return string
    
    
    
#---------------------IDF Collection-----------
def write_idfs_to_file(num_docs, wordID_to_total_freq): #WordID_to_total_freq = WordID : num docs in which it occurs
    outFile = open("idf_dict.txt","w")
    for item in wordID_to_total_freq.items():
      outFile.write(str(item[0])+">x<"+str(math.log((1.0*num_docs/item[1])+1))+"\t")
    outFile.close()
  
def get_idfs():
  return ExternalDict("idf_dict.txt")
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
