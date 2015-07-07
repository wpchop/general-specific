from ExternalDict import merge_dicts
from parse_turk_data import main as m
from parse_ani_data import main as am
from parse_turk_data import read_input_file as readm
  
#---------------------------- Data Collection ----------------------------------

def gather_data():
  '''Handles the collection of data from all files. Currently can gather from Ani's
  rated data and from mTurk result files.
  post: Returns a dictionary containing all data. Key value pairs can be as follows:
      "fname" : [(rating, "sentence"), ...]    <--Ani's data files
     "taskID" : Task                           <--mTurk result files'''
  files = read_input_file()
  mturk_files = [item for item in files if (not is_string(item))]
  ani_files = filter(is_string, files)
  return merge_dicts( collect_tasks(mturk_files), collect_ani_data(ani_files) )


#------------Different Data File Inputs------------------------
def is_string(item):
  '''Returns True if the given item is a string, False otherwise.'''
  return True if type(item) is str else False

def read_input_file():
    '''Uses a text file "input.txt" that lists all desired input files. 
    * The mTurk files should be listed on one line in the following format:
        mturk:\t<file>\t<file> 
      * where <file> is the name of BOTH the .input and .results file, listed here 
        without the extension, ex: week3
    * The Ani data files should be as follows:
        ani:\tnyt.txt\twsj.txt
    Returns the list of tuples and strings, where each tuple is of the form 
    ("file.input", "file.results")'''
    fname_list = []
    with open('data/input.txt', 'r') as inFile:
      for line in inFile:
        items = line.strip().split('\t')[1:]
        if line[:5] == 'mturk':
          for item in items:
            fname_list.append( (item+'.input', item+'.results') )
        if line[:3] == 'ani':
          for item in items:
            fname_list.append( item )
    return fname_list
  
#---------------Ani's Data Files ------------------------
def collect_ani_data(ani_files):
  '''Takes in a list of strings representing filenames.
  post: Returns a dictionary containing the data such that "fname":[(rating, "sentence")]'''
  data_dict = {}
  for string in ani_files:
    data_tup = am(string)                                           #(fname, [tups])
    data_dict[data_tup[0]] = data_tup[1]                            #"fname":[(rating, "sentence")]
  return data_dict

#---------------mTurk Result Files ------------------------
def collect_tasks(mturk_files=[]):
  '''Takes in a list of tuples such that (file.input, file.results). If not
  provided, uses an empty list and tries to read from file again.
  post: Returns a dictionary containing all tasks collected.'''
  task_dict = {}
  if mturk_files != []:
    for tup in mturk_files:
      task_dict = add_tasks(tup, task_dict)
      
  else:
    fname_list = readm()
    if fname_list != []:
      for tup in fname_list:
        task_dict = add_tasks(tup, task_dict)
        
  return task_dict

def add_tasks(tup, task_dict):
  '''Adds tasks from an mTurk output to the provided dictionary.
  pre: tup is a tuple such that (file.input, file.results), task_dict is a 
  dictionary of tasks.
  post: Returns a new dictionary with the tasks from the files.'''
  more_tasks = m(tup[0], tup[1])
  new_dict = merge_dicts(task_dict, more_tasks)
  return new_dict

#---------------------------- Feature Selection --------------------------------

def user_feature_selection():
  '''Handles user input for selecting which features to analyze. Returns the choice
  as an int.
  0: Punctuation count
  1: Term frequency only
  2: Tf-idf only
  3: All possible features'''
  choice = 5
  while choice not in range(4):
    choice = int(raw_input('''\nWhich feature(s) would you like to look at?:
  0: Punctuation count
  1: Term frequency only
  2: Tf-idf only
  3: All possible features
Enter the appropriate integer: '''))
  return choice


#--------------------------- File Type Selection -------------------------------
def user_outfile_type():
  '''Asks user if they are creating a .train file or a .test file. Returns 0 if 
  .train and 1 if .test.'''
  choice = -1
  while choice not in range(2):
    choice = int(raw_input('''\nWhich of the following would you like to create?
  0: A .train file to train a LibSVM model.
  1: A .test file to test a LibSVM model's prediction.
Enter the appropriate integer: '''))
  return choice


#-----------------------------------MAIN----------------------------------------

def main():
  file_type = user_outfile_type()                                         #Asks if .train or .test file
  data_dict = gather_data()                                               #Get dictionary of ALL DATA  
  feature_choice = user_feature_selection()                               #Which set of features to use
  return (file_type, feature_choice, data_dict)