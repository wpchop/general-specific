from parse_turk_data import main
import scipy
import numpy
import scipy.stats
from ExternalDict import ExternalDict
from idfCalculator import idfCalculator


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
  """Returns map that maps integer keys to a tuple (word, frequency) pairs.
  Size of map is equal to number of words in the sentence that are the most
  ambiguous"""
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

def find_context_labels(sentence):           #sentence is a sentence object
  labels = [0]*4
  for question in sentence.get_questions():
    labels[int(question.get_context()[0])]+=1
  return labels
  
def add_context_labels(list1, list2):       #adds elements of two lists
  for i, element in enumerate(list1):
    list1[i] = element + list2[i]
  return list1

def sent_length(sentence):               #sentence is a sentence object
  return len(sentence.get_sent().split())
  
def mean_confidence_interval(data, confidence=0.95):        #http://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
    a = 1.0*numpy.array(data)
    n = len(a)
    m, se = numpy.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t._ppf((1+confidence)/2., n-1)
    return round(m, 3), round(m-h, 3), round(m+h, 3)

def cap_words(sentence, amb_phrases):         #(sentence = list of words in sent, amb_phrases = {index of word: (string of word, #times asked about)}
  for i in amb_phrases:
    sentence[i] = sentence[i].upper() + "(" + str(amb_phrases[i][1]) + ")"
  return " ".join(sentence)
  
#------------------------------------------------------------MAIN------------------------------------------
input_fname, tasks = main()
info = []
task_lengths = []
amb_words = []                           #list of integers corresponding to ambiguity rating of a word
amb_words_idfs = []                      #list of idf corresponding to idf of ambiguous words in amb_words
word_dict = ExternalDict("word.dict")
idf_calc = idfCalculator()
all_corrs = []
amb_phrase_idfs = []
unamb_words_idfs = []

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
  context_labels = [0]*4 
  context_map = {0: "No", 3:"Vague", 2:"Some", 1:"Immediate"}
  task_lengths.append(sum(map(sent_length, task.get_sentences())))       #add sentence length of this task to list of task lengths
  context_value_map = {"0": 3, "1": 0, "2": 1, "3": 2}
  

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
    next_label = find_context_labels(sentence)
    context_labels = add_context_labels(context_labels, next_label)
    """
    For calculating correlation of labels and idf """
    sentlist = sentence.get_sent().split(" ")
    word_seen = [False]*len(sentlist)
    for question in sentence.get_questions():
      low = question.get_low()
      high = question.get_high()
      for i in range(low, high+1):
        amb_words.append(float(context_value_map[question.get_context()[0]]))
        amb_words_idfs.append(idf_calc.idf(word_dict[sentlist[i].lower()]))
        word_seen[i] = True
    for i, word in enumerate(sentlist):
      word = word.lower()
      if word_seen[i]:
        amb_phrase_idfs.append(idf_calc.idf(word_dict[word]))
      else:
        unamb_words_idfs.append(idf_calc.idf(word_dict[word]))
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
    all_corrs.append(corr[2])
  
  info.append("\n---------------Means, Standard Deviations, and Max/Min------------")
  scalemeans = []
  for i, element in enumerate(meanandDevs):
    info.append("\nSentence: " + str(element[0]) + "\n\tmean: " + str(element[1]) + "\n\tstd dev: " + str(element[2]))
    info.append("\n\tmax: " + str(scale_maxes[i]) + "\n\tmin: " + str(scale_mins[i]))
    scalemeans.append(element[1])
  print "average scale: " + str(round(numpy.mean(scalemeans),2))

  info.append("\n\n----------------QUESTIONS------------\n")
  info.append("\n-----------Correlations between Workers---------\n")
  for corr in num_questions_corrs:
    info.append("Worker 1: " + corr[0] + "\nWorker 2: " + corr[1] + "\n\tCorrelation: " + str(round(corr[2],2)) + "\n")

  info.append("\n---------------Means, Standard Deviations and Max/Min------------")
  qnumsmeans = []
  for i, element in enumerate(q_means_and_devs):
    info.append("\nSentence: " + str(element[0]) + "\n\tmean: " + str(element[1]) + "\n\tstd dev: " + str(element[2]))
    info.append("\n\tmax: " + str(q_maxes[i]) + "\n\tmin: " + str(q_mins[i]))
    qnumsmeans.append(element[1])
  info.append("\nAverage Number of Questions asked: " + str(round(numpy.mean(qnumsmeans),2)))
  print "average questions asked: " + str(round(numpy.mean(qnumsmeans),2))
  
  info.append("\n\n------------------Keyword Frequencies-----------------")
  info.append(print_keyword_freqs(kwordsbySent))

  info.append("\n\n------------------Most Ambiguous Phrases...----------")
  for i in range(len(amb_phrases_per_sent)):
    info.append("\n\nSentence: " + str(i) + cap_words(task.get_sentences()[i].get_sent().split(" "), amb_phrases_per_sent[i]))
      
  info.append("\n\n-----------------Context Labels-----------------")
  for i, contextfreq in enumerate(context_labels):
    info.append("\n" + context_map[i] + ": " + str(contextfreq))
  info.append("\n\n\n")
  
  
info.append("\n\n-----------------Confidence Interval of Sentence Lengths-----------------")
info.append("\n(mean, lower bound, upper bound) " + str(mean_confidence_interval(task_lengths)))
info.append("\nmin: " + str(min(task_lengths))+ "\nmax: " + str(max(task_lengths)))

info.append("\n\n-----------------OTHER DATA-----------------")
info.append("\n\n" + "Overall Worker Correlation:" + str(round(numpy.mean(all_corrs), 3)) + "\n")
info.append("95% Confidence Interval of ambiguous word idfs: " + str(mean_confidence_interval(amb_phrase_idfs)))
info.append("\n95% Confidence Interval of unambiguous word idfs: " + str(mean_confidence_interval(unamb_words_idfs)))
print "ambiguous words idfs: " + str(mean_confidence_interval(amb_phrase_idfs))
print "unambiguous words idfs: " + str(mean_confidence_interval(unamb_words_idfs))
print "average worker correlation: " + str(numpy.mean(all_corrs))

#print amb_words
#print amb_words_idfs

print "weird ambiguous word correlation: " + str(numpy.corrcoef(amb_words, amb_words_idfs)[1][0])

#PRINTING THINGS

outFile = open(input_fname[0:input_fname.index(".")] + "_output-stats.txt","w")

for line in info:
  outFile.write(line)

outFile.close()



















