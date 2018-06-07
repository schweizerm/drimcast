from utils import webcrawler
from utils.image import Image
import scrapy
import re

page_counter = 1
image_list = []
image_callback = None


class DeepDreamSpider(scrapy.Spider):
    name = "deepdream"
    link = 'https://deepdreamgenerator.com/feed?page='

    def start_requests(self):
        global page_counter
        next_link_to_crawl = self.link + str(page_counter)
        print("Crawling new images from {}".format(next_link_to_crawl))
        yield scrapy.Request(next_link_to_crawl, self.parse)
        page_counter += 1

    def parse(self, response):
        on_website_crawled(response)
        pass


def crawl_images():
    webcrawler.crawl(DeepDreamSpider)


def on_website_crawled(response):
    global image_list
    decoded = response.body.decode('utf-8')
    # luckily re.findall is always in the same order
    links = re.findall(r'data-src="([^"]+)"', decoded)
    users = re.findall(r'\/u[^>]+>([^<]+)<\/a', decoded)
    print("Done crawling! Found {} new images. ".format(len(links)))
    for index, image in enumerate(links):
        image_list.append(Image(links[index], "image/jpeg", users[index]))

    get_next_image(image_callback)


def get_next_image(callback):
    global image_callback
    if image_callback is None:
        image_callback = callback
    if len(image_list) <= 1:
        crawl_images()
    else:
        image_callback(image_list.pop(0))
