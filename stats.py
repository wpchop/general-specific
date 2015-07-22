import scipy
import numpy
import matplotlib.pyplot as pl
import scipy.stats
from gather import collect_tasks as get_tasks
from ExternalDict import ExternalDict
from idfCalculator import idfCalculator
from sets import Set
from random import *
from scipy import stats


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
  

def print_keyword_freqs(kwordsbySent):                     #prints those stars
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
  """sentence is sentence object; freqs is map {int index of word being asked about: tuple (string, frequency)}
  returns a dictionary {index: (string, maximum)} where maximum is max frequency asked about for any word in a sentence"""
  index_freqs = {}
  sent_list = sentence.get_sent().split()
  freq_list = []
  for pair in freqs.values():
    freq_list.append(pair[1])
  if freq_list != []:
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
  
def add_lists(*list_args):       #adds elements of lists of equal length at matching indices
  sum_list = [0]*len(list_args[0])
  for lst in list_args:
    for i, element in enumerate(lst):
      sum_list[i] = sum_list[i] + element
  return sum_list
  
def transpose_lists(*list_args):       #transposes elements of given lists, list[m][n] -> l[n][m]
  sum_list = [[] for i in range(len(list_args[0]))]
  print sum_list
  for lst in list_args:
    for i, element in enumerate(lst):
      sum_list[i].append(element)
  return sum_list

def add_map_list(map_list):             #given a list of maps, adds all values of keys that are the same, returns one map
  final_map = {}
  for a_map in map_list:
    for key in a_map:
      if key not in final_map:
        final_map[key] = a_map[key]
      else:
        final_map[key]+= a_map[key]
  return final_map

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
  return " ".join(sent)
      
def get_overlaps(sentence):                 #gets number of overlaps of each type for a sentence
  questions = sentence.get_questions()
  overlaps = {"equal":0, "intersect":0, "proper":0, "noverlap":0}
  for i in range(len(questions)):
    nolap = True
    for j in range(i+1, len(questions)):
      q1 = questions[i]
      q2 = questions[j]
      if q1.get_low() == q2.get_low() and q1.get_high() == q2.get_high():
        overlaps["equal"]+=1
        nolap = False
      elif (q1.get_low()>q2.get_high()) or (q1.get_high()<q2.get_low()):
        pass
      elif q1.get_low() in range(q2.get_low(), q2.get_high()+1) and q1.get_high() in range(q2.get_low(), q2.get_high()+1):
        overlaps["proper"]+=1
        nolap = False
        out_overlaps.write(print_overlap(q1, q2, sentence.get_sent().split()) + "\n")
      elif q2.get_low() in range(q1.get_low(), q1.get_high()+1) and q2.get_high() in range(q1.get_low(), q1.get_high()+1):
        overlaps["proper"]+=1
        nolap = False
        out_overlaps.write(print_overlap(q1, q2, sentence.get_sent().split()) + "\n")
      else:
        overlaps["intersect"]+=1
        nolap = False
    if nolap:
      overlaps["noverlap"]+=1
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
  
def worker_correlation_plot_helper(all_scales_w1, all_scales_w2):         
  """returns worker scales and frequency of each scale pair"""
  pairwise_worker_scales_counter = {}                                     #map of tuple to frequency {(w_1 scale, w_2 scale): count}
  w1_scales = all_scales_w1
  w2_scales = all_scales_w2
  sizes = []
  w1_new_scales = []
  w2_new_scales = []
  for k in range(len(w1_scales)):
    if (w1_scales[k], w2_scales[k]) in pairwise_worker_scales_counter:
      pairwise_worker_scales_counter[(w1_scales[k], w2_scales[k])]+= 1
    else:
      pairwise_worker_scales_counter[(w1_scales[k], w2_scales[k])] = 1
  for k, item in enumerate(pairwise_worker_scales_counter.items()):
    sizes.append(item[1]*5)
    w1_new_scales.append(item[0][0])
    w2_new_scales.append(item[0][1])
  return w1_scales, w2_scales, sizes
  
def get_other_workers_avg(other_workers, all_scales_per_worker):                   #other_workers is list of Workers, all_scales_per_worker is map{wID:all_scales}
  other_worker_scales = []
  other_worker_avgs = []
  for i in range(len(other_workers)):
    other_worker_scales.append(all_scales_per_worker[other_workers[i].get_ID()])
  for i in range(len(other_worker_scales[0])):
    total = 0.0
    for j in other_worker_scales:
      total+= j[i]
    other_worker_avgs.append(total/len(other_worker_scales))
  return other_worker_avgs

def count_differences(scales, differences):                                   #scales is list of scales(3 ints) for a sentence, differences is list of occurences of differences in scales
  for i in range(len(scales)):
    for j in range(i+1, len(scales)):
      differences[abs(scales[j]-scales[i])]+=1
  return differences

def count_scales(scales, labels):                                             #scales is a list of scales for all sentence(or tasks), labels is list of numbers we want to divide scales by
  count = [0]*(len(labels)-1)
  for i in range(len(scales)):
    scale = scales[i]
    for j in range(len(labels) - 1):
      if scale == labels[-1]:
        count[-1] += 1
        break
      if scale < labels[j+1] and scale >=labels[j]:
        count[j] += 1
        break
  return count

def count_list(l):
  '''Counts the frequency of values in l, where l is a list of ints. 
  Returns a list of ints such that the counts are stored at the index.
  Ex: If 12 occured in l 3 times, the returned list would store 3 at
  the index 12.'''
  count = [0]*(max(l)+1)
  for i in range(len(l)):
    count[l[i]] += 1
  return count
  
def write_bar_labels(labels):                                                 #labels is list of numbers. write_bar_labels returns list of strings of length len(labels)-1
  string_labels = []
  for i in range(len(labels)-1):
    string_labels.append(str(labels[i]) + "-" + str(labels[i+1]))
  return string_labels

def get_percentages(lst):                                #takes in list of numbers, returns list of percentages
  total = sum(lst)
  return [lst[i]*100.0/total for i in range(len(lst))]
#---------------------------------------------GENERATING RANDOM ANNOTATORS---------------------------------------------
def get_worker_percentage_distribution(l):                        #l is list of lists of ints, frequency of scale by worker
  percentages = [0]*len(l[0])
  total = 0
  for i in range(len(l[0])):
    for lst in l:
      percentages[i]+=lst[i]
      total+=lst[i]
  percentages[0] = 1.0*percentages[0]/total
  for i in range(1, len(percentages)):
    percentages[i] = percentages[i-1]+1.0*percentages[i]/total
  return percentages
  
def generate_random_scale(distribution):                                    #generates random number from 0-6 based on a probability distribution of 7 percentages
  rand = random()
  for i, percent in enumerate(distribution):
    if rand <= percent:
       return i

def generate_random_scales_per_sent(num, distribution):                                         #num = number of annotators
  scales = []
  for i in range(num):
    scales.append(generate_random_scale(distribution))
  return scales

def generate_annotations_all_sents(num_sents, num_annotators, distribution):              #num_sents = number of sentences
  all_sent_scales = []                  #list of lists of 3 ints
  for i in range(num_sents):
    all_sent_scales.append(generate_random_scales_per_sent(num_annotators, distribution))
  return all_sent_scales
  
def get_avg_diff(differences):                           #given list of ints representing frequency, finds average index of list
  total = 0.0
  for i in range(len(differences)):
    total+= i*differences[i]
  return total/sum(differences)
#----------------------------------------PLOTTING FUNCTIONS--------------------------------------------
def plot_corr(title, x_label, y_label, l1, l2, sizes = []):
  pl.title(title)
  pl.xlabel(x_label)
  pl.ylabel(y_label)
  if sizes != []:
    pl.scatter(l1, l2, s=sizes)
  else:
    pl.scatter(l1, l2)
  pl.show()

def make_barchart(title, x_label, y_label, l, bar_labels, x_labels, bins=0):             #l is list of lists to graph, bar_labels are labels corresponding to each list in l, x_labels is x_axis label
  if bins ==0:
    bins = len(l[0])
  fig, ax = pl.subplots()
  index = numpy.arange(bins)
  bar_width = 0.8/len(l)
  opacity = 0.4
  rects = []
  colors = ['g','b','c']
  for i,lst in enumerate(l):
    if bar_labels == []:
      rect = pl.bar(index + bar_width*i, lst, bar_width, alpha=opacity, color=colors[i%3])
    else:
      rect = pl.bar(index + bar_width*i, lst, bar_width, alpha=opacity, color=colors[i%3], label=bar_labels[i])
    rects.append(rect)
  pl.xlabel(x_label)
  pl.ylabel(y_label)
  pl.title(title)
  pl.xticks(index + bar_width*0.5, x_labels)
  pl.legend(loc='upper left')
  pl.tight_layout()

  y_min, y_max = pl.ylim()
  pl.ylim(y_min, y_max*1.2)
  
  for i, rect in enumerate(rects):
    total = sum(l[i])
    for bar in rect:
      height = bar.get_height()
      if height!=0:
        if len(l) > 1:
          ax.text(bar.get_x()+bar.get_width()/2.0, height/2, '%.2f'%(100.0*int(height)/total)+"%", ha='center', va='bottom', rotation='vertical')
        else:
          ax.text(bar.get_x()+bar.get_width()/2.0, height + y_max/150.0, '%.2f'%(100.0*int(height)/total)+"%", ha='center', va='bottom')
  pl.show()
  
def make_histogram(title, x_label, y_label, l, bins=7):
  opacity = 0.4
  pl.xlabel(x_label)
  pl.ylabel(y_label)
  pl.title(title)
  pl.hist(l, bins, alpha=opacity)
  pl.show()

#------------------------------------------------------------MAIN------------------------------------------
tasks = get_tasks()
info = []
out = open("output/combined_amb_phrases.txt","w") 
out_scales = open("output/combined_scales.txt","w") 
out_overlaps = open("output/combined_overlaps.txt", "w")
task_lengths = []
amb_words = []                           #list of integers corresponding to ambiguity rating of a word
amb_words_idfs = []                      #list of idf corresponding to idf of ambiguous words in amb_words
word_dict = ExternalDict("NYT/word.dict")
idf_calc = idfCalculator()
all_corrs = []
amb_phrase_idfs = []
unamb_words_idfs = []
avg_scales_per_worker = {}              #{worker ID: [avg scales per task]}
mean_scales = []                        #mean scales by sentence
num_qs = []                      #number of questions asked per sentence
mean_scales_by_task = []                #list of scales by task
percent_specific = []
context_percentage_map = {"No": [], "Immediate": [], "Some": [], "Vague": []}
worker_corrs = []                       #average worker correlation per task
all_scales_per_worker = {}             #{worker ID: [list of all scales by sentence]}
differences = [0]*7                       #list of frequencies for differences in scale of each sentence; index: difference in scale, item:number of occurrences
worker_scale_comparison_per_task = {}                #{task ID: [(worker ID, correlation between 1 worker scale and avg of other workers' scales)]
avg_std_dev_per_task = {}                            #{task ID : avg std dev of sentences} 
avg_diff_per_task = {}                               #{task ID: avg difference scales of sentences}
master_context_labels = [0]*4                        #list, index corresponds to type of context label, value corresponds to frequency
context_map = {0: "No", 3:"Vague", 2:"Some", 1:"Immediate"}      
context_value_map = {"0": 3, "1": 0, "2": 1, "3": 2}                   #trying to find correlation of idfs, "No" is least, "immediate" is most      
kwords_by_task = {}                                                    #map of maps: key is taskID, value is map {key = keyword (e.g. "what", "how"), value = frequency}
amb_word_freqs = {}                                                    #map of ambiguous words: key is word, value is freq
kwords_by_sent_all = []                                              #list of maps (index of list = sent#, key = keyword (e.g. "what", "how"), value = frequency)
overlap_freqs = {"equal": 0, "proper": 0, "intersect": 0, "noverlap":0}            # key is type of overlap, value is frequency of overlap
qword_q_count_total = {}                                       #{# of questions about a word: number of words asked about that many times}} 

for key in tasks:
  task = tasks[key]
  meanandDevs = []      #tuple of (sentence#, mean, std deviation) by sentence
  kwordsbySent = []			#list of maps (index of list = sent#, key = keyword (e.g. "what", "how"), value = frequency)
  qnumsbySent = []			#list of maps (index of list = sent#, key = workerID, value = number of questions asked)
  scale_means = []      #list of scale means per sentence
  scale_maxes = []
  scale_mins = []
  q_maxes = []
  q_mins = []
  amb_phrases_per_sent = []		      #list of maps that map to tuples (index of list = sent#, key = word index, value = ("word",freq)
  max_ambs = []                     #list of maps that map to tuples {index = sent #, key = word index in sentence, tuple = "word", freq
  context_labels = [0]*4            #list that represents count of each type of context label, index corresponds to context_map
  task_lengths.append(sum(map(sent_length, task.get_sentences())))       #add sentence length of this task to list of task lengths
  overlaps = []                                                          #list of maps (index of list = sent#, key = type of overlap, value = frequency)
  qword_worker_maps = []                                                 #list of maps; index of list = sent#  map: {index of word:[workerIDs]}
  qword_worker_count = []                                                #list of maps: index of list = sent#, map: {index of word: number of unique workers asking about the word}
  qword_q_count = []                                                     #list of maps: index of list = sent#, map: {index of word: number of questions about the word}
  qword_q_proportions = []                                               #list of maps: index of list = sent#, map: {# of questions about a word:proportion of that # in sent}
  worker_scale_comparison = []                                           #list of tuples: (worker ID, corr)
  diffs_for_task = [0]*7
  for i, sentence in enumerate(task.get_sentences()):
    sentlist = sentence.get_sent().split(" ")
    nums = extract_scale_nums(sentence.get_scales())
    differences = count_differences(nums, differences)
    diffs_for_task = count_differences(nums, diffs_for_task)
    if len(nums) != len(sentence.get_scales()):
      pass							#if someone doesn't rate a sentence, skip the sentence
    mean = numpy.mean(nums)
    scale_means.append(mean)            #per task
    mean_scales.append(mean)            #per all
    stdDev = numpy.std(nums)
    meanandDevs.append((sentence.get_num(),round(mean,2), round(stdDev,2)))
    qnums = find_quest_nums(sentence, task.get_workers())
    num_qs.append(sum(qnums.values()))
    qnumsbySent.append(qnums)
    q_maxes.append(max(qnums.values()))
    q_mins.append(min(qnums.values()))
    kwordsbySent.append(find_keyword_freqmap(sentence))
    scale_maxes.append(max(nums))
    scale_mins.append(min(nums))
    amb_phrases_per_sent.append(find_all_amb_phrases(sentence))
    max_ambs.append(find_max_amb_words(sentence, find_all_amb_phrases(sentence)))
    current_labels = find_context_labels(sentence)
    context_labels = add_lists(context_labels, current_labels)                              #updates context_labels by adding counts of current sentence
    current_overlaps = get_overlaps(sentence)
    overlaps.append(current_overlaps)
    for okey in current_overlaps:
      overlap_freqs[okey]+=current_overlaps[okey]
    qword_worker_maps.append(make_qword_worker_map(sentence))
    qword_worker_count.append(num_unique_worker(qword_worker_maps[i]))
    qword_q_count_map = num_questions(qword_worker_maps[i])
    zeros = len(sentlist) - len(qword_q_count_map)
    for qval in qword_q_count_map.values():                                                 #counts number of words asked about for qval number of times
      if qval in qword_q_count_total:
        qword_q_count_total[qval] = qword_q_count_total[qval] + 1
      else:
        qword_q_count_total[qval] = 1
    if 0 in qword_q_count_total:
      qword_q_count_total[0] += zeros
    else: 
      qword_q_count_total[0] = zeros
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
        if word in amb_word_freqs:
          amb_word_freqs[word] += 1
        else:
          amb_word_freqs[word] = 1
      else:
        if word in word_dict:
          unamb_words_idfs.append(idf_calc.idf(word_dict[word]))
        else:
          unamb_words_idfs.append(idf_calc.idf(word))
  avg_diff_per_task[key] = get_avg_diff(diffs_for_task)
  kwords_by_sent_all+= kwordsbySent
  kwords_by_task[key] = add_map_list(kwordsbySent)                  #gets frequencies of keywords for a task and adds to kwords_by_task with taskID as key
  master_context_labels = add_lists(master_context_labels, context_labels)         #updates master_context_label counts
  avg_std_dev_per_task[key] = sum([tup[2] for tup in meanandDevs]) / len(meanandDevs)
  workers = task.get_workers()
  scale_corrs = get_scale_corrs(workers)
  task_corrs = []
  for tup in scale_corrs:
    task_corrs.append(tup[2])
  worker_corrs.append(numpy.mean(task_corrs))
  mean_scales_by_task.append(numpy.mean(scale_means))
  task_scales_per_worker = {}                                               #{worker ID: [scale per sentence]}
  for worker in workers:
    wID = worker.get_ID()
    avg_scale = 1.0*sum(map(int_scale, worker.get_scales()))/len(worker.get_scales())
    if wID not in avg_scales_per_worker:
      avg_scales_per_worker[wID] = [avg_scale]
      all_scales_per_worker[wID] = map(int_scale, worker.get_scales())
    else:
      avg_scales_per_worker[wID].append(avg_scale)
      all_scales_per_worker[wID]+= map(int_scale, worker.get_scales())
    task_scales_per_worker[wID] = map(int_scale, worker.get_scales())
    
  for i in range(len(workers)):
    w1 = workers[i].get_ID()
    other_workers = workers[0:i] + workers[i+1:]
    other_worker_avgs = get_other_workers_avg(other_workers, task_scales_per_worker)
    worker_scale_comparison.append((w1, numpy.corrcoef(map(int_scale, workers[i].get_scales()), other_worker_avgs)[0][1]))
  worker_scale_comparison_per_task[key] = worker_scale_comparison
  
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
    context_percentage_map[context_map[i]].append(1.0*contextfreq/sum(map(int,context_labels)))
  
  info.append("\n\n------------------Overlap-----------------------\n")
  sums = {"equal":0, "intersect":0, "proper":0}
  for overlap in overlaps:
    for key in sums.keys():
      sums[key]+=overlap[key]
  
  for key in sums:
    info.append(key+": "+str(sums[key])+"\t")
  
  info.append("\n\n\n")
  
info.append("\n\n-----------------Confidence Interval of Task Lengths-----------------")
info.append("\n(mean, lower bound, upper bound) " + str(mean_confidence_interval(task_lengths)))
info.append("\nmin: " + str(min(task_lengths))+ "\nmax: " + str(max(task_lengths)))

info.append("\n\n----------------Correlation between Worker and Other Workers per Task-------------------")
for key in worker_scale_comparison_per_task:
  info.append("\nTask " + key + ":\n")
  avgs = []
  for tup in worker_scale_comparison_per_task[key]:
    avgs.append(tup[1])
    info.append("\t" + tup[0] + ":\t" + str(tup[1]) + "\n")


info.append("\n---------Average Standard Deviation of Specificity Ratings and Correlation between Annotators per Task---------------")
avg_std_dev_per_task_list = sorted(avg_std_dev_per_task.items(), key= lambda tup:tup[1])
for tup in avg_std_dev_per_task_list:
  correlations = [item[1] for item in worker_scale_comparison_per_task[tup[0]]]
  #info.append("\nTask " + tup[0] + ":\t\t stdv: %7s" % str(round(tup[1], 3)) + "\t\tcorr: %7s" % str(round(numpy.mean(correlations), 3)))
  info.append("\n" + tup[0] + "\t" + str(round(tup[1], 3)) + "\t" + str(round(avg_diff_per_task[tup[0]], 3)) + "\t" +  str(round(numpy.mean(correlations), 3)))



info.append("\n\n---------Average Standard Deviation of Specificity Ratings and Correlation between Annotators per Task SORTED BY ALPHA---------------")
avg_worker_scale_comparison_per_task = []
for key in worker_scale_comparison_per_task:
  avg_worker_scale_comparison_per_task.append((key, numpy.mean([tup[1] for tup in worker_scale_comparison_per_task[key]])))
avg_worker_scale_comparison_per_task = sorted(avg_worker_scale_comparison_per_task, key= lambda tup:tup[1])
for tup in avg_worker_scale_comparison_per_task:
  info.append("\n" + tup[0] + "\t" + str(round(avg_std_dev_per_task[tup[0]], 3)) + "\t" + str(round(avg_diff_per_task[tup[0]], 3)) + "\t" +  str(round(tup[1], 3)))


print "Average pairwise difference in scale: " + str(round(numpy.mean(avg_diff_per_task.values()), 3))

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
info.append("\nWorker Correlation with Average of other Workers: ")
for i in range(len(workers)):
  w1 = workers[i].get_ID()
  other_workers = workers[0:i] + workers[i+1:]
  other_worker_avgs = get_other_workers_avg(other_workers, all_scales_per_worker)
  info.append("\n\t" + w1 + ": " + str(numpy.corrcoef(all_scales_per_worker[w1], other_worker_avgs)[0][1]))

info.append("\n\n----------z-Score Correlation between Worker and Other Workers--------")
all_zscores_per_worker = {}
for i in range(len(workers)):
  w1 = workers[i].get_ID()
  all_zscores_per_worker[w1] = stats.zscore(all_scales_per_worker[w1])
for i in range(len(workers)):
  w1 = workers[i].get_ID()
  other_workers = workers[0:i] + workers[i+1:]
  other_worker_avgs = get_other_workers_avg(other_workers, all_zscores_per_worker)
  info.append("\n\t" + w1 + ": " + str(numpy.corrcoef(all_zscores_per_worker[w1], other_worker_avgs)[0][1]))
  
  
info.append("\nPercentage of No Labels and Avg Scale per task correlation: " +  str(numpy.corrcoef(context_percentage_map["No"], mean_scales_by_task)[0][1]))
info.append("\nPercentage of Immediate Labels and Avg Scale per task correlation: " +  str(numpy.corrcoef(context_percentage_map["Immediate"], mean_scales_by_task)[0][1]))
info.append("\nPercentage of Some Labels and Avg Scale per task correlation: " +  str(numpy.corrcoef(context_percentage_map["Some"], mean_scales_by_task)[0][1]))
info.append("\nCorrelation between Worker Correlation and Task Generality: " + str(numpy.corrcoef(mean_scales_by_task, worker_corrs)[0][1]))
all_kword_freqs = add_map_list(kwords_by_task.values())                        #turn list of maps by task into one map
all_kword_items = all_kword_freqs.items()                                      #get list of items
all_kword_percents = get_percentages([item[1] for item in all_kword_items])    #items -> kword, percentages
info.append("\nPercentage of Question Word by Type: \n")
info.append("\n\nAverage Rating Specificity by Question type\n")
kword_sent_scale = {"who": [0,0,0,0], "what": [0,0,0,0], "where": [0,0,0,0], "when": [0,0,0,0], "why": [0,0,0,0], "how": [0,0,0,0], "which": [0,0,0,0], "": [0,0,0,0]} 
#[present, not present, number present, number not present]
for i in range(len(kwords_by_sent_all)):               #list of maps: {key = keyword (e.g. "what", "how"), value = frequency}
  for key in kwords_by_sent_all[i]:
    if kwords_by_sent_all[i][key] != 0:
      kword_sent_scale[key][0]+= mean_scales[i]
      kword_sent_scale[key][2]+=1
    else:
      kword_sent_scale[key][1]+= mean_scales[i]
      kword_sent_scale[key][3]+=1

for i, item in enumerate(all_kword_items):
  if item[0] == "":
    info.append("\t" + "%-6s"%("none") + ": "+ "%-7s"%(str(round(all_kword_percents[i], 2)) + "%"))
    info.append("\t\t" + "%-7s"%(str(round(1.0*kword_sent_scale[item[0]][0]/kword_sent_scale[item[0]][2], 3))) + "\t\t\t" +  str(round(1.0*kword_sent_scale[item[0]][1]/kword_sent_scale[item[0]][3], 3)) + "\n") 
  else:  
    info.append("\t" + "%-6s"%(item[0]) + ": "+ "%-7s"%(str(round(all_kword_percents[i], 2)) + "%") )
    info.append("\t\t" + "%-7s"%(str(round(1.0*kword_sent_scale[item[0]][0]/kword_sent_scale[item[0]][2], 3))) + "\t\t\t" + str(round(1.0*kword_sent_scale[item[0]][1]/kword_sent_scale[item[0]][3], 3)) + "\n") 
percent_context_labels = get_percentages(master_context_labels)                #get percentages of context labels
info.append("\nPercentage of Context Labels in Corpus: \n")
for i, label in enumerate(percent_context_labels):
  info.append("\t" + "%-9s"%(context_map[i]) + ": " + str(round(label,2)) + "%\n")
info.append("\n\nOverlap Counts\n")
for key in overlap_freqs:
  info.append(key + ": " + str(overlap_freqs[key]) + "\n")
info.append("total # of questions: " + str(sum(num_qs)))

total_num_words = sum(qword_q_count_total.values())
info.append("\nQuestion word proportions: ")
for item in qword_q_count_total.items():
  info.append("\n # Q's: " + str(item[0]) + "\t Percentage of words: " + "%.2f"%(item[1]))

info.append("\n\nambiguous words idfs: " + str(mean_confidence_interval(amb_phrase_idfs)))
info.append("\nunambiguous words idfs: " + str(mean_confidence_interval(unamb_words_idfs)))


#PRINTING THINGS
print "ambiguous words idfs: " + str(mean_confidence_interval(amb_phrase_idfs))
print "unambiguous words idfs: " + str(mean_confidence_interval(unamb_words_idfs))
print "average worker correlation: " + str(numpy.mean(all_corrs))
print "map of keywords: \n" + str(all_kword_freqs)
print "list of context label frequencies: " +  str(master_context_labels)
print "Question Number and Scale Correlation by Sentence: " + str(round(numpy.corrcoef(mean_scales, num_qs)[0][1], 3))
#print sorted(amb_word_freqs.items(), key=lambda item: item[1])
#print "weird ambiguous word correlation: " + str(numpy.corrcoef(amb_words, amb_words_idfs)[1][0])

print "NUMBER OF SENTENCES: " + str(len(mean_scales))

outFile = open("output/combined_output-stats.txt","w")

for line in info:
  outFile.write(line)

outFile.close()
out.close()
out_overlaps.close()

#-------------------------------------------------PLOTTING THINGS--------------------------------------------------------------
wIDs = avg_scales_per_worker.keys()
"""
for i in range(len(avg_scales_per_worker)):
  for j in range(i+1, len(avg_scales_per_worker)):
    w1_new_scales, w2_new_scales, sizes = worker_correlation_plot_helper(all_scales_per_worker[wIDs[i]], all_scales_per_worker[wIDs[j]])
    plot_corr("Annotator Ratings", wIDs[i], wIDs[j], w1_new_scales, w2_new_scales, sizes)"""

counted_worker_scales = []
bar_labels = []
for k in range(len(avg_scales_per_worker)):
  counted_worker_scales.append(count_list(all_scales_per_worker[wIDs[k]]))
  bar_labels.append(wIDs[k])
make_barchart("Annotator Specificity Rating Frequency", "Rating", "Frequency", counted_worker_scales, bar_labels, range(7), 7)

distribution = get_worker_percentage_distribution(counted_worker_scales)
list_rand_diffs = []

for i in range(1000):
  rand_diffs = [0]*7
  rand_sent_annots = generate_annotations_all_sents(len(all_scales_per_worker[wIDs[0]]), len(wIDs), distribution)  #list of lists of 3 ints
  for sent in rand_sent_annots:
    rand_diffs = count_differences(sent, rand_diffs)
  list_rand_diffs.append(rand_diffs)
trans_rand_diffs = transpose_lists(*list_rand_diffs)
rand_diffs_ci = []
for i in range(len(trans_rand_diffs)):
  rand_diffs_ci.append(mean_confidence_interval(trans_rand_diffs[i]))
print rand_diffs_ci
avg_rand_diffs = add_lists(*list_rand_diffs)

for i in range(len(avg_rand_diffs)):
  avg_rand_diffs[i]/=1.0*len(list_rand_diffs)


alpha_labels = [0.0, 0.5, 0.7, 0.8, 1]
alphas = [tup[1] for tup in avg_worker_scale_comparison_per_task]
alpha_freqs = [0]*4
for alpha in alphas:
  for i in range(1, len(alpha_labels)):
    if alpha < alpha_labels[i]:
      alpha_freqs[i-1]+=1
      break
make_barchart("Cronbach's Alpha for Specificity Ratings by Article", "Cronbach's Alpha", "Frequency", [alpha_freqs], [], write_bar_labels(alpha_labels))


make_barchart("Frequency of Pairwise Annotator Differences vs. Randomly Generated Differences\nin Specificity Rating per Sentence", "Difference between Ratings per Sentence", "Frequency", [differences, avg_rand_diffs], ["Human Annotators", "Randomly Generated"], range(len(rand_diffs)), 7)

plot_corr("Average Correlation between Annotators vs. Mean Rating per Task", "Mean Rating", "Correlation", mean_scales_by_task, worker_corrs)
plot_corr("Percent of Sentence Specificity vs. Mean Rating per Sentence", "Mean Rating", "% Specific", mean_scales, percent_specific)
by_task_labels = numpy.arange(0, 7, 1)
by_sent_labels = range(7)
make_barchart("Average Specificity Ratings of Task", "Average Rating", "Frequency", [count_scales(mean_scales_by_task, by_task_labels)], [], write_bar_labels(by_task_labels))
make_barchart("Average Specificity Ratings of Sentences", "Average Rating", "Frequency", [count_scales(mean_scales, by_sent_labels)], [], write_bar_labels(by_sent_labels), 6)

#make_barchart("Frequency of Pairwise Worker Differences in Specificity Rating per Sentence", "Difference between Ratings per Sentence", "Frequency", [differences], [], range(len(differences)), 7)







