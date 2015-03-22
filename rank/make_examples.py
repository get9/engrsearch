#!/usr/bin/env python2

import pickle

example1 = {
    'Page A': {
        'out': ['Page B', 'Page C'],
    },
    'Page B': {
        'out': ['Page C'],
    },
    'Page C': {
        'out': ['Page A'],
    },
    'Page D': {
        'out': ['Page C'],
    },
}

example2 = {
    'Home': {
        'out': ['About', 'Product', 'Links'],
    },
    'About': {
        'out': ['Home'],
    },
    'Product': {
        'out': ['Home'],
    },
    'Links': {
        'out': ['Home', 'External Site A', 'External Site B', 'External Site C', 'External Site D'],
    },
    'External Site A': {
        'out': [],
    },
    'External Site B': {
        'out': [],
    },
    'External Site C': {
        'out': [],
    },
    'External Site D': {
        'out': [],
    },
}

example3 = {
    'Home': {
        'out': ['About', 'Product', 'Links'],
    },
    'About': {
        'out': ['Home'],
    },
    'Product': {
        'out': ['Home'],
    },
    'Links': {
        'out': ['Home', 'External Site A', 'External Site B', 'External Site C', 'External Site D', 'Review A', 'Review B', 'Review C', 'Review D'],
    },
    'External Site A': {
        'out': [],
    },
    'External Site B': {
        'out': [],
    },
    'External Site C': {
        'out': [],
    },
    'External Site D': {
        'out': [],
    },
    'Review A': {
        'out': ['Home']
    },
    'Review B': {
        'out': ['Home']
    },
    'Review C': {
        'out': ['Home']
    },
    'Review D': {
        'out': ['Home']
    },
}

with open('example1.graph', 'w') as f:
    pickle.dump(example1, f)
with open('example2.graph', 'w') as f:
    pickle.dump(example2, f)
with open('example3.graph', 'w') as f:
    pickle.dump(example3, f)
