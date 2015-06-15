# Sentence Specificity Classifier
Repositiory for work on a classifier to distinguish between general and specific sentences.
Creates files to be read by the LibSVM classifier.

Instructions

To create a training or test file for LibSVM:

1. Run count.dict_builder.py
  - Creates the file count.dict for idf calculations.
2. Run classify.py
  - Creates the input file for LibSVM, either specific.train or specific.test
