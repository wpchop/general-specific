# Sentence Specificity Classifier
Repositiory for work on a classifier to distinguish between general and specific sentences.
Creates files to be read by the LibSVM classifier.

##Instructions

#####To create a training or test file for LibSVM:
1. Run classify.py
  * Creates the input file for LibSVM, either specific.train or specific.test
  * The data files for classify.py's prompts should be located in the data folder

#####To run statistical analysis on mTurk result files:
1. Run stats.py
  * Outputs three .txt files.
    * file\_amb_phrases.txt   - Each sentence listed with (<#times asked about>) next to segments that were questioned.
    * file_output-stats.txt   - Varied stastics output neatly.
    * file_scales.txt         - The mean scale for each sentence listed.

#####To add more documents for IDF calculation:
1. Run count.dict_builder.py
  * WARNING: Will permanently modify NYT/count.dict
