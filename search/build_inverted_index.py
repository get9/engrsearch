#!/usr/bin/env python

import sqlite3
import zlib
import sys

from collections import defaultdict
from contextlib import closing
from nltk.stem import PorterStemmer

# List of common english stopwords from "http://www.ranks.nl/stopwords"
STOP_WORDS = [
"a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
"any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
"below", "between", "both", "but", "by", "can't", "cannot", "could", "couldn't",
"did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
"each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
"have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
"here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
"i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
"its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no",
"nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our",
"ours", "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd",
"she'll", "she's", "should", "shouldn't", "so", "some", "such", "than", "that",
"that's", "the", "their", "theirs", "them", "themselves", "then", "there",
"there's", "these", "they", "they'd", "they'll", "they're", "they've", "this",
"those", "through", "to", "too", "under", "until", "up", "very", "was",
"wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
"what's", "when", "when's", "where", "where's", "which", "while", "who",
"who's", "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you",
"you'd", "you'll", "you're", "you've", "your", "yours", "yourself",
"yourselves"
]

# Gets the text data from the database. Returns list of pairs:
# (docID, compressed_data)
def get_text_data(curs):
    get_pairs = "SELECT hash, data FROM urls";
    curs.execute(get_pairs)
    return [(h, d) for h, d in curs.fetchall()]

# Creates the table to store the inverted index in the database
def create_inverted_index_table(curs):
    create_table = """
        CREATE TABLE IF NOT EXISTS inverted_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT,
            hash TEXT,
            UNIQUE(word, hash)
        )
    """
    curs.execute(create_table)

def uncompress(data):
    return zlib.decompress(data)

def normalize(word):
    return word.strip().lower()

# Actually creates the inverted index in memory
def create_inverted_index(pairs):
    # Use defaultdict with set to make initial empty collection a set if there
    # is no key in the dict
    inverted_index = defaultdict(set)
    for docid, text in pairs:
        split_text = map(lambda w: normalize(w), text.split())
        for w in filter(lambda w: w not in STOP_WORDS, split_text):
            inverted_index[w].add(docid)
    return inverted_index

# Add all pairs of (word, docID) to the db
def add_inverted_index_to_db(curs, index):
    # Need to decode to utf-8 to insert into sqlite correctly...
    pairs = [(w.decode('utf-8'), d) for w, docs in index.iteritems() for d in docs]
    add_pair = "INSERT INTO inverted_index (word, hash) VALUES (?, ?)"
    curs.executemany(add_pair, pairs)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("    {} dbfile".format(sys.argv[0]))
        sys.exit(1)

    dbfile = sys.argv[1]
    with sqlite3.connect(dbfile) as conn:
        with closing(conn.cursor()) as curs:
            print("Getting compressed text data")
            pairs = get_text_data(curs)

            # Uncompress each data element of the pair
            print("Uncompressing data")
            pairs = map(lambda p: (p[0], uncompress(p[1])), pairs)

            # Create inverted index and a place to store it in db
            create_inverted_index_table(curs)
            print("Creating inverted index")
            inverted_index = create_inverted_index(pairs)
            print("Adding inverted_index to {}".format(dbfile))
            add_inverted_index_to_db(curs, inverted_index)

main() 
