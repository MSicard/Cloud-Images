
from nltk.stem import PorterStemmer 

def stem(word):
    stemmer = PorterStemmer()
    return stemmer.stem(word)