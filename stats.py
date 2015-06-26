import scipy
import numpy
import scipy.stats
from sets import Set
import matplotlib.pyplot as pl
from ExternalDict import ExternalDict
from idfCalculator import idfCalculator
from gather import ask_user_for_tasks as get_tasks



def extract_scale_nums(scales):          #scales: list of scales from a sentence
  nums = []
  for scale in scales:
    if scale[0] !="NA":
      nums.append(int(scale[0]))
  return nums

def has_keyword(phrase, keyword):                          #not used
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


def find_max_amb_words(sentence, freqs):
  index_freqs = {}
  sent_list = sentence.get_sent().split()
  freq_list = []
  for pair in freqs.values():
    freq_list.append(pair[1])
  maximum = max(freq_list)
  for i in freqs:
    if freqs[i][1] == maximum:
      index_freqs[i] = (sent_list[i],maximum)

  return index_freqs

def find_all_amb_phrases(sentence):
  questions = sentence.get_questions()
  index_freqs = {}
  sent_list = sentence.get_sent().split()
  freqs = [0 for i in range(len(sent_list))]
  for question in questions:
    low = question.get_low()
    high = question.get_high()
    for i in range(low, high+1):
      freqs[i]+=1
  for i in range(len(freqs)):
    if freqs[i]!=0:
      index_freqs[i] = (sent_list[i],freqs[i])
  return index_freqs

def find_context_labels(sentence):           #sentence is a sentence object
  labels = [0]*4
  for question in sentence.get_questions():
    if "NA" not in question.get_context():
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

def add_qfreqs(sent, qmap, amb_phrases):         #(sent = sentence object, amb_phrases = {index of word: (string of word, #times asked about)}
  sentence = sent.get_sent().split()
  for i in amb_phrases:
    sentence[i] = sentence[i] + "(" + str(qmap[i]) + "/" + str(amb_phrases[i][1]) + ")"
  return " ".join(sentence)

def print_overlap(q1, q2, sent):                    # q1, q2 = questions, sent = list; prints sentences with overlaps annotated as () and [] brackets
  q1sym = '('
  q2sym = '['
  low = min([q1.get_low(), q2.get_low()])
  midlow = max([q1.get_low(), q2.get_low()])
  hi = max([q1.get_high(), q2.get_high()])
  midhigh = min([q1.get_high(), q2.get_high()])
  #for i in range(low, hi+1):
  #short_sent = 
  tups = [(q1.get_low(),"("), (q1.get_high()+1,")"), (q2.get_low(),"["), (q2.get_high()+1,"]")]
  tups = sorted(tups, key = lambda tup: tup[0], reverse=True)
  '''for i in [q1, q2]:
    tups.append((i.get_low(), i))
    tups.append((i.get_high(), i))
  tups = sorted(tups, key = lambda tup: tup[0], reverse=True)'''
  for tup in tups:
    sent.insert(tup[0], tup[1])
  #print " ".join(sent)
      
def get_overlaps(sentence):                 #gets number of overlaps of each type for a sentence
  questions = sentence.get_questions()
  overlaps = {"equal":0, "intersect":0, "proper":0}
  for i in range(len(questions)):
    for j in range(i+1, len(questions)):
      q1 = questions[i]
      q2 = questions[j]
      if q1.get_low() == q2.get_low() and q1.get_high() == q2.get_high():
        overlaps["equal"]+=1
      elif (q1.get_low()>q2.get_high()) or (q1.get_high()<q2.get_low()):
        pass
      elif q1.get_low() in range(q2.get_low(), q2.get_high()+1) and q1.get_high() in range(q2.get_low(), q2.get_high()+1):
        overlaps["proper"]+=1
        #print_overlap(q1, q2, sentence.get_sent().split())
      elif q2.get_low() in range(q1.get_low(), q1.get_high()+1) and q2.get_high() in range(q1.get_low(), q1.get_high()+1):
        overlaps["proper"]+=1
        #print_overlap(q1, q2, sentence.get_sent().split())
      else:
        overlaps["intersect"]+=1
  return overlaps
  
def make_qword_worker_map(sentence):                     #makes map: {index of ambiguous word:[workerIDs]}
  qmap = {}
  for question in sentence.get_questions():
    for i in range(question.get_low(), question.get_high()+1):
      if i in qmap:
        qmap[i].append(question.get_ID())
      else:
        qmap[i] = [question.get_ID()]
  return qmap
  
def num_unique_worker(qmap):                         #qmap: {index of ambiguous words:[workerIDs]};  returns map of {index:number of unique workerIDs}
  newmap = {}
  for key in qmap:
    newmap[key] = len(Set(qmap[key]))
  return newmap
  
def num_questions(qmap):                             #takes in qmap {index of ambword:[workerIDs]}; returns map of {index:number of questions}
  newmap = {}
  for key in qmap:
    newmap[key] = len(qmap[key])
  return newmap

def make_qword_prop_map(qmap, sentlength):              #takes in map {index of ambword:# questions} and sent length: #; returns map of {#Qs asked about word: proportion of sentence} 
  prop_map = {}
  for qfreq in qmap.values():
    if qfreq in prop_map:
      prop_map[qfreq] += 1.0/sentlength
    else:
      prop_map[qfreq] = 1.0/sentlength
  prop_map[0] = float(sentlength - len(qmap))/sentlength
  return prop_map
  
def int_scale(scale):                                   #returns scale as int
  return int(scale[0])
  

#----------------------------------------PLOTTING FUNCTIONS--------------------------------------------
def plot_corr(x_label, y_label, l1, l2):
  pl.xlabel(x_label)
  pl.ylabel(y_label)
  pl.scatter(l1, l2)
  pl.show()

#------------------------------------------------------------MAIN------------------------------------------
tasks = get_tasks()
info = []
out = open("output/combined_amb_phrases.txt","w") 
out_scales = open("output/combined_scales.txt","w")
task_lengths = []
amb_words = []                           #list of integers corresponding to ambiguity rating of a word
amb_words_idfs = []                      #list of idf corresponding to idf of ambiguous words in amb_words
word_dict = ExternalDict("NYT/word.dict")
idf_calc = idfCalculator()
all_corrs = []
amb_phrase_idfs = []
unamb_words_idfs = []
avg_scales_per_worker = {}              #{worker ID: [avg scales per task]}
mean_scales = []
percent_specific = []
for key in tasks:
  task = tasks[key]
  meanandDevs = []
  kwordsbySent = []			#list of maps (index of list = sent#, key = keyword (e.g. "what", "how"), value = frequency)
  qnumsbySent = []			#list of maps (index of list = sent#, key = workerID, value = number of questions asked)
  scale_maxes = []
  scale_mins = []
  q_maxes = []
  q_mins = []
  amb_phrases_per_sent = []		#list of maps that map to tuples (index of list = sent#, key = word index, value = ("word",freq)
  max_ambs = []         #list of maps that map to tuples {index = sent #, key = word index in sentence, tuple = "word", freq
  context_labels = [0]*4 
  context_map = {0: "No", 3:"Vague", 2:"Some", 1:"Immediate"}            
  task_lengths.append(sum(map(sent_length, task.get_sentences())))       #add sentence length of this task to list of task lengths
  context_value_map = {"0": 3, "1": 0, "2": 1, "3": 2}                   #trying to find correlation of idfs, "No" is least, "immediate" is most
  overlaps = []                                                          #list of maps (index of list = sent#, key = type of overlap, value = frequency)
  qword_worker_maps = []                                                 #list of maps; index of list = sent#  map: {index of word:[workerIDs]}
  qword_worker_count = []                                                #list of maps: index of list = sent#, map: {index of word: number of unique workers asking about the word}
  qword_q_count = []                                                     #list of maps: index of list = sent#, map: {index of word: number of questions about the word}
  qword_q_proportions = []                                               #list of maps: index of list = sent#, map: {# of questions about a word:proportion of that # in sent}

  
  for i, sentence in enumerate(task.get_sentences()):
    sentlist = sentence.get_sent().split(" ")
    nums = extract_scale_nums(sentence.get_scales())
    if len(nums) != len(sentence.get_scales()):
      pass							#if someone doesn't rate a sentence, skip the sentence
    mean = numpy.mean(nums)
    mean_scales.append(mean)
    stdDev = numpy.std(nums)
    meanandDevs.append((sentence.get_num(),round(mean,2), round(stdDev,2)))
    qnums = find_quest_nums(sentence, task.get_workers())
    qnumsbySent.append(qnums)
    q_maxes.append(max(qnums.values()))
    q_mins.append(min(qnums.values()))
    kwordsbySent.append(find_keyword_freqmap(sentence))
    scale_maxes.append(max(nums))
    scale_mins.append(min(nums))
    amb_phrases_per_sent.append(find_all_amb_phrases(sentence))
    max_ambs.append(find_max_amb_words(sentence, find_all_amb_phrases(sentence)))
    next_label = find_context_labels(sentence)
    context_labels = add_context_labels(context_labels, next_label)
    overlaps.append(get_overlaps(sentence))
    qword_worker_maps.append(make_qword_worker_map(sentence))
    qword_worker_count.append(num_unique_worker(qword_worker_maps[i]))
    qword_q_count_map = num_questions(qword_worker_maps[i])
    qword_q_count.append(qword_q_count_map)
    another_qmap = make_qword_prop_map(qword_q_count_map, len(sentlist))                #this is to store a qword_q_proportion: see above
    qword_q_proportions.append(another_qmap)
    percent_specific.append(another_qmap[0])
    word_seen = [False]*len(sentlist)                                                   #start for calculating IDF correlations
    for question in sentence.get_questions():
      low = question.get_low()
      high = question.get_high()
      for i in range(low, high+1):
        word = sentlist[i]
        word = word.lower()
        amb_words.append(float(context_value_map[question.get_context()[0]]))
        amb_words_idfs.append(idf_calc.idf(word))
        word_seen[i] = True
    for i, word in enumerate(sentlist):
      word = word.lower()
      if word_seen[i]:
        if word in word_dict:
          amb_phrase_idfs.append(idf_calc.idf(word_dict[word]))
        else:
          amb_phrase_idfs.append(idf_calc.idf(word))
      else:
        if word in word_dict:
          unamb_words_idfs.append(idf_calc.idf(word_dict[word]))
        else:
          unamb_words_idfs.append(idf_calc.idf(word))
  workers = task.get_workers()
  scale_corrs = get_scale_corrs(workers)
  for worker in workers:
    wID = worker.get_ID()
    avg_scale = 1.0*sum(map(int_scale, worker.get_scales()))/len(worker.get_scales())
    if wID not in avg_scales_per_worker:
      avg_scales_per_worker[wID] = [avg_scale]
    else:
      avg_scales_per_worker[wID].append(avg_scale)

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
  #print "average scale: " + str(round(numpy.mean(scalemeans),2))
  """
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
  #print "average questions asked: " + str(round(numpy.mean(qnumsmeans),2))
  
  info.append("\n\n------------------Keyword Frequencies-----------------")
  info.append(print_keyword_freqs(kwordsbySent))
  """
  info.append("\n\n------------------Most Ambiguous Phrases...----------")
  for i in range(len(amb_phrases_per_sent)):
    info.append("\n\nSentence " + str(i)+": " + add_qfreqs(task.get_sentences()[i], qword_worker_count[i], amb_phrases_per_sent[i]))
    
    #for amb_phrases file
    sent = task.get_sentences()[i]
    avg_scale = sum(extract_scale_nums(sent.get_scales()))*1.0/len(sent.get_scales())
    out.write("Sentence "+ str(i) + ": ")
    out.write(add_qfreqs(sent, qword_worker_count[i], amb_phrases_per_sent[i]))
    out_scales.write(str(avg_scale)+"\n")
    out.write("\n\n")
    info.append("Sent " + str(i) + ": \n")
    for key in qword_q_proportions[i]:
      info.append("\t# Q's: " + str(key) + " %: " + str(round(qword_q_proportions[i][key], 4)*100) + "\n")
  info.append("\nCorrelation between Scale and Percent of Sentence not asked about: " + str(numpy.corrcoef(mean_scales, percent_specific)[0][1]))    
  info.append("\n\n-----------------Context Labels-----------------")
  for i, contextfreq in enumerate(context_labels):
    info.append("\n" + context_map[i] + ": " + str(1.0*contextfreq/sum(map(int,context_labels))))

  
  info.append("\n\n------------------Overlap-----------------------\n")
  sums = {"equal":0, "intersect":0, "proper":0}
  for overlap in overlaps:
    for key in sums.keys():
      sums[key]+=overlap[key]
  
  for key in sums:
    info.append(key+": "+str(sums[key])+"\t")
    
  info.append("\n\n\n")
  
info.append("\n\n-----------------Confidence Interval of Sentence Lengths-----------------")
info.append("\n(mean, lower bound, upper bound) " + str(mean_confidence_interval(task_lengths)))
info.append("\nmin: " + str(min(task_lengths))+ "\nmax: " + str(max(task_lengths)))

info.append("\n\n-----------------OTHER DATA-----------------")
info.append("\n\n" + "Overall Worker Correlation:" + str(round(numpy.mean(all_corrs), 3)) + "\n")
info.append("95% Confidence Interval of ambiguous word idfs: " + str(mean_confidence_interval(amb_phrase_idfs)))
info.append("\n95% Confidence Interval of unambiguous word idfs: " + str(mean_confidence_interval(unamb_words_idfs)))
info.append("\nAverage Scale per Task Correlation between Workers: ") 
for i in range(len(workers)):
  for j in range(i+1, len(workers)):
    w1 = workers[i].get_ID()
    w2 = workers[j].get_ID()
    info.append( "\n\t" + w1 + " " + w2 + " :" + str(numpy.corrcoef(avg_scales_per_worker[w1], avg_scales_per_worker[w2])[0][1]))

print "ambiguous words idfs: " + str(mean_confidence_interval(amb_phrase_idfs))
print "unambiguous words idfs: " + str(mean_confidence_interval(unamb_words_idfs))
print "average worker correlation: " + str(numpy.mean(all_corrs))

#print "weird ambiguous word correlation: " + str(numpy.corrcoef(amb_words, amb_words_idfs)[1][0])

#PRINTING THINGS
outFile = open("output/combined_output-stats.txt","w")

for line in info:
  outFile.write(line)

outFile.close()
out.close()

#-------------------------------------------------PLOTTING THINGS--------------------------------------------------------------
wIDs = avg_scales_per_worker.keys()
for i in range(len(avg_scales_per_worker)):
  for j in range(i+1, len(avg_scales_per_worker)):
    plot_corr(wIDs[i], wIDs[j], avg_scales_per_worker[wIDs[i]], avg_scales_per_worker[wIDs[j]])

plot_corr("Mean Scales", "% Specific", mean_scales, percent_specific)








