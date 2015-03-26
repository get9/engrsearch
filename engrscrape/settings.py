# -*- coding: utf-8 -*-

# Scrapy settings for engrscrape project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'engrscrape'

SPIDER_MODULES = ['engrscrape.spiders']
NEWSPIDER_MODULE = 'engrscrape.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'engrscrape (+http://www.engr.uky.edu)'

# Respect robots.txt
ROBOTSTXT_OBEY = True

# Pipeline and order
ITEM_PIPELINES = {
    'engrscrape.pipelines.InitializeDBPipeline': 200,
    'engrscrape.pipelines.DropRedirectURLsPipeline': 300,
    'engrscrape.pipelines.SqlitePipeline': 500,
}

# Increase number of concurrent requests
CONCURRENT_REQUESTS = 32

# Decrease download timeout to something reasonable - pdf's take awhile
DOWNLOAD_TIMEOUT = 10

# Set log file
LOG_FILE = 'engrspider.log'

# Set max number of retries to 1 (if we didn't get it before, we probably won't
# get it on the second time around
RETRY_TIMES = 1
