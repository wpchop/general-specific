from stats import *
import scipy
import numpy
import matplotlib.pyplot as pl

for task in tasks:
  means = []
  devs = []
  for item in meanandDevs:
    means.append(item[1])
    devs.append(item[2])

  n = len(means)
  fig, ax = pl.subplots()
  index = numpy.arange(n)
  bar_width = 0.7
  error_config = {'ecolor': '0.000003'}
  
  rects = pl.bar(index, means, bar_width, alpha = 0.4, color='g', yerr=devs, error_kw=error_config)
  
  pl.xlabel("Sentence")
  pl.ylabel("Mean Ratings")
  pl.title("yayyy")
  pl.xticks(index+bar_width, [i for i in range(len(task.get_sentences()))])
  pl.show()

#----------------------Plotting Frequencies of Keywords--------------------------------

  n = len(task.get_sentences())
  
  fig, ax = pl.subplots()
  index = numpy.arange(n)
  bar_width = 0.3
  error_config = {'ecolor': '0.000003'}
  
  rects = pl.bar(index, means, bar_width, alpha = 0.4, color='g', yerr=devs, error_kw=error_config)
  
  pl.xlabel("Sentence")
  pl.ylabel("Mean Ratings")
  pl.title("yayyy")
  pl.xticks(index+bar_width, [i for i in range(len(task.get_sentences()))])
  pl.show()

