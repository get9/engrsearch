import sqlite3
from xxhash import xxh64

from scrapy import log
from scrapy.exceptions import DropItem
from twisted.enterprise import adbapi

from engrscrape.dbhandler import add_url_and_outlinks, create_db
from engrscrape.util import in_domains, fix_link

from urlparse import urlsplit

allowed_domains = [
    'engr.uky.edu',
    #'cs.uky.edu',
]

# Sets up the db initially (why this can't be done via script I have no idea...)
class InitializeDBPipeline(object):
    """ A pipeline for initializing the database. There's an error when trying
        to initialize from a .sql script with sqlite3. I have no idea why. """

    def __init__(self):
        self.conn = sqlite3.connect('./links.db')

    def open_spider(self, spider):
        create_db(self.conn)

# Drops any items that were populated from a redirected URL
class DropRedirectURLsPipeline(object):
    """ A pipeline for dropping any redirected URLs that got resolved by the
        downloader """

    def process_item(self, item, spider):
        if in_domains(item['url'], allowed_domains):
            return item
        else:
            raise DropItem("Disallowed {} in item pipeline from Downloader middleware resolving redirected URL".format(item['url']))

# Filters any duplicate links from the incoming stream
class SqlitePipeline(object):
    """ A pipeline for handling database operations with the SQLite database """

    def __init__(self):
        self.dbpool = adbapi.ConnectionPool('sqlite3', 'links.db', check_same_thread=False)

    def process_item(self, item, spider):
        item['url'] = item['url'].strip().rstrip('/')
        item['xhash'] = xxh64(item['url']).hexdigest()
        def handle_error(url):
            log.msg("Could not add {} to database".format(url), level=log.WARNING)

        query = self.dbpool.runInteraction(add_url_and_outlinks, item)
        query.addErrback(handle_error, item['url'])
        return item
