#!/usr/bin/env python

import sys
import sqlite3
import numpy as np

from itertools import chain
from collections import defaultdict
from contextlib import closing
from search_util import normalize
from math import log

# Gets all terms from the document corpus
def get_all_terms(curs):
    get_terms = "SELECT DISTINCT word FROM inverted_index"
    curs.execute(get_terms)
    return list(chain.from_iterable(curs.fetchall()))

# Get term count for document
def get_doc_termcount(curs, dochash):
    get_count = "SELECT data FROM urls WHERE hash = ?"
    curs.execute(get_count, (dochash,))
    return len(zlib.decompress(curs.fetchone()[0]))

# Computes the TF vector for the given document and returns it as a
# numpy array of length |terms| in corpus
def get_tf_vec(curs, dochash, searchterms, allterms):
    d_t_pairs = [(dochash, q) for q in searchterms]
    get_term_count_pairs = "SELECT word, count(word) FROM inverted_index WHERE hash = ? AND word = ? ORDER BY word"
    curs.executemany(get_term_count_pairs, d_t_pairs)
    term_count = dict(curs.fetchall())

    # Fill missing portions of vector with 0's 
    tfvec = map(lambda w: 0 if w not in term_count else term_count[w], allterms)

    # Change to numpy array, scale by sum of terms in document
    return np.asarray(tfvec, dtype=float32) / get_doc_termcount(curs, dochash)

# Compute IDF vector and return as Numpy array
def get_idf_vec(curs, ndocs):
    get_idf = "SELECT COUNT(word) FROM inverted_index GROUP BY word"
    curs.execute(get_idf)
    idf = list(chain.from_iterable(curs.fetchall()))
    idf = map(lambda x: log((1 + ndocs) / x), idf)
    return np.asarray(idf, dtype=float32)

# Returns a list of all dochashes
def get_all_docs(curs):
    get_docs = "SELECT hash FROM urls ORDER BY hash"
    curs.execute(get_docs)
    return list(chain.from_iterable(curs.fetchall()))

# Returns the number of documents containing a given word
def get_num_docs_for_term(curs, term):
    get_num_docs = "SELECT COUNT(hash) FROM inverted_index WHERE word = ?"
    curs.execute(get_num_docs, (term,))
    return curs.fetchone()[0]

# Computes q TFIDF vector
def get_q_tf_vec(curs, searchterms, allterms):
    tfvec = np.zeros(allterms)
    for q in searchterms:
        tfvec[allterms.index(q)] = searchterms.count(q) / float(len(searchterms))
    return tfvec
    
# Returns a vector of the pageranks of all URLs (indexed by hash)
def get_pageranks(curs):
    get_ranks = "SELECT pagerank FROM urls ORDER BY hash"
    curs.execute(get_ranks)
    return list(chain.from_iterable(curs.fetchall()))

# Return url associated with hash
def get_url(curs, xhash):
    get_url = "SELECT url FROM urls WHERE hash = ?"
    curs.execute(get_url, (xhash,))
    return curs.fetchone()[0]

def main():
    if len(sys.argv) < 4:
        print("Usage:")
        print("    {} dbfile 'search query ...' nresults".format(sys.argv[0]))
        sys.exit(1)

    dbfile = sys.argv[1]
    searchterms = map(lambda w: normalize(w), sys.argv[2].split())
    N = int(sys.argv[3])

    # Database access
    conn = sqlite3.connect(dbfile)
    curs = conn.cursor()

    # Can calculate IDF vector just once (technically could cache this later on)
    alldocs = get_all_docs(curs)
    idfvec = get_idf_vec(curs, len(alldocs))

    # Calculate query TFIDF vector
    q_tfidf = get_q_tf_vec * idfvec

    # Compute TF vectors for documents
    tfidf_ranks = []
    allterms = get_all_terms(curs)
    for d in alldocs
        tfvec = get_tf_vec(curs, d, searchterms, allterms)
        doc_tfidf = tfvec * idfvec
        # Compute cosine between query and doc, put it in ranks
        tfidf_ranks.append(np.dot(q_tfidf, doc_tfidf) / (np.linalg.norm(q_tfidf) * np.linalg.norm(doc_tfidf)))

    # Compute final ranking of all documents for this query
    final_ranks = map(lambda x: x[0] * x[1], zip(get_pageranks(curs), tfidf_ranks))

    # Associate with hashes and sort
    hash_ranks = sorted(zip(alldocs, final_ranks), key=lambda x: x[1])
    
    # Return top N results
    for i in range(min(len(hash_ranks), N)):
        print(get_url(curs, hash_ranks[i]))

main()
