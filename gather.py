from ExternalDict import merge_dicts
from parse_turk_data import main as m
from parse_ani_data import main as am
  
#---------------------------- Data Collection ----------------------------------

def gather_data():
  '''Handles the collection of data from all files. Currently can gather from Ani's
  rated data and from mTurk result files.
  post: Returns a dictionary containing all data. Key value pairs can be as follows:
      "fname" : [(rating, "sentence"), ...]    <--Ani's data files
     "taskID" : Task                           <--mTurk result files'''
  c = {0:ask_user_for_tasks, 1:ask_user_for_ani_data}                              #If new data format, add something here
  data = {}
  while True:
    choice = user_infile_type()
    data = merge_dicts(c[choice](), data)
    cont = raw_input("Are there more data files to include? y/n : ")
    if 'y' not in cont.lower(): break
  return data


#------------Different Data File Inputs------------------------
def user_infile_type():
  '''Handles user input for the choice of data to parse. Returns an int representing
  the choice.
  0: mTurk result files
  1: Ani and Annie's annotated data from wsj/asp/nyt'''
  choice = -400
  while choice not in range(2):
    choice = int(raw_input('''\nWhich of the following data files would you like to input?
  0: mTurk result files
  1: Ani and Annie's annotated data from wsj/asp/nyt
Enter the appropriate integer: '''))
  return choice
  
#---------------Ani's Data Files ------------------------
def ask_user_for_ani_data():
  '''Handles user input for the collection of data from Ani and Annie's annotated
  data from newspapers.
  post: Returns a dictionary containing the data such that "fname":[(rating, "sentence")]'''
  data_dict = {}
  print ""
  while True:
    data_tup = am()                                                 #(fname, [tups])
    data_dict[data_tup[0]] = data_tup[1]                            #"fname":[(rating, "sentence")]
    cont = raw_input("Are there more 'Ani's data' files to include? y/n : ")
    if 'y' not in cont.lower(): break
  return data_dict

#---------------mTurk Result Files ------------------------
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
  more_tasks = m()[1]
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