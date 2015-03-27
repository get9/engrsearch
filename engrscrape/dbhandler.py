import sqlite3

from scrapy.exceptions import DropItem
from contextlib import closing
from urlparse import urlsplit

# Adds an item to the database and its associated outlinks
def add_url_and_outlinks(curs, item):
    # Check if URL is already in the database via hashing
    check_hash = "SELECT * FROM urls WHERE hash = ?"
    curs.execute(check_hash, (item['xhash'],))
    if curs.fetchone():
        raise DropItem("{} already in database".format(item['url']))

    # Check if we have the http/https version in the db already. If so, don't add it
    check_http_vers = "SELECT * FROM urls WHERE url LIKE ?"
    url_without_scheme = '%' + ''.join(urlsplit(item['url'])[1:])
    curs.execute(check_http_vers, (url_without_scheme,))
    if curs.fetchone():
        raise DropItem("{} already in database".format(item['url']))

    else:
        add_url = "INSERT INTO urls VALUES (?, ?, ?)"
        # Need sqlite3.Binary() so that we can put the compressed data in the db
        curs.execute(add_url, (item['xhash'], item['url'], sqlite3.Binary(item['compressed_text'])))
        add_outlinks = "INSERT INTO linkgraph VALUES (?, ?)"
        inserts = [(item['xhash'], l) for l in item['outlinks']]

        # Check if there are any links to insert. There won't be in the case of
        # an endpoint page (i.e. pdf, image, etc)
        if inserts:
            curs.executemany(add_outlinks, inserts)
    print(item['url'])
    return item

# Creates the database
def create_db(conn):
    create_urls = """
        CREATE TABLE IF NOT EXISTS urls (
            hash TEXT PRIMARY KEY,
            url TEXT,
            data BLOB
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
