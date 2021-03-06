import numpy
import xml.etree.ElementTree as ET
from parse_turk_data import main
from sets import Set

#IMPORTANT NOTE: order of turk task input file = order of xml input

'''This script parses an xml tree created by StanfordCoreNLP. It also takes in the corresponding mTurk .input and .results files to match Sentence and Question objects with the tokens in the xml files. 

This script was written with the intention of finding the correlation between the number of words asked about for each POS with the average scale.
'''
	
def parse_tree(root):
	'''@param root of an xml tree 
	@return a dictionary {POS:[all words in sentence of this POS]}'''
	dicts = []
	for doc in root:
		sentences = doc.findall('sentences')
		for sent in sentences:
			sent_list = sent.findall('sentence')
			for i in range(len(sent_list)):
				pos_dict = {"C": [], "DT": [], "EX": [], "FW": [], "PREP": [], "ADJ": [], "NN": [], "NNP": [], "PR": [], "ADV": [], "PART": [], "VB": [], "SYM": []}
				mapping = {"CC": "C", "CD": "SYM", "DT": "DT", "EX": "EX", "FW": "FW", "IN": "PREP", "JJ": "ADJ", "JJR": "ADJ", "JJS": "ADJ", "NN": "NN", "NNS": "NN", "NNP": "NNP", "NNPS": "NNP", "PDT": "DT", "PRP": "PR", "PRP$": "PR", "RB": "ADV", "RBR": "ADV", "RBS": "ADV", "RP": "PART", "SYM": "SYM", "TO": "C", "VB": "VB", "VBD": "VB", "VBG":"VB", "VBN": "VB", "VBP":"VB", "VBZ":"VB", "WDT": "DT", "WP$": "PR", "WRB": "ADV"}
				sent = sent_list[i]
				ts = sent.findall('tokens')
				for token in ts:
					token_list = token.findall('token')
					for i in range(len(token_list)):
						t = token_list[i]
						if t.find("POS").text in pos_dict.keys():
							pos_dict[t.find('POS').text].append(t.find("word").text)
				dicts.append(pos_dict)
	return dicts

'''def get_type(t, sentence):
	gives the number of phrases marked ambiguous in given sentence
	@param type = string ("noun", "proper", etc.), sentence = [int]
	@return [int]
	
	types = {"noun":2, "proper":3, "event":4, "pronoun": 5, "verb":6, "adj":7, "adv":8, "preposition":9, "article":10, "conjunction":11}
	return sentence[types[t]]'''
	
def get_corr(l1, l2):
	'''gets the correlation between 2 lists as long as neither of them are only 0s.
	@param 2 lists
	@return correlation coefficient (float)'''
	if l1 == [0.0]*len(l1) or l2 == [0.0]*len(l1):
		return " NA"
	return numpy.corrcoef(l1,l2)[0][1]
	
'''def get_corr_of_type(t, sentences):
	type_freqs = []
	scales = []
	for sent in sentences:
		if get_type(t,sent)!=0:
			scales.append(sent[1])
			type_freqs.append(get_type(t,sent)/len(sent))
	return get_corr(type_freqs, scales)'''

def get_freqs(t, dicts):	
	'''Given a POS t and a list of dictionaries, this function finds the number of words that of POS t for each dictionary
	@param t is POS, dicts = list of dictionaries (each dictionary represents a sentence)
	@return [int] - list of frequencies of words that are POS t in each dictionary. index = index of dict in dicts (ie. index of sentence)'''
  freqs = []
  for d in dicts:
  	if t in d:
  		freqs.append(len(list(Set(d[t]))))
  return freqs
  
def get_tasks(num):
	'''@param number of tasks one plans on entering.
	@return [tasks] and [[sentences of each task]] objects. 
	Order of sentences corresponds to order of input files'''
	all_tasks = []
	sents = []	#list of lists where each list corresponds to a task
	for i in range(num):
		fname, tasks = main()
		outFile = open(fname[0:fname.index(".")] + "_sentences.txt","w")
		scaleFile = open(fname[0:fname.index(".")] + "_scales.txt","w")
		sent_list = []
		for key in tasks:
			task = tasks[key]
			all_tasks.append(task)
			sentences = task.get_sentences()
			sent_list+=sentences
			for sent in sentences:
				outFile.write(sent.get_sent())
				tot = 0.0
				scales = sent.get_scales()
				for scale in scales:
					tot+=float(scale[0])			
				scaleFile.write(str(tot/len(sent.get_scales()))+"\n")
		outFile.close()
		sents.append(sent_list)
		
	return all_tasks, sents


def write_corr_file(all_dicts, scales, fname):
	'''writes the file that has correlations between number of words of each POS and specificity scale
	@param [{POS:[words]}], [int], "name of output file"'''
	outFile = open('output/'+fname+"_corr1.txt","w")
	for t in all_dicts[0]:
		corr = get_corr(get_freqs(t,all_dicts), scales)
		outFile.write(t + "\t" + str(corr)+ "\n")
	outFile.close()

def get_amb_words_dict(root, sents):
	''' given a tree and list of sentences, this function gives a dictionary that stores the words that are of each POS
	@param root of tree, [Sentence object]
	@return [{POS:[words in sentence]}]; index of list of dicts = sentence number'''
	dicts = []
	for doc in root:
		for sent in doc.findall("sentences"):
			for i in range(len(sent.findall("sentence"))):
				s = sent.findall("sentence")[i]
				pos_dict = {"C": [], "DT": [], "EX": [], "FW": [], "PREP": [], "ADJ": [], "NN": [], "NNP": [], "PR": [], "ADV": [], "PART": [], "VB": [], "SYM": []}
				mapping = {"CC": "C", "CD": "SYM", "DT": "DT", "EX": "EX", "FW": "FW", "IN": "PREP", "JJ": "ADJ", "JJR": "ADJ", "JJS": "ADJ", "NN": "NN", "NNS": "NN", "NNP": "NNP", "NNPS": "NNP", "PDT": "DT", "PRP": "PR", "PRP$": "PR", "RB": "ADV", "RBR": "ADV", "RBS": "ADV", "RP": "PART", "SYM": "SYM", "TO": "C", "VB": "VB", "VBD": "VB", "VBG":"VB", "VBN": "VB", "VBP":"VB", "VBZ":"VB", "WDT": "DT", "WP$": "PR", "WRB": "ADV"}
				quests = sents[i].get_questions()
				tokens = s.findall("tokens")[0].findall("token")
				
				for q in quests:
					low = q.get_low()
					high = q.get_high()
					for j in range(low, high+1):
						token = tokens[j]
						if token.find("POS").text in pos_dict.keys():
							pos_dict[mapping[token.find("POS").text]].append(token.find("word").text)	
				dicts.append(pos_dict)
	return dicts

outFile = open("ambTypesScales.txt","w")

tasks, sents = get_tasks(2)

roots = []
all_dicts = []	#each dict corresponds to sent {POS:[words in sent]}
amb_phrases_dicts=[]
scales = []			#[float]

while True:
	fname = raw_input("Enter xml file name (press enter when done): ")
	scale_fname = raw_input("Enter file with scales (press enter when done): ")
	
	if fname == "" or scale_fname == "":		#user hits ENTER for both prompts, signalling end of list of files
		break
	else:
		scales += map(float, open(scale_fname, "r").readlines())
		doc = ET.parse(fname)
		root = doc.getroot().findall('document')
		roots.append(root)

for i in range(len(roots)):
	all_dicts += (parse_tree(roots[i]))
	amb_phrases_dicts += (get_amb_words_dict(roots[i], sents[i]))

write_corr_file(amb_phrases_dicts, scales, "amb")
write_corr_file(all_dicts, scales, "all")


'''StanfordCoreNLP POS:
#pos_dict = {"CC":[], "CD":[], "DT":[], "EX":[], "FW":[], "IN":[], "JJ":[], "JJR":[], "JJS":[], "LS":[], "MD":[], "NN":[], "NNS":[], "NNP":[], "NNPS":[], "PDT":[], "POS":[], "PRP":[], "PRP$":[], "RB":[], "RBR":[], "RBS":[], "RP":[], "SYM":[], "TO":[], "UH":[], "VB":[], "VBD":[], "VBG":[], "VBP":[], "VBZ":[], "WDT":[], "WP":[], "WP$":[], "WRB":[]}'''

