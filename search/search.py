#!/usr/bin/env python

import sys
import sqlite3

from itertools import chain, combinations
from collections import defaultdict
from contextlib import closing

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

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("    {} dbfile 'search query ...'".format(sys.argv[0]))
        sys.exit(1)

    dbfile = sys.argv[1]
    searchterms = sys.argv[2].split()

    # Get the documents corresponding to this search term
    docsforterm = dict()
    with sqlite3.connect(dbfile) as conn:
        with closing(conn.cursor()) as curs:
            for term in searchterms:
                docsforterm[term] = get_docs_for_term(curs, term)

    # Need to compute intersection of all documents from the powerset of terms.
    # Do this by going through each group in the powerset, 
    docgroups = list()
    for combination in reversed(list(powerset(searchterms))):
        # Get the documents that contain each term in each term group
        docgroups = map(lambda t: docsforterm[t], combination)

        # Gets the intersection of returned documents for combination
        docgroups.append(combination[0].intersection(*combination))

    # Since intersections of many things will probably return no docs, remove
    # empty elements
    docgroups = filter(None, docgroups)

    print(map(lambda x: len(x), docgroups))

main()
