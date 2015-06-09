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

def format_sentence_svm(sentence, chars, label):	#sentence is a string, chars = tokens not counted in attributes, label = classification number
  '''can be used to format test sentences'''

  global words
  sentl = map(lower, sentence.split(" "))
  string = str(label)
  count = {}
  for word in sentl:
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


#making training data from tasks obtained from main
tasks = main()
outFile = open("training.txt", "w")
training_set = []	#list of strings to add to outFile
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
    
    sentence = format_sentence_svm(sent.get_sent(), chars, clas)
    training_set.append(sentence)

for line in training_set:
  outFile.write(line)

outFile.close()


