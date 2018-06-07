from scrapy.crawler import CrawlerProcess
from twisted.internet.error import ReactorAlreadyRunning
process = CrawlerProcess()


def crawl(spider):
    process.crawl(spider)
    try:
        process.start()
    except ReactorAlreadyRunning:
        pass
