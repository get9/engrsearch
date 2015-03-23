from scrapy.item import Item, Field

# The basic item that'll be scraped. All we need to store is URLs.
class URLItem(Item):
    url = Field()
    xhash = Field()
    outlinks = Field()
    compressed_data = Field()

    # Override this so the item doesn't get printed in the log
    def __repr__(self):
        return ""
