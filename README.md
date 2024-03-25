# Scrapy Yelp Spider

This Python script utilizes Scrapy to crawl Yelp for business information based on specified categories and locations.

## Overview

The Scrapy Yelp Spider is designed to scrape Yelp for business details such as name, rating, number of reviews, website, and select reviews. It allows users to specify a category and location, crawling through Yelp search results to gather information on businesses matching the criteria.

## Features

- **Customizable Search**: Specify the category and location to focus the search on specific businesses.
- **Scalable Crawling**: Utilizes Scrapy framework for efficient web crawling and scraping.
- **Output Options**: Outputs scraped data in JSON format for easy integration with various systems.

## Usage

1. **Install dependencies**: Ensure you have Python and Scrapy installed.
   ```bash
     pip install -r requirements.txt'
   ```
2. **Run the spider**: Execute the `main.py` script with appropriate arguments.
   ```bash
   python main.py 'output_file' '<category>' '<location>'

   python main.py 'result.json' 'contractors' 'San Francisco, CA'

```
