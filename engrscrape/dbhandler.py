import sqlite3

from scrapy.exceptions import DropItem
from contextlib import closing

# Adds an item to the database and its associated outlinks
def add_url_and_outlinks(curs, item):
    check_url = "SELECT * FROM urls WHERE hash = ?"
    curs.execute(check_url, (item['xhash'],))
    if curs.fetchone():
        raise DropItem("{} already in database".format(item['url']))
    else:
        add_url = "INSERT INTO urls VALUES (?, ?)"
        curs.execute(add_url, (item['xhash'], item['url']))
        add_outlinks = "INSERT INTO linkgraph VALUES (?, ?)"
        inserts = [(item['xhash'], l) for l in item['outlinks']]

        # Check if there are any links to insert. There won't be in the case of
        # an endpoint page (i.e. pdf, image, etc)
        if inserts:
            curs.executemany(add_outlinks, inserts)
    return item

# Creates the database
def create_db(conn):
    create_urls = """
        CREATE TABLE IF NOT EXISTS urls (
            hash TEXT PRIMARY KEY,
            url TEXT
        )
        """
    create_linkgraph = """
        CREATE TABLE IF NOT EXISTS linkgraph (
            url TEXT,
            outlink TEXT,
            FOREIGN KEY(url) REFERENCES urls(hash),
            FOREIGN KEY(outlink) REFERENCES urls(hash),
            UNIQUE(url, outlink)
        )
        """
    with closing(conn.cursor()) as curs:
        curs.execute(create_urls)
        curs.execute(create_linkgraph)
