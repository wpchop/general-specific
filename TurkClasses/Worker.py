class Worker:
  def __init__(self, workerID, taskID):
    self.workerID = workerID
    self.taskID = taskID
    self.scales = []		#(scale, sentence number) (string, string)
  def add_scale(self,scale):
    self.scales.append(scale)
  def get_ID(self):
    return self.workerID
  def get_scales(self):
    return self.scales
  def get_taskID(self):
    return self.taskID
