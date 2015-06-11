from main import *
from math import *
import collections
from collections import OrderedDict

def lower(x):
  return x.lower()

def format_line(words, sentence, label, weights):	
  '''@param {string:int}, string, [string], int, {string: float}
  each word: unique ID, sentence, stop words, 1=gen, -1=spec, token:weight
  can be used to format test sentences'''

  string = str(label)
  od = collections.OrderedDict(sorted(weights.items()))
  l = od.items()
  for pair in l:
    string += " " + str(pair[0]) + ":" + str(pair[1])
  string+="\n"
  return string

def format_tasks(tasks, outFile):
  training_set = []					#list of strings to add to outFile
  words = {}						#key = "word" value = unique int ID
  chars = list("!@#$%^&*()_+-=[]{};:'\".>,</?\|")	#stop words
  for task_key in tasks:
    task = tasks[task_key]
    sentences = task.get_sentences()

    for sent in sentences:
      word_freqs = {}		#(word num: freq)
      avg_scale = sum(int(i[0]) for i in sent.get_scales())/len(sent.get_scales())
      clas = 0		#0 = specific, 1 = mixed, 2 = general

      if avg_scale < 3:
        clas = -1
      elif avg_scale == 3:
        clas = 0
      else:
        clas = 1
    
      if 
      sentence = format_line(words, sent.get_sent(), clas, word_freqs)
      training_set.append(sentence)

  for line in training_set:
    outFile.write(line)

#making training data from tasks obtained from main
#tasks = main()
outFile = open("training.txt", "w")

#format_tasks(tasks,outFile)
#outFile.close()


