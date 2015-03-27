import re

from nltk.stem import PorterStemmer

# Normalize each word by removing punctuation, stemming, lowercase, etc
def normalize(word):
    word = unicode(word, 'utf-8')
    # Make everything lower-case
    word = word.lower()

    # Remove any punctuation and space characters
    word = re.sub(r'[\W\s]+', '', word, re.UNICODE)

    # Stem each word
    word = PorterStemmer().stem(word)

    return word
