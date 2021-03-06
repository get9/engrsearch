#!/usr/bin/env python

import sys
import sqlite3

from itertools import chain, combinations
from collections import defaultdict
from contextlib import closing
from search_util import normalize

# Returns the power set of a given search query
# Augmented to remove the empty set as the first item in the powerset
# From: "https://docs.python.org/2/library/itertools.html#recipes"
def powerset(searchterms):
    s = list(searchterms)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1))

# Gets the documents associated with each term as a set (to support fast
# intersection operations of document sets)
def get_docs_for_term(curs, term):
    get_docs = "SELECT hash FROM inverted_index WHERE word = ?"
    curs.execute(get_docs, (term,))
    return set(chain.from_iterable(curs.fetchall()))

# Returns a dictionary of the pageranks of all URLs (indexed by hash)
def get_pageranks(curs):
    get_ranks = "SELECT hash, pagerank FROM urls"
    curs.execute(get_ranks)
    return dict(curs.fetchall())

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

    # Get the documents corresponding to this search term
    docsforterm = dict()
    for term in searchterms:
        docsforterm[term] = get_docs_for_term(curs, term)

    # Need to compute intersection of all documents from the powerset of terms.
    # Do this by going through each group in the powerset, 
    docgroups = defaultdict(list)
    for combination in reversed(list(powerset(searchterms))):
        # Get the documents that contain each term in each term group
        docs = map(lambda t: docsforterm[t], combination)

        # Gets the intersection of returned documents for combination
        docgroups[len(combination)].extend(list(docs[0].intersection(*docs)))

    # Sort each set in list based on PageRank
    pageranks = get_pageranks(curs)
    for k in docgroups:
        docgroups[k] = sorted(docgroups[k], key=lambda d: pageranks[d])

    # Merge dict of lists into one giant list of documents
    sortedlist = []
    for k in reversed(docgroups.keys()):
        sortedlist.extend(docgroups[k])

    # Filter any empty elements out from the list
    sortedlist = filter(None, sortedlist)

    # Return top N results
    for i in range(min(len(sortedlist), N)):
        print(get_url(curs, sortedlist[i]))

main()
