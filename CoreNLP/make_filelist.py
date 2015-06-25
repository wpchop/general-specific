import os
path = "/nlp/users/odanielb/nyt_idf/texts"
with open("input/filelist.txt", "w") as outFile:
  for file in os.listdir(path):
    outFile.write(path+'/'+file+'\n')