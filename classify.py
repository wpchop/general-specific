from main import *
import collections
from collections import OrderedDict

def lower(x):
  return x.lower()

'''def return_tuple_list(l):
  newlist = []
  for i, item in enumerate(l):
    newlist.append((i,item))
  return newlist
'''

def format_sentence_svm(sentence, words):	#sentence is a string, words = dict of words used in training data
  '''can be used to format test sentences'''

  sentl = map(lower, sentence.split(" "))
  string = "0"		#0 because arbitrary numbers can be used for first column of test data
  count = {}
  for word in sentl:
    if word not in chars:
      if word in words.keys():
        if word in count.keys():
          count[words[word]] += 1
        else:
          count[words[word]] = 1
      else:
        count[len(words)+1] = 1

  od = collections.OrderedDict(sorted(count.items()))
  l = od.items()
  for pair in l:
    string += " " + str(pair[0]) + ":" + str(pair[1])
  string += "\n"
  return string


#making training data from tasks obtained from main
tasks = main()
outFile = open("training.txt", "w")
training_sets = []	#list of dicts that each corresponds to attributes of each sentence {class:attributes}
words = {}		#key = "word" value = integer that will correspond to attribute number

chars = list("!@#$%^&*()_+-=[]{};:'\".>,</?\|")		#characters that should not be words

for task_key in tasks:
  task = tasks[task_key]
  sentences = task.get_sentences()

  for sent in sentences:
    word_freqs = {}		#(word num: freq)
    avg_scale = sum(int(i[0]) for i in sent.get_scales())/len(sent.get_scales())
    clas = 0		#0 = specific, 1 = mixed, 2 = general

    if avg_scale < 3:
      clas = 0
    elif avg_scale == 3:
      clas = 1
    else:
      clas = 2
    
    sent_list = map(lower, sent.get_sent().split(" "))

    #filling up word_freqs and words
    for word in sent_list:
      keys_global = words.keys()
      keys_local = word_freqs.keys()
      if word not in chars:
        if word in keys_global and words[word] in keys_local:
          word_freqs[words[word]] += 1
        elif word in keys_global:
          word_freqs[words[word]] = 1
        else:
          words[word] = len(words)
          word_freqs[words[word]] = 1
    
    od = collections.OrderedDict(sorted(word_freqs.items()))
    training_sets.append({clas: od})

for d in training_sets:
  for c in d:
    outFile.write(str(c))
    nlist = list(d[c].items())
    for pair in nlist:
      outFile.write(" "+ str(pair[0]) + ":" + str(pair[1]))
    outFile.write("\n")


