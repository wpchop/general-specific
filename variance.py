#-------------------------------------------------------------------------------
# Name:        variance.py
# Purpose: Takes in mTurk files and outputs a file "score-variance.txt" that 
#          lists the variance between scores for each Sentence in the task.
# Output:  Each line in the output will be of the form, tab separated: 
#         <TaskID> <Sentence#> <Std. Dev> <#q's: No> <#Immediate> <#Some> <#Vague>
# Authors: Bridget O'Daniel, Wenli Zhao, Lily Wu
# Created: 10/06/2015
# Acknowledgements: Aaron Hall for merge_dicts: http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression
#-------------------------------------------------------------------------------
import numpy as np
from gather import ask_user_for_tasks as gather

def is_number(s):
  try:
    float(s)
    return True
  except ValueError:
    return False


def stdDev(sentence):
  '''Given a Sentence object, returns the standard deviation of its scores (float).'''
  scores = [int(item[0]) for item in sentence.get_scales() if is_number(item[0])]
  return np.std(scores)


def get_context_counts(sentence):
  '''Given a Sentence, returns a list of ints containing its Questions' number 
  of each kind of context label, such that [#No, #Immediate, #Some, #Vague]'''
  contexts = [ q.get_context()[0] for q in sentence.get_questions() ]
  counts = [0]*4
  for context in contexts:
    counts[int(context)] += 1
  return counts

def analyze_task(task):
  '''Given a Task, returns a list of tuples each representing a sentence and 
  containg the following information: 
  (taskID, sentence#, score_std, #No, #Immediate, #Some, #Vague)'''
  taskID = task.get_ID()
  lst = []
  for sent in task.get_sentences():
    num = sent.get_num()
    std = stdDev(sent)
    contexts = get_context_counts(sent)
    lst.append( (taskID, num, std, contexts[0], contexts[1], contexts[2], contexts[3]) )
  return lst
  
def analyze_all(tasks):
  '''Given a dictionary of all Tasks such that taskID:Task, returns a list of tuples
  each representing a sentence and containing the following information:
  (taskID, sentence#, score_std, #No, #Immediate, #Some, #Vague)'''
  info_tups = []
  for task in tasks.values():
    info_tups.extend( analyze_task(task) )
  return info_tups
    
def output(tups):
  '''Outputs the list of tuples to a file "score-variance.txt" with each line
  containing the tuple, its elements separated by tabs.
  WARNING: Will overwrite a file of the same name.'''
  outFile = open('score-variance.txt',"w")
  for tup in tups:
    string = ''
    for item in tup:
      string += str(item)+'\t'
    outFile.write(string+'\n')
  print 'score-variance.txt written.'
  outFile.close()
  
def main():
  tasks = gather()      #Task dictionary of taskID:Task object
  tups = analyze_all(tasks)
  output(tups)
    
main()