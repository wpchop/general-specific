#-------------------------------------------------------------------------------
# Name:        parse_data.py
# Purpose: Takes a .input file and a .results file from mTurk, extracts the data,
# and outputs it nicely.
# Authors:      Bridget O'Daniel, Wenli Zhao, Lily Wu
# Created:     21/05/2015
#-------------------------------------------------------------------------------
import os, sys
sys.path.insert( 0, sys.path[0]+'/TurkClasses' )                                #Allows script to reach TurkClasses folder
from ast import (literal_eval)
from Task import Task
from Question import Question
from Sentence import Sentence
from Worker import Worker

def parseMeta(string):	#separate into sentence number, (question number), field
    """Takes an entry of meta tags of the form "Answer.xxx" and extracts relevant
    information, storing it in a tuple.
    pre: string is a String of the form "Answer.sentxxx"
    post: Returns a tuple of one of the following forms:
        1) ()
        2) (sentence_num, 'field')
        3) (sentence_num, question_num, 'field')"""
    new_string = string[12::]   #Removes Answer.sent
    lst = new_string.split("_")
    sentnum = lst[0]                                  #Gets the sentence number
    if len(lst) == 3:                                 #If field is part of a quesetion...
      q = lst[1][1::]                                   #Get the question number (w/o the q)
      field = lst[2][0:len(lst[2])-1]                   #Get the field without the final quote
      return (sentnum, q, field)
    elif len(lst) == 2:                               #If field is part of a scale or qstat
      field = lst[1][0:len(lst[1])-1]                   #Get the field without the final quote
      return (sentnum, field)
    else:                                             #If field is submitbutton, empty tuple
      return ()

def deleteQuotes(string):
    """Takes an input string and removes the first and last characters.
    Presumably quotation marks, but it'll happily cut off other things too."""
    return string[1:len(string)-1]

def get_input_file_lines(fname):
    """Returns a list of the lines from the given input file name, leaving off
    the first line of the file."""
    inputFile = open("data/"+fname, "r")
    inputFile.readline()                            #Ignore first line of input file
    inputlines = inputFile.readlines()              #Read the rest of the lines!
    inputFile.close()
    return inputlines

def make_task_dict(input_lines):
    """Takes the lines from the input file and creates Tasks containing
    the proper Sentences from that information. Returns the Tasks as a dictionary,
    where the keys are the taskID's (strings) and the values are the Task objects."""
    tasks = {}                                      #Dictionary to store the {taskID:Task Object}
    for task_line in input_lines:                   #For each task in the input file...
        task_line = task_line.split("\t")               #Split string into parts
        taskID = task_line[0]                           #First part is the taskID!
        task = Task(taskID)                             #Make a Task object with the ID
        s_list = literal_eval(task_line[3])             #Get the list of sentences as a list!!
        s_list = [i.strip() for i in s_list]            #Clean up the sentences
        task = add_sentences_to_task(s_list, task)      #Add sentences to the task
        tasks[taskID]= task                             #Put the task in the task dictionary
    return tasks

def add_sentences_to_task(s_list, task):
    """Adds each sentence (string) in s_list to the given task (Task object),
    and returns the task."""
    for i, sent in enumerate(s_list):             #For each sentence...
        sentence = Sentence(i, sent)                    #Make a Sentence object for it
        task.add_sentence(sentence)                     #Add it to the Task's sentence list
    return task

def read_results_file(fname):
    """Opens the given file name and extracts the metadata and the lines that
    follow, containing each user's results.
    pre: fname--string that is a valid file name.
    post: Returns meta (a list of metadata strings) and result_lines (a list of
    lines in the file)"""
    inFile = open("data/"+fname, "r")
    meta = inFile.readline().strip().split()
    #taskID = meta[29]
    result_lines=inFile.readlines()
    inFile.close()
    return meta, result_lines

def make_category_dict(meta):
    """Takes in the list of metadata strings and parses them. Returns a dictionary
    wherein the keys are the order of the tags and the values are tuples that
    represent the metadata usefully. See parseMeta for details."""
    categories = {}
    for i in range(30, len(meta)):              #Skips irrelevant data at the start of the meta
        categories[i-30] = parseMeta(meta[i])   #Creates the tuples and puts 'em in there
    return categories

def __add_questions(l, currenttask, categories, worker):
    """Function for actually categorizing questions and adding them. Returns the
    changed Task."""
    low, high, body, context = 0,0,"",""              #Initialize variables for the loop
    workerID = worker.get_ID()
    for i in range(30, len(l)):                       #For all data by the worker....
        entry = categories[i-30]                            #Get relevant category information (what sentence/question/field this info is)
        if l[i] == "":                                      #If the info is empty, skip it.
          pass
        elif len(entry) == 2:                               #If the worker did NOT ask a question...
          if entry[1] == "scale":                               #If the info is a scale
            currenttask.sentences[int(entry[0])].add_scale((l[i], workerID))	#On the current task, add scale to corresponding sentence
            worker.add_scale((l[i],entry[0]))
          else:                                                 #If the info is a qstat
            currenttask.sentences[int(entry[0])].add_qstat(l[i])    #Add it to the proper question
        elif len(entry)== 3:                                #If the worker DID ask a question...
          if entry[2] == "low":                                 #Add the field into the proper variable for later Question making
            low = int(l[i])
          elif entry[2] == "high":
            high = int(l[i])
          elif entry[2] == "body":
            body = l[i]
          else:                                                                     #If we're on context, that means it's the end of a question
            context = l[i]
            question = Question(int(entry[1]), workerID, low, high, body, context)  #Put all current info from variables into a Question object
            currenttask.get_sentence(int(entry[0])).add_question(question)          #Now add that question to the proper sentence in the task (phew)
    return currenttask

def add_questions_to_sentences(resultlines, categories, tasks):
    """Adds the Questions to the Sentences in the Tasks (phew), reading the worker's
    data from resultlines (a list of lines from the result file) and using the
    dictionary categories to put the Questions in the correct places.
    pre: resultlines is a list of lines from the result file, categories is a
    hash table based on metadata strings.
    post: Returns the task dictionary."""
    workers = []
    for rline in resultlines:                                                   #For each worker's data...
      l = rline.split("\t")                                                         #Make it a list of data
      workerID = l[19]                                                              #Retrieve workerID
      l = map(deleteQuotes,l)                                                       #Delete all the unnecessary quotes
      worker = Worker(workerID, l[29])
      workers.append(worker)
      currentTask = tasks[ l[29] ]                                                  #Find the Task that the worker is working on (taskID @l[29])
      #print currentTask.get_ID()
      currentTask = __add_questions(l, currentTask, categories, worker)           #Add the questions where they should go
      #currentTask.add_worker(worker)
    #print len(currentTask.get_workers())
    for worker in workers:
      taskID = worker.get_taskID()
      task = tasks[taskID]
      if task.get_ID()==taskID:
      	task.add_worker(worker)
    #print len(
    return tasks

def write_output(input_fname, tasks):
    """Creates an output file by the name of "<file>_output.txt" using the hash of
    Task objects.
    WARNING: Will overwrite another file of the same name."""
    outFile = open(input_fname[0:-6]+"_output.txt","w")
    context_map = {0: "No", 1: "Vague", 2: "Some", 3: "Immediate"}
    for key in tasks:
      outFile.write("\n==================TASK==================\n"+key+"\n\n")
      task = tasks[key]
      for sentence in task.get_sentences():
        outFile.write("\n---SENTENCE "+str(sentence.get_num()) + "---\n"+sentence.get_sent()+"\n")

        for question in sentence.get_questions():
          outFile.write("\t---Question #"+str(question.get_num())+" "+question.get_ID()+"\n")
          outFile.write("\tTXT\t"+question.get_text(sentence.get_sent().split())+"\n")
          outFile.write("\tBODY\t"+question.get_body()+"\n")
          outFile.write("\tIN CONTEXT\t"+context_map[int(question.get_context()[0:1])]+"\n")
        outFile.write("--Specificity scale: ")
        for scale in sentence.get_scales():
          outFile.write(str(scale))
        outFile.write("\n\n")
    outFile.close()

def read_input_file():
    '''Uses a text file "input.txt" that lists all desired input files. The mTurk
    files should be listed on one line in the following format:
    mturk:\t<file>\t<file> 
    where <file> is the name of BOTH the .input and .results file, listed here 
    without the extension, ex: week3
    Returns the list of tuples where each tuple is of the form 
    ("file.input", "file.results")'''
    fname_list = []
    with open('data/input.txt', 'r') as inFile:
      for line in inFile:
        if line[:5] == 'mturk':
          items = line.strip().split('\t')[1:]
          for item in items:
            fname_list.append( (item+'.input', item+'.results') )
    return fname_list


def main(input_fname, result_fname):
    '''Takes in two strings representing the .input file and the .results file,
    respectively. Returns a dictionary of tasks.'''
    input_lines = get_input_file_lines(input_fname)                             #Get lines from .input file
    tasks = make_task_dict(input_lines)                                         #Make a dictionary containing the Tasks with Sentences in them
    meta, resultlines = read_results_file(result_fname)                         #Get the list of metadata and the lines from the .result file
    categories = make_category_dict(meta)                                       #A category dictionary parsed from the metadata
    tasks = add_questions_to_sentences(resultlines, categories, tasks)          #Add Questions to the proper Sentences
    #write_output('output/'+input_fname,tasks)                                                         #Output to an output file "output.txt"
    return tasks

#for tup in read_input_file():
#  main( tup[0], tup[1] )
