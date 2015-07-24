#-------------------------------------------------------------------------------
# Name:        parse_ani_data.py
# Purpose: Parses the information in data files from http://homepages.inf.ed.ac.uk/alouis/genspec.html
#          Import main into your file and run it to receive the data in the form
#          (fname, [(rating, sentence),...]).
# Authors: Bridget O'Daniel, Wenli Zhao, Lily Wu
# Created: 10/06/2015
# Acknowledgements:
#-------------------------------------------------------------------------------


def get_input_lines(fname):
  '''Returns a list of the lines from the given input file name, leaving off
  the first line of the file.'''
  inputFile = open("data/"+fname, "r")
  inputlines = inputFile.readlines()              #reads lines
  inputFile.close()
  return inputlines
    
def get_fname():
  '''Handles user input for the selection of the input file.
  Returns the file name.'''
  return raw_input("Enter the 'Ani's data' file name: ")
  
  
def convert_rating(rating):
  '''Converts a rating of 'gen'/'spec' or '1'/'-1' to 1/0, respectively. Returns the int.'''
  return {'gen':1, 'spec':0, '1':1, '-1':0}[rating]
  
  
def parse_line(line):
  '''Parses the provided line to return a tuple such that (rating, sentence), where
  rating is either 0 or 1 and sentence is a string'''
  line = line.split('\t')
  sent = str(line[3])[1:-1]                   #Gets the sentence and removes quotes
  rating = convert_rating(line[7])            #Use 4 for classifier's choice, 7 for annotators' choice
  return (rating, sent)
  
  
def parse_lines(lines):
  '''Parses the provided list of lines and returns a list of tuples such that
  (rating, sentence), where rating is either 0 or 1 and sentence is a string.'''
  return map(parse_line, lines)
  

def main(fname):
  '''Handles everything. Returns (fname, [(rating, sentence),...]) where fname is 
  the file's name, rating is an int and sentence is a string.'''
  lines = get_input_lines(fname)                  #Get input lines
  lst_tups = parse_lines(lines)                   #For each line get the tuple (rating, sentence)
  return (fname, lst_tups)                        #Return tuple (fname, [tups])
