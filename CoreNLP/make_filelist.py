import os

# Example paths:
#   to unstructured PubMed abstracts: "/nlp/users/odanielb/pubmed_idf/texts"
#   to NYT data: "/nlp/users/odanielb/nyt_idf/texts"

path = raw_input("Enter the path to the directory containing the files to list:\n")
outfile = raw_input("Enter the desired name for the output list (extension included):\n")

with open(outfile, "w") as outFile:
  for file in os.listdir(path):
    outFile.write(path+'/'+file+'\n')