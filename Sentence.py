#-------------------------------------------------------------------------------
# Name:        Sentence.py
# Purpose: A class to contain a sentence in an mTurk test.
#
# Authors:      Bridget O'Daniel, Wenli Zhao, Lily Wu
#
# Created:     21/05/2015
#-------------------------------------------------------------------------------

class Sentence: 	#sentence, all questions, all scales
  def __init__(self, num, sent):
    """Initialized a Sentence object with an id number (num) and a sentence (as
    represented as a string). Created with empty lists to store questions, scales,
    and qstats."""
    self.num = num
    self.sent = sent
    self.questions = []
    self.scales = []
    self.qstats = []

#-----------Add Methods--------------------
  def add_scale(self, scale):
    self.scales.append(scale)

  def add_question(self, question):
    self.questions.append(question)

  def add_qstat(self, qstat):
    self.qstats.append(qstat)

#-----------Get Methods--------------------
  def get_num(self):
    return self.num

  def get_scales(self):
    return self.scales

  def get_questions(self):
    return self.questions

  def get_qstats(self):
    return self.qstats

  def get_sent(self):
    return self.sent
    
  def get_word(self, index):
    return self.sent.split()[index]

#-----------Other Methods--------------------
  def split_sentence(self):
    """Splits the sentence into a list of words and returns it."""
    return self.sent.split()
