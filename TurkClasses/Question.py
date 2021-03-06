#-------------------------------------------------------------------------------
# Name:        Question.py
# Purpose: A class to contain a question asked in an mTurk test.
#
# Authors:      Bridget O'Daniel, Wenli Zhao, Lily Wu
#
# Created:     21/05/2015
#-------------------------------------------------------------------------------

class Question:
  def __init__(self, num, workerID, low, high, body, context):		#question number, worker ID, ranges, question, in context?
    """Initializes a Question object containing the following:
    a question num (int), a workerID (string), a low and high (ints) that
    represent the range of words related to the question asked, the body (ie
    the question itself as a string), and in what context the answer may be
    found (string)."""
    self.num = num
    self.workerID = workerID
    self.low = low
    self.high = high
    self.body = body
    self.context = context

#-----------Get Methods--------------------
  def get_num(self):
    return self.num

  def get_ID(self):
    return self.workerID

  def get_text(self, sentence):		#sentence is a list
    """Uses the low and high to find the substring bound by that range in the
    given string, and returns that substring."""
    return " ".join(sentence[self.low:self.high+1])

  def get_body(self):
    return self.body

  def get_context(self):
    return self.context

  def get_low(self):
    return self.low

  def get_high(self):
    return self.high
