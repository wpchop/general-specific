#-------------------------------------------------------------------------------
# Name:        Task.py
# Purpose: A class to manage an mTurk task.
#
# Authors:      Bridget O'Daniel, Wenli Zhao, Lily Wu
#
# Created:     21/05/2015
#-------------------------------------------------------------------------------

class Task:
    def __init__(self, taskID):
        self.taskID = taskID
        self.sentences = []
        self.workers = []

    def __str__(self):
        return "Task "+self.taskID

    def get_ID(self):
        return self.taskID

    def get_sentences(self):
        return self.sentences

    def get_sentences_as_strings(self):
        ls = []
        for sentence in self.sentences:
          ls.append(sentence.get_sent())
        return ls

    def get_sentence(self, index):
        """Gets the sentence at a particular index in the Task's list of sentences."""
        return self.sentences[index]

    def get_workers(self):
        return self.workers

    def add_worker(self, worker):
        self.workers.append(worker)

    def add_sentence(self, sentence):
        self.sentences.append(sentence)
