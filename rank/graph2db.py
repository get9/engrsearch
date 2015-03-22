#!/usr/bin/env python2

from __future__ import print_function
from xxhash import xxh64

import sys
import pickle
import sqlite3

# Hashing function used in previous crawl
def gethash(x):
    return xxh64(x).hexdigest()

# Creates DB tables
def create_db(dbfile):
    conn = sqlite3.connect(dbfile)
    with conn:
        curs = conn.cursor()
        create_urls = """
            CREATE TABLE IF NOT EXISTS urls (
                hash TEXT PRIMARY KEY,
                url TEXT
            );
        """
        create_linkgraph = """
            CREATE TABLE IF NOT EXISTS linkgraph (
                url TEXT,
                outlink TEXT,
                FOREIGN KEY(url) REFERENCES urls(hash),
                FOREIGN KEY(outlink) REFERENCES urls(hash),
                UNIQUE(url, outlink)
            );
        """
        curs.execute(create_urls)
        curs.execute(create_linkgraph)

# Load graph in via pickle
def read_graph(filename):
    with open(filename, 'r') as f:
        try:
            graph = pickle.load(f)
        except:
            print("[error]: couldn't unpickle {}".format(filename), file=sys.stderr)
        return graph

# Need two lists of tuples:
#     - [(url, hash(url)]
#     - [(hash(url), hash(url))]
# Graph hash looks like this:
#     {
#         'url': {
#             'in': set([url, ...]),
#             'out': set([url, ...]),
#         }
#         ...
#     }
# where 'in' value is the set of inlinks
def construct_tuple_lists(graph):
    urls = []
    linkgraph = []
    for k, v in graph.iteritems():
        # Construct tuple for 'urls' table (hash, url)
        urls.append((gethash(k), k))
        
        # Parse outlinks and construct a hash for them (page, outlink)
        linkgraph.extend([(gethash(k), gethash(u)) for u in v['out']]) 

    return [urls, linkgraph]

# Puts tuples from each list into the db
# Note: Assumes db already exists
def lists2db(dbfile, urls, linkgraph):
    conn = sqlite3.connect(dbfile)
    with conn:
        curs = conn.cursor()
        insert_urls = "INSERT INTO urls VALUES (?, ?)"
        insert_linkgraph = "INSERT INTO linkgraph VALUES (?, ?)"
        curs.executemany(insert_urls, urls)
        curs.executemany(insert_linkgraph, linkgraph)

if __name__ == "__main__":
    _, graphname, dbname = sys.argv
    create_db(dbname)
    g = read_graph(graphname)
    urls, linkgraph = construct_tuple_lists(g)
    lists2db(dbname, urls, linkgraph)
