from gather import ask_user_for_tasks as get_tasks
from random import *
task_dict = get_tasks()

master_list = []
grouped = []
for task in task_dict:
  for sentence in task_dict[task].get_sentences():
    master_list.append(sentence.get_sent())
shuffle(master_list)

for i in range(0, len(master_list), 5):
  if i <= len(master_list) - 5:
    five = []
    for j in range(i, i+5):
      five.append(master_list[j])
    grouped.append(five)
    
outfile = open("grouped_sentences.txt", "w")
for group in grouped:
  for sentence in group:
    outfile.write(sentence + "\t")
  outfile.write("\n")
