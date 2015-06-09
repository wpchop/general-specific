import os.path
from parse_data import main as m
from sets import Set
from random import choice

#-----------------------------Basic Functions--------------------------------------
def words(string):
  '''Lowers and divides a given string into a list of words.'''
  return string.lower().split()


def merge_dicts(*dict_args):
    '''Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.'''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def ispunct(string):
  '''Checks if the given string is just punctuation. Returns True or False.'''
  punct = list(",.?!@#$%^&*~()_+-=[]{};:'\"></\|")
  result = True
  for char in string:
    result = (char in punct)            #If char is punct, result = True
    if not result:                      #If result is False, return False
      return result
  return result

#-----------------------------Task Collection--------------------------------------
def user_file_type():
  '''Asks user if they are creating a .train file or a .test file. Returns 0 if 
  .train and 1 if .test.'''
  choice = 3
  while choice not in range(2):
    choice = int(raw_input('''\nWhich of the following would you like to create?
  0: A .train file to train a LibSVM model.
  1: A .test file to test a LibSVM model's prediction.
Enter the appropriate integer: '''))
  return choice


def ask_user_for_tasks():
  '''Handles user input for the collection of all data from all tasks. Loops through
  task acception until user indicates they are finished.
  post: Returns a dictionary containing all tasks collected.'''
  task_dict = {}
  print ""
  while True:
    task_dict = add_tasks(task_dict)
    cont = raw_input("Are there more mTurk result files to include? y/n : ")
    if 'y' not in cont.lower(): break
  return task_dict


def add_tasks(task_dict):
  '''Adds tasks from an mTurk output to the provided dictionary.
  pre: task_dict is a dictionary of tasks.
  post: Returns a new dictionary with the tasks from the asked for files.'''
  more_tasks = m()
  new_dict = merge_dicts(task_dict, more_tasks)
  return new_dict


def user_feature_selection():
  '''Handles user input for selecting which features to analyze. Returns the choice
  as an int.
  0 = term frequency only
  1 = punctuation frequency only
  2 = term and punctuation frequency'''
  choice = 5
  while choice not in range(3):
    choice = int(raw_input('''\nWhich feature(s) would you like to look at?:
  0: Term frequency only
  1: Punctuation frequency only
  2: Both term and punctuation frequency
Enter the appropriate integer: '''))
  return choice


#-------------------------Building Word Dictionary---------------------------------
def is_word_dict_exist():
  '''Checks if a file named "word_dict.txt" exists and returns True or False.'''
  return os.path.isfile("word_dict.txt") 


def upload_word_dict():
  '''Looks for a file named "word_dict.txt" to upload that information to the dictionary.
  If no such file exists, assumes the dictionary is empty. Returns the filled word_dict
  and the highest id number found.
  post: Returns a tuple (word_dict, i) such that word_dict is a dictionary of the form
  "word":ID and i is the highest ID in the dictionary.'''
  if is_word_dict_exist():
    return read_word_dict_txt()
  else:
    return {}


def read_word_dict_txt():
  '''Reads a "word_dict.txt" file, building the dictionary it contains and returning
  that dictionary.
  post: Returns word_dict, a dictionary of the form "word":ID '''
  word_dict = {}
  dictFile = open("word_dict.txt", "r")
  items = dictFile.readlines()[0].strip().split("\t")
  for item in items:
    pair = item.split(">x<")
    word_dict[pair[0]] = int(pair[1])
  dictFile.close()
  return word_dict


def get_list_of_all_sentences(task_dict):
  '''Returns a list of all sentences from all tasks.'''
  sentences = []
  for task in task_dict.values():
    for sent in task.get_sentences():
      sentences.append( sent.get_sent() )
  return sentences


def get_word_set(word_dict, sentences):
  '''Takes in a list of sentences (strings) and returns a set of
  all words making up those sentences.
  pre: sentences is a list of strings
  post: returns an unordered, no-duplicates set of strings'''
  words_ls = words(" ".join(sentences))	        #Makes a big string then breaks @ spaces
  words_ls.extend(word_dict.keys())             #Adds on words already in dictionary
  words_s = Set(words_ls)					              #Removes duplicates and randomizes order
  return words_s


def __build_word_dict(word_dict, sentences):
  '''Fills the given dictionary with the individual words in the given
  list of sentences, and returns the full dictionary.
  pre: word_dict = {} or {"word": wordID}, sentences = list of strings}
  post: Returns word_dict, in format above.'''
  words = get_word_set(word_dict, sentences)
  maxi = get_max_id(word_dict)
  for word in words:		    #For each word not already in it, adds it to the dictionary with a unique id
    if word in word_dict:
      pass
    else:
      maxi += 1               #Prepares for the id
      word_dict[word] = maxi
  return word_dict


def get_max_id(word_dict):
  '''Returns the maximum value of the dictionary's value set.'''
  if word_dict == {}:
    return -1                               #So that next id is 0
  else:
    return sorted(word_dict.values())[-1]   #Sort the IDs, get the highest from off the end


def update_word_dict(task_dict):
  '''Creates a word dictionary such that {"word": wordID (int)} from the provided
  dictionary of tasks, {taskID:Task}. Adds to a dictionary in a "word_dict.txt" file
  or if none, from scratch.
  post: Returns the updated word_dict.'''
  word_dict = upload_word_dict()                                      #Gets word_dict from file if present
  sentences = get_list_of_all_sentences(task_dict)                    #Get list of all sentences from all tasks
  word_dict = __build_word_dict(word_dict, sentences)                 #Adds any new words
  return word_dict


def get_word_dict(task_dict, choice):
  '''Gets the appropriate word dictionary based on the provided choice.
  pre: task_dict is a dictionary of Tasks and choice is an int 0-1.
  post: Returns a dictionary such that {"word:wordID}'''
  if choice == 0:                                                         #If .train file...
    word_dict = update_word_dict(task_dict)                                 #Update word dictionary {"word:wordID}
  else:                                                                   #If .test file...
    word_dict = upload_word_dict()                                          #Get the word dictionary as already exists
  return word_dict


def output_word_dict(word_dict):
  '''Outputs word_dict to a file for reuse in other data gathering ventures.
  pre: word_dict is a dictionary such that "word":wordID
  post: Outputs a file "word_dict.txt" where the words are listed--> word:ID\tword:ID...
  WARNING: Overwrites any file by the same name.'''
  outFile = open("word_dict.txt","w")
  for item in word_dict.items():
    outFile.write(item[0]+">x<"+str(item[1])+"\t")
  outFile.close()
    

#---------------------------------Features-----------------------------------------

#------Term Frequency: Words & Punctuation------
def get_tf_dicts(sentence, word_dict):
  '''Takes in a sentence (string) and creates a term frequency and a
  punctuation frequency dictionary for it using the provided word
  dictionary.
  pre: sentence is a tokenized string.
  word_dict is a dictionary such that {"word": int}
  post: returns a tf dictionary and a pf dictionary of the forms {wordID:count_int}'''
  tf_dict, pf_dict = {}, {}
  for word in words(sentence):                          #For each word in the sentence
    if word in word_dict:                                 #If word is in the dictionary (.train = always, .test = not always)
      wordID = word_dict[word]                              #Get the word's ID
      if ispunct(word) and (wordID in pf_dict.keys()):      #If the punct has already appeared, add to it
        pf_dict[ wordID ] += 1
      elif ispunct(word):                                   #If the punct hasn't yet appeared, add as new key
        pf_dict[ wordID ] = 1
      elif wordID in tf_dict.keys():                        #If the word has already appeared, add to it
        tf_dict[ wordID ] += 1
      else:                                                 #If the word hasn't yet appeared, add as new key
        tf_dict[ wordID ] = 1
    else:                                                 #if word not in dictionary (.test, if it wasn't in training data)
      pass
  return (tf_dict, pf_dict)


def get_list_of_tf_dicts(sentences, word_dict):
  '''Takes in a list of sentences and the word dictionary and
  finds the term frequency dictionaries for each sentences and 
  returns that list.
  pre: sentences is list of strings, word_dict is a dictionary such
  that {"word":int}
  post: returns a list of tuples, each containing two dictionaries,
  (term_freq_dict, punct_freq_dict).'''
  ls = []
  for sentence in sentences:
    ls.append(get_tf_dicts(sentence, word_dict) )
  return ls


def associate_tasks_with_features(task_dict, word_dict):
  '''Creates a dictionary of the form:
     Task : [( {term freq}, {punct freq} ), ...]
  where each tuple is for Sentence #[index] in the Task. The inner dictionaries 
  are of the form {wordID:int}.
  pre: task_dict is a dictionary of all taskIDs associated with their Task object,
  word_dict is a dictionary such that {"word":wordID}
  post: returns a dictionary as described above.'''
  task_to_tf_dicts = {}
  for task in task_dict.values():
    task_to_tf_dicts[task] = get_list_of_tf_dicts(task.get_sentences_as_strings(), word_dict)
  return task_to_tf_dicts

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

#------Feature Options--------------------------
def match_choice_to_func(choice): #See commented ints below
  '''Choice in an int 0-2, representing which feature output to use.
  post: returns a function to create a line of output when given a feature tuple for
  a particular sentence.'''
  d = {0:tf_feature_string, 1:pf_feature_string, 2:tfpf_feature_string}
  return d[choice]


def tf_feature_string(f_tup): #0
  '''Takes in the tuple containing the features for the sentence. Uses this info to
  return a string for the LibSVM classifier using ONLY word frequencies.
  pre: f_tup is a tuple of dictionaries -> ({wordID:freq}, {punctID:freq})
  post: returns a string in the following form: "0:freq 1:freq ... n:freq"'''
  line = ''
  wordIDs = sort_wordIDs(f_tup[0])
  for wordID in wordIDs:
    line += " " + str(wordID) + ":" + str(f_tup[0][wordID])
  return line+"\n"


def pf_feature_string(f_tup): #1
  '''Takes in the tuple containing the features for the sentence. Uses this info to
  return a string for the LibSVM classifier using ONLY punctuation frequencies.
  pre: f_tup is a tuple of dictionaries -> ({wordID:freq}, {punctID:freq})
  post: returns a string in the following form: "0:freq 1:freq ... n:freq"'''
  line = ''
  wordIDs = sort_wordIDs(f_tup[1])
  for wordID in wordIDs:
    line += " " + str(wordID) + ":" + str(f_tup[1][wordID])
  return line+"\n"


def tfpf_feature_string(f_tup): #2
  '''Takes in the tuple containing the features for the sentence. Uses this info to
  return a string for the LibSVM classifier using BOTH word and punctuation 
  frequencies.
  pre: f_tup is a tuple of dictionaries -> ({wordID:freq}, {punctID:freq})
  post: returns a string in the following form: "0:freq 1:freq ... n:freq"'''
  line = ""
  wordIDs = sort_wordIDs(f_tup[0], f_tup[1])
  for wordID in wordIDs:
    if wordID in f_tup[1].keys():
      line += " " + str(wordID) + ":" + str(f_tup[1][wordID])
    else:
      line += " " + str(wordID) + ":" + str(f_tup[0][wordID])
  return line+"\n"

#------Output File Creation---------------------
def output_string(task_to_features, choice):
  '''Takes in a dictionary of tasks with their features, and a user provided choice 
  to indicate which features to use.
  pre: The dictionary is of the form {Task:[( {term freq}, {punct freq} ), ...]}, and
  choice is an int between 0 and 2.
  post: returns a string to output to a file.'''
  outstr = ""
  for task in task_to_features.keys():
    for sent in task.get_sentences():
      f_tup = task_to_features[task][sent.get_num()]    #This is ({term freq}, {punct freq})
      outstr += get_output_line(sent, choice, f_tup)
  return outstr


def get_output_line(sent, choice, f_tup):
  '''Given the Sentence object, the feature choice, and the feature tuple for that 
  Sentence, this function will return a string representing the output line for the
  Sentence. "0 34:3 56:1"...etc
  pre: task is a Task object, sent is a Sentence object, choice is an int 0-2.
  post: returns the line as a string'''
  line = str( categorize(mean(sent)) )              #"0" or "1" for specific or general
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
  outFile = open(f_name,"w")
  outFile.write(outstr)
  outFile.close()


#-----------------------------------MAIN-------------------------------------------
def main():
  file_type = user_file_type()                                            #Asks if .train or .test file
  task_dict = ask_user_for_tasks()                                        #Get dictionary of all tasks
  choice = user_feature_selection()                                       #Which set of features to use
  word_dict = get_word_dict(task_dict, file_type)                         #Word dictionary {"word:wordID}
  
  task_to_features = associate_tasks_with_features(task_dict, word_dict)  #Task : [( {term freq}, {punct freq} ), ...]
 
  output_word_dict(word_dict)
  write_output( output_string(task_to_features, choice) , make_fname(file_type))


main()


'''
Fixes:

deal with 'll and other punct + letters combos
see why it is missing one, regardless
'''
