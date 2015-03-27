#!/usr/bin/env python

import sqlite3
import zlib
import sys

from collections import defaultdict
from contextlib import closing
from nltk.corpus import stopwords
from search_util import normalize

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

# Actually creates the inverted index in memory
def create_inverted_index(pairs):
    # Use defaultdict with set to make initial empty collection a set if there
    # is no key in the dict
    inverted_index = defaultdict(set)
    for docid, text in pairs:
        split_text = map(lambda w: normalize(w), text.split())
        # Filter out stopwords
        split_text = filter(lambda w: w not in stopwords.words('english'), split_text)
        # Filter out any empty words
        split_text = filter(None, split_text)
        for w in split_text:
            inverted_index[w].add(docid)
    return inverted_index

# Add all pairs of (word, docID) to the db
def add_inverted_index_to_db(curs, index):
    # Need to decode to utf-8 to insert into sqlite correctly...
    pairs = [(w, d) for w, docs in index.iteritems() for d in docs]
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
