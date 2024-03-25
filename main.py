import re
import sys
from urllib.parse import unquote_plus
from urllib.parse import urlencode

import scrapy
from scrapy.crawler import CrawlerProcess


class YelpSpiderClass(scrapy.Spider):
    BASE_URL = 'https://www.yelp.com'
    name = 'yelp_spider'
    allowed_domains = ['yelp.com']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = kwargs.get('category')
        self.location = kwargs.get('location')
        self.limit_pages = 1

    def start_requests(self):
        params = {'find_desc': self.category, 'find_loc': self.location}
        url = f'{self.BASE_URL}/search?{urlencode(params)}'

        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        businesses = self.extract_businesses(response)

        for business in businesses:
            name, rating, num_reviews, yelp_url = self.extract_business_info(business, response)
            yield scrapy.Request(
                yelp_url, callback=self.parse_business_page,
                meta={'name': name, 'rating': rating, 'num_reviews': num_reviews, 'yelp_url': yelp_url}
            )

        if self.should_continue_to_next_page(response):
            next_page_url = self.extract_next_page_url(response)
            yield scrapy.Request(next_page_url, callback=self.parse)

    @staticmethod
    def extract_businesses(response):
        return response.xpath('//div[contains(@class, "toggle__09f24__fZMQ4")]')

    @staticmethod
    def extract_business_info(business, response):
        name = business.xpath('.//a[contains(@class, "css-19v1rkv")]/text()').get()
        rating = business.xpath('.//span[contains(@class, "css-gutk1c")]/text()').get()

        reviews_str = business.xpath('.//span[contains(@class, "css-chan6m")]/text()').get()
        reviews_match = re.search(r'(\d+)', reviews_str)
        num_reviews = reviews_match.group(1) if reviews_match else 0

        yelp_url = business.css('a.css-1jrzyc::attr(href)').get()
        return name, rating, num_reviews, response.urljoin(yelp_url)

    def should_continue_to_next_page(self, response):
        return response.css('a.next-link::attr(href)').get() and self.limit_pages > 1

    @staticmethod
    def extract_next_page_url(response):
        return response.urljoin(response.css('a.next-link::attr(href)').get())

    def parse_business_page(self, response):
        name, rating, num_reviews, yelp_url = self.extract_metadata(response)
        website = self.extract_website(response)
        item = {'name': name, 'rating': rating, 'num_reviews': num_reviews, 'yelp_url': yelp_url, 'website': website,
                'reviews': self.extract_reviews(response)}
        yield item

    @staticmethod
    def extract_metadata(response):
        name = response.meta.get('name')
        rating = response.meta.get('rating')
        num_reviews = response.meta.get('num_reviews')
        yelp_url = response.meta.get('yelp_url')
        return name, rating, num_reviews, yelp_url

    @staticmethod
    def extract_website(response):
        website_href = response.xpath(
            './/p[contains(@class, "css-1p9ibgf")]//a[contains(@class, "css-1idmmu3")]/@href').get()
        decoded_url = unquote_plus(website_href) if website_href else ""

        website = ""
        if decoded_url:
            domain_match = re.search(r'https?://([^/?&]+)', decoded_url)  # Extract the domain
            website = domain_match.group(1).split("&")[0] if domain_match else ""
        return website

    @staticmethod
    def extract_reviews(response):
        review_block = response.xpath('.//div[@id="reviews"]//li[contains(@class, "css-1q2nwpv")]')
        reviews = []
        for review in review_block[:5]:
            reviewer_name = review.xpath('.//a[contains(@class, "css-19v1rkv")]/text()').get()
            reviewer_location = review.xpath('.//span[contains(@class, "css-qgunke")]/text()').get()
            review_date = review.xpath('.//span[contains(@class, "css-chan6m")]/text()').get()

            review_item = {
                'reviewer_name': reviewer_name,
                'reviewer_location': reviewer_location,
                'review_date': review_date
            }
            reviews.append(review_item)
        return reviews

    @classmethod
    def run_yelp_spider(cls, output_file, category, location):
        process = CrawlerProcess(settings={
            'FEEDS': {
                output_file: {'format': 'json', 'overwrite': True},
            },
        })
        process.crawl(cls, category=category, location=location)
        process.start()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python main.py 'output_file' '<category>' '<location>'")
        sys.exit(1)
    YelpSpiderClass.run_yelp_spider(*sys.argv[1:])
