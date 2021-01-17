import logging

from loguru import logger
import pendulum
import scrapy

from slashdot_crawler.items import Article


class SlashdotSpider(scrapy.Spider):
    name = "slashdot"

    base_url = "http://slashdot.org/"

    # Scrapy will use these to start the parsing
    start_urls = [base_url]

    def __init__(self) -> None:
        super().__init__()

        # Somehow this needs to happen here, not at the top of the module
        # (it doesn't work)
        # See: https://stackoverflow.com/questions/33203620/how-to-turn-off-logging-in-scrapy-python
        logging.getLogger("scrapy").setLevel(logging.WARNING)
        logging.getLogger("protego").setLevel(logging.WARNING)

        self.current_page = 3468

    def parse(self, response):

        all_articles = response.css("div.main-content article")

        articles_in_page = 0

        if not all_articles:
            logger.info("No articles found on this page, stopping crawler")
            return

        for article in all_articles:

            title = article.css("h2.story span.story-title a[onclick]::text").get()

            url = article.css("h2.story a[onclick]::attr(href)").get()

            if url is None:
                logger.debug(f"Skipping article, None URL. Title was: {title}")
                continue

            url = "https:" + article.css("h2.story a[onclick]::attr(href)").get()

            date_posted = article.css(
                "header div.details span.story-byline time::text"
            ).get()

            if date_posted is None:
                logger.debug(f"Skipping article, None date. Title was: {title}")
                continue

            # Remove the "on" at the beginning and parse date to datetime
            # 'on Saturday January 16, 2021 @10:34AM'
            date_posted = date_posted.replace("on ", "")
            datetime = pendulum.from_format(date_posted, "dddd MMMM DD, YYYY @HH:mmA")

            content = article.css("div.body div.p").get()

            item = Article()
            item["title"] = title
            item["url"] = url
            item["content"] = content
            item["datetime"] = datetime

            articles_in_page += 1

            yield item

        logger.debug(f"Found {articles_in_page} on this page")

        self.current_page += 1
        next_page_url = self.base_url + "?page=" + str(self.current_page)
        logger.info(f"Next page URL: {next_page_url}")

        if next_page_url:
            yield response.follow(next_page_url, callback=self.parse)
        else:
            logger.info("Next page URL not found")
