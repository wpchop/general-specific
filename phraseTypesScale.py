import numpy
import xml.etree.ElementTree as ET
'''check if avg_scale is in token list.find("word").text rather than checking first token.
if so, take tokens from 2 after it'''

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
	
def get_corr_of_type(t, sentences):
	type_freqs = []
	scales = []
	for sent in sentences:
		if get_type(t,sent)!=0:
			scales.append(sent[1])
			type_freqs.append(get_type(t,sent)/len(sent))
	return get_corr(type_freqs, scales)

def get_freqs(t, dicts):	#t is POS, dicts = list of dictionaries
  freqs = []
  for d in dicts:
  	if t in d:
  		freqs.append(len(d[t]))
  return freqs
  

sents = []
outFile = open("ambTypesScales.txt","w")
scale_fname = raw_input("Enter file with scales:")
scales = map(float, open(scale_fname, "r").readlines())
while True:
  fname = raw_input("Enter text file name (press enter when done): ")
  if fname == "":
  	break
  else:
  	doc = ET.parse(fname)
  	root = doc.getroot().findall('document')
  	inFile = open(fname, "r")
  	'''sent = inFile.readline().strip().split("\t")
  	while True:
  		sent = inFile.readline().strip().split("\t")
  		if sent != [""]:
  			sents.append(map(float,sent))
  		else:
  			break
  	inFile.close()'''
  	
  	dicts = parse_tree(root)
  	print len(scales)
  	print len(dicts)
  	for t in dicts[0]:
  		print get_freqs(t,dicts)
  		print t
  		corr = get_corr(get_freqs(t,dicts), scales)
  		outFile.write(t + "\t" + str(corr)+ "\n")
		

types = {"noun":2, "proper":3, "event":4, "pronoun": 5, "verb":6, "adj":7, "adv":8, "preposition":9, "article":10, "conjunction":11}

'''for t in types.keys():
	outFile.write(t + "\t" + str(get_corr_of_type(t,sents))+ "\n")
'''

	
