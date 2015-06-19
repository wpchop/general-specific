import numpy
import xml.etree.ElementTree as ET
from parse_turk_data import main
from sets import Set
'''check if avg_scale is in token list.find("word").text rather than checking first token.
if so, take tokens from 2 after it'''

'''order of turk task input file = order of xml input'''

def get_text_of_word(t):
	return t.find("word").text
	
def parse_tree(root):
	dicts = []
	for doc in root:
		sentences = doc.findall('sentences')
		for sent in sentences:
			sent_list = sent.findall('sentence')
			for i in range(len(sent_list)):
				pos_dict = {"CC":[], "CD":[], "DT":[], "EX":[], "FW":[], "IN":[], "JJ":[], "JJR":[], "JJS":[], "LS":[], "MD":[], "NN":[], "NNS":[], "NNP":[], "NNPS":[], "PDT":[], "POS":[], "PRP":[], "PRP$":[], "RB":[], "RBR":[], "RBS":[], "RP":[], "SYM":[], "TO":[], "UH":[], "VB":[], "VBD":[], "VBG":[], "VBP":[], "VBZ":[], "WDT":[], "WP":[], "WP$":[], "WRB":[]}
				sent = sent_list[i]
				ts = sent.findall('tokens')
				for token in ts:
					token_list = token.findall('token')
					#l = map(get_text_of_word, token_list)
					for i in range(len(token_list)):
						t = token_list[i]
						if t.find("POS").text in pos_dict.keys():
							pos_dict[t.find('POS').text].append(t.find("word").text)
				dicts.append(pos_dict)
					
		
	return (dicts)

def get_type(t, sentence):
	'''gives the number of phrases marked ambiguous in given sentence
	@param type = string ("noun", "proper", etc.), sentence = [int]
	@return [int]
	'''
	types = {"noun":2, "proper":3, "event":4, "pronoun": 5, "verb":6, "adj":7, "adv":8, "preposition":9, "article":10, "conjunction":11}
	return sentence[types[t]]
	
def get_corr(l1, l2):
	if l1 == [0.0]*len(l1):
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

def get_freqs(t, dicts):	#t is POS, dicts = list of dictionaries
  freqs = []
  for d in dicts:
  	if t in d:
  		freqs.append(len(list(Set(d[t]))))
  return freqs
  
def get_tasks(num):
	'''returns tasks and sentence objects. Order of sentences correspond to order of input files'''
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
	outFile = open(fname+"_corr1.txt","w")
	for t in all_dicts[0]:
		corr = get_corr(get_freqs(t,all_dicts), scales)
		outFile.write(t + "\t" + str(corr)+ "\n")
	outFile.close()

def get_amb_words_dict(root, sents):
	dicts = []
		
	for doc in root:
		for sent in doc.findall("sentences"):
			for i in range(len(sent.findall("sentence"))):
				s = sent.findall("sentence")[i]
				pos_dict = {"CC":[], "CD":[], "DT":[], "EX":[], "FW":[], "IN":[], "JJ":[], "JJR":[], "JJS":[], "LS":[], "MD":[], "NN":[], "NNS":[], "NNP":[], "NNPS":[], "PDT":[], "POS":[], "PRP":[], "PRP$":[], "RB":[], "RBR":[], "RBS":[], "RP":[], "SYM":[], "TO":[], "UH":[], "VB":[], "VBD":[], "VBG":[], "VBP":[], "VBZ":[], "WDT":[], "WP":[], "WP$":[], "WRB":[]}
				quests = sents[i].get_questions()
				tokens = s.findall("tokens")[0].findall("token")
				
				for q in quests:
					low = q.get_low()
					high = q.get_high()
					for j in range(low, high+1):
						token = tokens[j]
						if token.find("POS").text in pos_dict.keys():
							pos_dict[token.find("POS").text].append(token.find("word").text)	
				dicts.append(pos_dict)
		
	return (dicts)

outFile = open("ambTypesScales.txt","w")\

tasks, sents = get_tasks(2)

roots = []
all_dicts = []	#each dict corresponds to sent {POS:[words in sent]}
amb_phrases_dicts=[]
scales = []			#[float]

while True:
	fname = raw_input("Enter xml file name (press enter when done): ")
	scale_fname = raw_input("Enter file with scales: ")
	
	if fname == "" or scale_fname == "":
		break
	else:
		scales += map(float, open(scale_fname, "r").readlines())
		doc = ET.parse(fname)
		root = doc.getroot().findall('document')
		roots.append(root)

for i in range(len(roots)):
	all_dicts += (parse_tree(roots[i]))
	amb_phrases_dicts += (get_amb_words_dict(roots[i], sents[i]))
	amb_phrases_dicts

write_corr_file(amb_phrases_dicts, scales, "amb")
write_corr_file(all_dicts, scales, "all")


