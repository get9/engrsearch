import re

from engrscrape.items import URLItem
from engrscrape.util import gethash, in_domains, fix_link

from scrapy import Request, log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.utils.url import canonicalize_url

from urlparse import urljoin, urlsplit

TAGS_TO_EXTRACT = ['p']

# Main spider class
class EngrSpider(CrawlSpider):
    name = 'engrspider'
    start_urls = [
        'http://www.engr.uky.edu/',
        #'http://cs.uky.edu/',
        #'http://cs.uky.edu/~jurek/advising/important_resources.sphp'
    ]

    good_domains = [
        'engr.uky.edu',
        #'cs.uky.edu',
    ]

    # Default callback for parsing response from fetch
    #def parse_link(self, response):
    def parse(self, response):
        # Get a bunch of these errors on endpoint pages; just make outlinks
        # empty if we do.
        links = []
        if hasattr(response, 'xpath') and callable(getattr(response, 'xpath')):
            links = response.xpath('//a/@href').extract()

        # Extract text from TAGS_TO_EXTRACT in the response
        text = ""
        for tag in TAGS_TO_EXTRACT:
            for e in response.xpath('//{}'.format(tag))

        # Make every URL absolute and canonical so we can index, fetch, and hash
        # appropriately
        links = map(lambda l: fix_link(l, response.url), links)

        # Filter non-domain URLs from the list of outlinks.
        links = filter(lambda x: in_domains(x, self.good_domains), links)

        # Filter out $engr/events/category/alumni/...
        links = filter(lambda x: not re.search(r'\/events\/category\/alumni\/\d+-\d*', x), links)

        # Construct item
        item = URLItem()
        item['url'] = response.url
        item['xhash'] = gethash(response.url)
        item['outlinks'] = set(gethash(l) for l in links)
        yield item
        for l in links:
            yield(Request(l))
