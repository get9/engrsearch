#!/usr/bin/env python2

# Need a couple of matrices/parameters for the computation:
#
#     H hyperlink matrix
#         Each position (i, j) has the value (1 / #outlinks) if there a link
#         between page_i and page_j
#
#     A termination page matrix
#         Each column corresponding to a termination node in the link graph
#         has value (1 / N), where N is the total number of pages in the graph
#
#     S matrix product of H and A
#         Easier to compute this together than separately
#
#     alpha probability of choosing which matrix to pick next link from
#         Lies in range [0, 1]
#
#     N number of pages in graph

import sys
import sqlite3
import numpy as np

from collections import defaultdict
from contextlib import closing

# Compute S = H + A matrix
# hashes looks like:
# {
#     'hash' => 1,
#     'hash' => 2,
# }
# serving as a cache of the indices of each hash for the matrix
def compute_s(hashes, outlinks):
    # Base matrix for S
    N = len(hashes.keys())
    S = np.zeros((N, N), dtype=float)

    # Fill the S matrix
    for h in sorted(hashes.keys()):
        # Termination links. This computes A matrix
        if h not in outlinks:
            S[:, hashes[h]] = 1.0 / N

        # This part computes H matrix
        else:
            for o in outlinks[h]:
                S[hashes[o], hashes[h]] = 1.0 / len(outlinks[h])

    # Return S = HA matrix
    return S

# Compute constant matrix for random jumps to other pages
def compute_one(N):
    return np.full((N, N), 1.0 / N, dtype=float)

# Compute Google matrix G
def compute_g(alpha, S, one):
    return (alpha * S) + ((1 - alpha) * one)

# Get PageRank of all pages by running power method
def run_power_method(G, N, iters):
    # Initialization of I array
    I = np.full((N, 1), (1.0 / N), dtype=float)
    diff = 1.0
    i = 0
    for i in range(iters):
        oldI = I
        I = np.dot(G, I)
        diff = np.linalg.norm(I - oldI)

    # Return PageRanks of all pages
    print("num iters: {}".format(iters))
    print("diff = {}".format(diff))
    return I

# Make a list of pairs of URLs and their associated PageRanks
def make_hash_pr_tuples(hashes, pageranks):
    return zip(pageranks.flatten().tolist(), sorted(hashes.keys()))

# Import data from db
def from_db(dbfile):
    # Structures to return; list of hashes
    outlinks = defaultdict(set)
    # outlinks looks like:
    #
    #     {
    #         page1: (outlink, ...),
    #         page2: (outlink, ...),
    #         ...
    #     }
    #
    # where all values are hashes in the dictionary

    # Connect to database and execute queries
    conn = sqlite3.connect(dbfile)
    # Note: this will return all hashes sorted, so we don't need to call
    # sorted() everywhere
    get_hashes = "SELECT hash FROM urls ORDER BY hash"
    get_outlinks = "SELECT url, outlink FROM linkgraph"
    with conn:
        curs = conn.cursor()
        curs.execute(get_hashes)
        hashes = sorted([l[0] for l in curs.fetchall()])
        hashes = dict(zip(hashes, range(len(hashes))))
        curs.execute(get_outlinks)
        for t in curs.fetchall():
            outlinks[t[0]].add(t[1])
        # Include extra filter to make sure there are no links that aren't in
        # hashes
        for t in outlinks:
            outlinks[t] = sorted(filter(lambda h: h in hashes, outlinks[t]))
        return hashes, outlinks

# Get URL associated with hash
def hash2url(xhash, dbfile):
    get_url = "SELECT url FROM urls WHERE hash = ?"
    with sqlite3.connect(dbfile) as conn:
        curs = conn.cursor()
        curs.execute(get_url, (xhash,))
        return curs.fetchone()[0]

# Add pageranks to database
def add_ranks_to_db(dbfile, tuples):
    add_ranks = "UPDATE urls SET pagerank = ? WHERE hash = ?"
    with sqlite3.connect(dbfile) as conn:
        with closing(conn.cursor()) as curs:
            curs.executemany(add_ranks, tuples)

# Scale PageRanks based on number of entries
def scale_ranks(tuples, N):
    return map(lambda p: (p[0], p[1] * N), tuples)

# main function
if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage:")
        print("    {} db alpha nresults".format(sys.argv[0]))
        sys.exit(1)

    dbfile = sys.argv[1]
    hashes, outlinks = from_db(dbfile)

    # Scalars
    alpha = float(sys.argv[2])
    print("alpha = {}".format(alpha))
    N = len(hashes)
    print("N = {}".format(N))

    # Matrices
    print("Computing 1")
    one = compute_one(N)
    print("Computing S")
    S = compute_s(hashes, outlinks)
    print("Computing G")
    G = compute_g(alpha, S, one)

    # Compute PageRanks via power method of 100 iterations
    print("Computing I")
    pageranks = run_power_method(G, N, 100)

    # Get tuples of (hash, pr) tuples and add them to database
    pr_h_tuples = make_hash_pr_tuples(hashes, pageranks)
    #h_pr_tuples = scale_ranks(h_pr_tuples, N)
    add_ranks_to_db(dbfile, pr_h_tuples)

    # Print out top 10 ranked pages
    for i in sorted(pr_h_tuples, key=lambda x: x[0], reverse=True)[:int(sys.argv[3])]:
        print("{:<50}\t{}".format(hash2url(i[1], dbfile), i[0]))
