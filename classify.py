from sets import Set
from random import choice
from gather import main as gatherm
from ExternalDict import ExternalDict
from idfCalculator import idfCalculator

#-----------------------------Basic Functions--------------------------------------
def words(string):
  '''Lowers and divides a given string into a list of words.'''
  return string.lower().split()


def ispunct(string):
  '''Checks if the given string is just punctuation. Returns True or False.'''
  punct = list(",.?!@#$%^&*~()_+-=[]{};:'\"></\|")
  result = True
  for char in string:
    result = (char in punct)            #If char is punct, result = True
    if not result:                      #If result is False, return False
      return result
  return result
  

#-------------------------Building Word Dictionary---------------------------------
def get_list_of_all_sentences(data_dict):
  '''Returns a list of all sentences from all data.'''
  sentences = []
  for data in data_dict.values():                                                  #If new data format, add something here
    if type(data) is list:
      for tup in data:
        sentences.append( tup[1] )
    else:
      for sent in data.get_sentences():
        sentences.append( sent.get_sent() )
  return sentences


def get_word_list(data_dict):
  '''Gets a list of every word contained in the data's sentences. Returns the list.'''
  return words(" ".join( get_list_of_all_sentences(data_dict) ))


def get_word_dict(data_dict, choice):
  '''Gets the appropriate word dictionary based on the provided choice.
  pre: data_dict is a dictionary of Tasks or fnames, and choice is an int 0-1.
  post: Returns an ExternalDict such that {"word:wordID}'''
  word_dict = ExternalDict("NYT/word.dict")                               #If .test file... Leave word dict as is.
  if choice == 0:                                                         #If .train file...
    word_dict.add_list( Set(get_word_list(data_dict)) )                   #Update word dictionary {"word:wordID}
  return word_dict


#---------------------------------Features-----------------------------------------

#------Term Frequency: Words & Punctuation------
def get_ftup(sentence, word_dict):
  '''Takes in a sentence (string) and creates a term frequency dict and a
  punctuation count for it using the provided word dictionary.
  pre: sentence is a tokenized string.
  word_dict is an ExternalDict such that {"word": int}
  post: returns a tf dictionary of the form {wordID:count_int} and an int that is 
  #ofpunctuation in sentence.'''
  tf_dict, p_count = {}, 0
  for word in words(sentence):                          #For each word in the sentence
    if word in word_dict:                                 #If word is in the dictionary (.train = always, .test = not always)
      wordID = word_dict[word]                              #Get the word's ID
      if ispunct(word):                                     #If punctuation, add to count
        p_count += 1
      elif wordID in tf_dict.keys():                        #If the word has already appeared, add to it
        tf_dict[ wordID ] += 1
      else:                                                 #If the word hasn't yet appeared, add as new key
        tf_dict[ wordID ] = 1
    else:                                                 #if word not in dictionary (.test, if it wasn't in training data)
      pass
  return (tf_dict, p_count)


def get_ftups(sentences, word_dict):
  '''Takes in a list of sentences and the word dictionary and
  finds the term frequency dictionaries for each sentences and 
  returns that list.
  pre: sentences is list of strings, word_dict is an ExternalDict such that {"word":int}
  post: returns a list of tuples, each containing two dictionaries,
  (term_freq_dict, punct_freq_dict).'''
  ls = []
  for sentence in sentences:
    ls.append(get_ftup(sentence, word_dict) )
  return ls


def associate_data_with_features(data_dict, word_dict):
  '''Creates a dictionary of the form:
     Task/list of tuples : [( {term freq}, punct_count ), ...]
  where each tuple is for Sentence #[index] in the Task or list of tuples. The 
  inner dictionary is of the form {wordID:int}.
  pre: data_dict is a dictionary of all dataIDs associated with their data:
      -taskIDs associated with their Task object OR
      -filenames associated with a list of tuples (rating, "sentence")
  word_dict is an ExternalDict such that {"word":wordID}
  post: returns a dictionary as described above.'''
  data_to_ftups = {}
  for data in data_dict.values():
    if type(data) is list:
      data_to_ftups[tuple(data)] = get_ftups([tup[1] for tup in data], word_dict)
    else:
      data_to_ftups[data] = get_ftups(data.get_sentences_as_strings(), word_dict)
  return data_to_ftups


#--------------------------------File Output---------------------------------------

#------Interpreting Data------------------------
def categorize(scale):
  '''Given a scale rating 0-6, returns a binary
  category, 0 for specific and 1 for general.
  Note: If given 3, will randomly pick a category.'''
  if scale < 3:
    return 0
  if scale > 3:
    return 1
  else:
    return choice([0,1])


def mean(sent):
  '''Returns the mean scale of the provided Sentence object.'''
  add = 0
  skips = 0
  for i in sent.get_scales():
    if i[0] == 'NA':
      skips += 1
    else:
      i = int(i[0])
      add += i
  return add/(len(sent.get_scales()) - skips)


def sort_wordIDs(*dict_args):
  '''Collects the keys of all provided dictionaries into a list and sorts numerically.
  pre: Any number of dictionaries with keys representing wordIDs
  post: returns a list of wordIDs sorted from least to greatest'''
  ls = []
  for dic in dict_args:
    ls.extend(dic.keys())
  return sorted(ls)


def get_tf(freq, total_terms):
  '''Interprets the term frequency for a term given its frequency in the document
  and the total number of terms in that document.
  pre: freq and total_terms are ints.
  post: returns a float representing term frequency.'''
  return freq/float(total_terms)


def get_tfidf(tf, idf):
  '''Returns the tf-idf.'''
  return tf * idf

#------Feature Options--------------------------
def match_choice_to_func(choice): #See commented ints below
  '''Choice in an int 0-2, representing which feature output to use.
  post: returns a function to create a line of output when given a feature tuple for
  a particular sentence.'''
  d = {0:pf_count, 1:tf_feature_string, 2:tfidf_feature_string, 3:all_feature_string}
  return d[choice]


def pf_count(f_tup): #0
  '''Takes in a sentence's f_tup and returns a segment 
  of a line for the output file, namely "0:#ofpunct" where 0 is the feature id.
  pre: f_tup is a tuple of dictionaries -> ({wordID:freq}, {punctID:freq})
  post: returns a string of the form "0:#ofpunct\\n", unless #ofpunct is 0, which
  returns newline.'''
  num = f_tup[1]
  if num != 0:
    return " 0:"+str(num)+'\n'
  return "\n"


def tf_feature_string(f_tup): #1
  '''Takes in the tuple containing the features for the sentence. Uses this info to
  return a string for the LibSVM classifier using ONLY word frequencies.
  pre: f_tup is a tuple -> ( {term freq}, punct_count ),
  post: returns a string in the following form: "0:freq 1:freq ... n:freq"'''
  line = ''  
  num_terms = float(len(f_tup[0].keys()))
  wordIDs = sort_wordIDs(f_tup[0])
  for wordID in wordIDs:
    line += " " + str(wordID) + ":" + str( get_tf(f_tup[0][wordID],num_terms) )
  return line+"\n"


def tfidf_feature_string(f_tup): #2
  '''Takes in the tuple containing the geatures for the setnences. Uses this info
  to return a string for the LibSVM classifier using ONLY tf-idf.add_tasks
  pre: f_tup is a tuple -> ( {term freq}, punct_count )
  post: returns a string in the following form: "0:freq 1:freq ... n:freq"'''
  line = ''
  len_doc = float(len(f_tup[0].keys()))
  wordIDs = sort_wordIDs(f_tup[0])
  idfCalc = idfCalculator()
  
  for wordID in wordIDs:
    tf = get_tf( f_tup[0][wordID], len_doc)
    idf = idfCalc[wordID]
    line += " " + str(wordID) + ":" + str( get_tfidf(tf, idf) )
    
  return line+"\n"
  

def all_feature_string(f_tup): #3
  '''Takes in the tuple containing the features for the sentence. Uses this info to
  return a string for the LibSVM classifier using BOTH punct count and TF-IDF.
  pre: f_tup is a tuple -> ({wordID:freq}, punct_count)
  post: returns a string in the following form: "0:freq 1:freq ... n:freq"'''
  line = pf_count(f_tup).strip('\n')            #Punct count
  line += tfidf_feature_string(f_tup)           #tfidf
  return line

#------Output File Creation---------------------
def output_string(data_to_features, choice):
  '''Takes in a dictionary of data with their features, and a user provided choice 
  to indicate which features to use.
  pre: The dictionary is of the form {Task/listoftups : [( {term freq}, punct_count ), ...]}, and
  choice is an int between 0 and 2, inclusive.
  post: returns a string to output to a file.'''
  outstr = ""
  for data in data_to_features:
  
    if type(data) is tuple:
      sentences = data                    #tuple of tuples
      ratings = [tup[0] for tup in data]  #list of ints
    else:
      sentences = data.get_sentences()                #list of Sentences
      ratings = map(categorize, map(mean, sentences)) #list of ints
    
    for i in range(len(sentences)):
      ftup = data_to_features[data][i]                                             #This is ({term freq}, p_count)
      outstr += get_output_line(ratings[i], choice, ftup)
      
  return outstr


def get_output_line(rating, choice, f_tup):
  '''Given the rating, the feature choice, and the feature tuple for a 
  sentence, this function will return a string representing the output line for the
  sentence. "0 34:3 56:1"...etc
  pre: rating is an int 0-1, choice is an int 0-2, and ftup is a feature tuple
  post: returns the line as a string'''
  line = str( rating )                              #"0" or "1" for specific or general
  line += (match_choice_to_func(choice))(f_tup)     #+ " 0:freq 1:freq ... n:feq\n"
  return line


def make_fname(file_type):
  '''Uses the user's choice of file type to create a file name for the final output.
  pre: file_type is either 0 or 1, corresponding to .train and .test respectively.
  post: returns a string for use as a file name.'''
  if file_type == 0:
    return "specific.train"
  else:
    return "specific.test"


def write_output(outstr, f_name):
  '''Creates an output file containing the provided string outstr. The file will be
  named with the provided f_name. 
  WARNING: Will overwrite another file of the same name.'''
  outFile = open('output/'+f_name,"w")
  outFile.write(outstr)
  outFile.close()
  
  
def main():
    (file_type, feature_choice, data_dict) = gatherm()                          #Collect user input and data from gather.py
    word_dict = get_word_dict(data_dict, file_type)                             #ExternalDict {"word:wordID}
  
    data_to_features = associate_data_with_features(data_dict, word_dict)       #Task/listoftups : [( {term freq}, punct_count ), ...]
 
    word_dict.save()
    outstr = output_string(data_to_features, feature_choice)
    write_output( outstr, make_fname(file_type))
    
main()