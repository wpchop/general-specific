from parse_turk_data import main
from math import *
import collections
import itertools

def lower(x):
  return x.lower()

def build_dict(docs, chars):	#@param list of sentences (string), stop tokens
  words = {}			#key = string, val = integer (unique ID of word)
  for doc in docs:
    for word in map(lower, doc.split(" ")):
      if word not in words.keys() and word not in chars:
        words[word] = len(words)
  return words
      
def det_class(label):		#@param string
  if label == "gen":
    return 1
  elif label == "spec":
    return -1

#------------------FEATURES-----------------------------------------------

def find_idf(word, docs):	#@param string, [string]
  n = len(docs)			#total number of docs/sentences
  p = 0				#keeps track of how many docs have the word
  for doc in docs:
    doc = doc.lower()
    if word in doc.split():
      p+=1
  if p == 0:
    return 1
  else:
    return log10(n/p)

def find_freqs(words, sent):
  count = {}				#word_ID(int): freq(int)
  for word in map(lower, sent.split(" ")):
    if word in words.keys():
      count[words[word]] += 1
    else:
      words[word] = len(words)
      count[words[word]] = 1
  return count

#-----------------------------FORMATTING-----------------------------------
def format_line(words, sentence, label, weights):	
  '''@param {string:int}, string, [string], int, {string: float}
  each word: unique ID, sentence, stop words, 1=gen, -1=spec, token ID :weight
  can be used to format test sentences'''

  string = str(label)
  od = collections.OrderedDict(sorted(weights.items()))
  l = od.items()
  for pair in l:
    string += " " + str(pair[0]) + ":" + str(pair[1])
  string+="\n"
  return string

def format_tasks(words, tasks, outFile):
  training_set = []					#list of exact strings to write to outFile
  #words = {}						#key = "word" value = unique int ID
  chars = list("!@#$%^&*()_+-=[]{};:'\".>,</?\|")	#stop words
  all_sents = []					#all the sentences in all tasks (strings)
  all_labels = []
  idfs = {}

  for task_key in tasks:
    task = tasks[task_key]
    sentences = task.get_sentences()
    for sent in sentences:
      all_sents.append(sent.get_sent())
      avg_scale = sum(int(i[0]) for i in sent.get_scales())/len(sent.get_scales())
      clas = 0						#0 = mixed, -1 = spec, 1 = gen
      if avg_scale < 3:
        clas = -1
      elif avg_scale == 3:
        clas = 0
      else:
        clas = 1
      all_labels.append(clas)
  for word in words.keys():
    print word
    idfs[words[word]] = find_idf(word, all_sents)

  for i in range(len(all_sents)):
    sent = all_sents[i]
    label = all_labels[i]
    #word_freqs = find_freq(words, sent)		#(word num: freq)
    sentence = format_line(words, sent, label, idfs)
    print idfs
    training_set.append(sentence)

  for line in training_set:
    outFile.write(line)

  return outFile

input_fname = raw_input("Input file: ")			#file with stats about each sentence; currently file is in format of ws.txt
inFile = open(input_fname,"r")
outFile = open(input_fname[0:-4]+"_sents.txt", "w")
testFile = open("ws_test.txt", "w")

words = {}						#dictionary matching string of each word to its unique integer ID
training_set = []

chars = list("!@#$%^&*()_+-=[]{};:'\".>,</?\|")	#forbidden words/characters
'''chars.append("the")
chars.append("is")
chars.append("of")
chars.append("an")
'''

docs = []			#[string]
labels = []			#[int]; index corresponds to docs
#info = []			#[string]; exact lines that will be written in the outFile

#---------------Filling up docs and labels--------------------------#
while True:
  line = inFile.readline().strip().split("\t")
  if line != ['']:
    sent = line[3][1:-2]
    label = det_class(line[7])
    docs.append(sent)
    labels.append(label)
  else:
    break

words = build_dict(docs, chars)

#print words
for i in range(len(docs)):	#for each element in the doc (ie each sentence)
  doc = docs[i]
  label = labels[i]
  sentence = doc
  idfs = {}			#unique_ID: idf
  for word in doc.lower().split(" "):
    if word in words.keys():
      idfs[words[word]] = find_idf(word, docs)
  outFile.write(format_line(words, "".join(sentence), label, idfs))



sents = ["I want an apple", "Tomorrow there will be a lot of snow on the ground on the east coast", "He will come to my house.", "Everyone loves watching the sitcom because it is spectacular", "Over 50 000 people were killed in the Iraq war"]


for sent in sents:
  idf = {}
  for word in map(lower, sent.split(" ")):
    idf[word] = find_idf(word, sents)
  testFile.write(format_line(words, sent, 1, idf))

#===========================================================
#--------------------FROM TASKS-----------------------------
#making training data from tasks obtained from main
tasks = main()[1]
outFile = open("test.txt", "w")
outFile = format_tasks(words, tasks, outFile)
outFile.close()



