from main import *
import scipy
import numpy
import matplotlib.pyplot as pl


def extract_scale_nums(scales):
  nums = []
  for scale in scales:
    if scale[0] !="NA":
      nums.append(int(scale[0]))
  return nums

def has_keyword(phrase, keyword):
  return phrase.lower().find(keyword.lower())!=-1

def find_keyword(phrase, keywords):
  for word in keywords.keys():
    if phrase.lower().find(word)!=-1 and word!="":
      return word
  return ""

def find_quest_nums(sentence, workers):
  """Returns a map for one sentence from workIDs to number of questions asked"""
  worker_questions = {}
  for worker in workers:
    worker_questions[worker.get_ID()] = 0
  for question in sentence.get_questions():
    worker_questions[question.get_ID()]+=1
  return worker_questions

def find_keyword_freqmap(sentence):
  keywords = {"who": 0, "what": 0, "where": 0, "when": 0, "why": 0, "how": 0, "which": 0, "": 0}
  for question in sentence.get_questions():
      kword = find_keyword(question.get_body(), keywords)
      keywords[kword] = keywords[kword] + 1
  return keywords

def get_corr_list(dicc): 
  corr_list = []
  keys = dicc.keys()
  for i in range(len(keys)): #len(keys) = # of workers
    for j in range(i, len(keys)):
      if i!=j:
        #get lists to work with
        list1 = dicc[keys[i]]
        list2 = dicc[keys[j]]
        corr = numpy.corrcoef(list1, list2)[0][1]
        w1 = keys[i]
        w2 = keys[j]
        corr_list.append( (w1, w2, corr) )
  return corr_list

        
def make_worker_to_freq_list_map(qnum_map_list): #qnum_map_list = list of maps (one per sentence) that describe the # of questions for each worker (worker_ID:#ofquestions)
  output_map = {}
  for workerID in qnum_map_list[0].keys():
    output_map[workerID] = []
  for dicc in qnum_map_list:
    for workerID in dicc.keys():
      output_map[workerID].append( dicc[workerID] )
  return output_map

def get_scale_corrs(workers):
  corr_list = []
  for i in range(len(workers)):
    for j in range(i,len(workers)):
      if i!=j:
        scalenums1 = []
        scalenums2 = []
        scales1 = workers[i].get_scales()
        scales2 = workers[j].get_scales()
        for k in range(len(scales1)):
          if scales1[k][0]!="NA" and scales2[k][0]!="NA":
            scalenums1.append(int(scales1[k][0]))
            scalenums2.append(int(scales2[k][0]))
        corr = (workers[i].get_ID(), workers[j].get_ID(), numpy.corrcoef(scalenums1, scalenums2)[0][1])
        corr_list.append(corr)
  return corr_list
  

def print_keyword_freqs(kwordsbySent):
  string = ""
  for i, sentHash in enumerate(kwordsbySent):
    string+= "\nSentence " + str(i) + ":\n" 
    maxfreq = max(sentHash.values())+1
    for key in sentHash :
      string += key + ": " + (5-len(key))*" " + "*" * sentHash[key] + " " * (maxfreq - sentHash[key]) + "(" + str(sentHash[key])+")\n"
  return string

def means_and_devs_qs(freqlist):
  meansandDevs = []
  for i, sentence in enumerate(freqlist):
    nums = sentence.values()							#if someone doesn't rate a sentence, skip the sentence
    mean = numpy.mean(nums)
    stdDev = numpy.std(nums)
    meansandDevs.append((i,round(mean,2), round(stdDev,2)))
  return meansandDevs

def find_amb_words(sentence):
  questions = sentence.get_questions()
  index_freqs = {}
  sent_list = sentence.get_sent().split()
  freqs = [0 for i in range(len(sent_list))]

  for question in questions:
    low = question.get_low()
    high = question.get_high()
    for i in range(low, high+1):
      freqs[i]+=1
  
  maximum = max(freqs)
  for i in range(len(freqs)):
    if freqs[i] == maximum:
      index_freqs[i] = (sent_list[i],maximum)

  return index_freqs

#------------------------------------------------------------MAIN------------------------------------------
tasks = main()
info = []
for key in tasks:
  task = tasks[key]
  meanandDevs = []
  kwordsbySent = []			#list of maps (index of list = sent#, key = keyword (e.g. "what", "how"), value = frequency)
  qnumsbySent = []			#list of maps (index of list = sent#, key = workerID, value = number of questions asked)
  scale_maxes = []
  scale_mins = []
  q_maxes = []
  q_mins = []
  amb_phrases_per_sent = []		#list of maps that map to tuples (index of list = sent#, key = word index, tuple = "word", freq)
  

  for sentence in task.get_sentences():
    nums = extract_scale_nums(sentence.get_scales())
    if len(nums) != len(sentence.get_scales()):
      pass							#if someone doesn't rate a sentence, skip the sentence
    mean = numpy.mean(nums)
    stdDev = numpy.std(nums)
    meanandDevs.append((sentence.get_num(),round(mean,2), round(stdDev,2)))
    qnums = find_quest_nums(sentence, task.get_workers())
    qnumsbySent.append(qnums)
    q_maxes.append(max(qnums.values()))
    q_mins.append(min(qnums.values()))
    kwordsbySent.append(find_keyword_freqmap(sentence))
    scale_maxes.append(max(nums))
    scale_mins.append(min(nums))
    amb_phrases_per_sent.append(find_amb_words(sentence))

  workers = task.get_workers()
  scale_corrs = get_scale_corrs(workers)

  num_questions_map = make_worker_to_freq_list_map(qnumsbySent)
  num_questions_corrs = get_corr_list(num_questions_map)

  q_means_and_devs = means_and_devs_qs(qnumsbySent)

#--------------------ADDING DATA TO INFO-----------------------
  info.append("=========================================================\nTASK: " + key )
  info.append("\n\n----------------SCALES--------------\n")
  info.append("\n-------------Correlations between Workers--------------\n")
  for corr in scale_corrs:
    info.append("Worker 1: " + corr[0] + "\nWorker 2: " + corr[1] + "\n\tCorrelation: " + str(round(corr[2],2)) + "\n")
  
  info.append("\n---------------Means, Standard Deviations, and Max/Min------------")
  for i, element in enumerate(meanandDevs):
    info.append("\nSentence: " + str(element[0]) + "\n\tmean: " + str(element[1]) + "\n\tstd dev: " + str(element[2]))
    info.append("\n\tmax: " + str(scale_maxes[i]) + "\n\tmin: " + str(scale_mins[i]))

  info.append("\n\n----------------QUESTIONS------------\n")
  info.append("\n-----------Correlations between Workers---------\n")
  for corr in num_questions_corrs:
    info.append("Worker 1: " + corr[0] + "\nWorker 2: " + corr[1] + "\n\tCorrelation: " + str(round(corr[2],2)) + "\n")

  info.append("\n---------------Means, Standard Deviations and Max/Min------------")
  for i, element in enumerate(q_means_and_devs):
    info.append("\nSentence: " + str(element[0]) + "\n\tmean: " + str(element[1]) + "\n\tstd dev: " + str(element[2]))
    info.append("\n\tmax: " + str(q_maxes[i]) + "\n\tmin: " + str(q_mins[i]))
  
  info.append("\n\n------------------Keyword Frequencies-----------------")
  info.append(print_keyword_freqs(kwordsbySent))

  info.append("\n\n------------------Most Ambiguous Phrases...----------")
  for i in range(len(amb_phrases_per_sent)):
    info.append("\n\nSentence: " + str(i) + "\n" + task.get_sentence(i).get_sent())
    keys = amb_phrases_per_sent[i].keys()
    for key in keys:
      info.append("\n\tindex: " + str(key) + "\tword: " + amb_phrases_per_sent[i][key][0] + "\tfreq: " + str(amb_phrases_per_sent[i][key][1]))  
  info.append("\n\n\n")

#PRINTING THINGS

outFile = open("outputs-stats.txt","w")

for line in info:
  outFile.write(line)

outFile.close()



















