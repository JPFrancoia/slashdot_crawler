import logging

from loguru import logger
import pendulum
import scrapy

from slashdot_crawler.items import Article


class SlashdotSpider(scrapy.Spider):
    name = "slashdot"

    # Scrapy will use these to start the parsing
    start_urls = ["http://slashdot.org/"]

    def __init__(self) -> None:
        super().__init__()

        # Somehow this needs to happen here, not at the top of the module
        # (it doesn't work)
        # See: https://stackoverflow.com/questions/33203620/how-to-turn-off-logging-in-scrapy-python
        logging.getLogger("scrapy").setLevel(logging.WARNING)
        logging.getLogger("protego").setLevel(logging.WARNING)
        self.cur_page = 2

    def parse(self, response):

        all_articles = response.css("article")

        for article in all_articles:
            try:
                slashdot_id = int(article.css("article::attr(data-fhid)").get())
            except Exception as e:
                logger.debug(f"Skipping article, couldn't get id: {e}")
                continue

            title = article.css("h2.story span.story-title a[onclick]::text").get()

            url = "https:" + article.css("h2.story a[onclick]::attr(href)").get()

            date_posted = article.css("header div.details span.story-byline time::text").get()

            if date_posted is None:
                logger.debug(f"Skipping article. Title was: {title}")
                continue

            # Remove the "on" at the beginning and parse date to datetime
            # 'on Saturday January 16, 2021 @10:34AM'
            date_posted = date_posted.replace("on ", "")
            datetime = pendulum.from_format(date_posted, "dddd MMMM DD, YYYY @HH:mmA")

            content = article.css("div.body div.p").get()

            item = Article()
            item["slashdot_id"] = slashdot_id
            item["title"] = title
            item["url"] = url
            item["content"] = content
            item["datetime"] = datetime

            logger.debug(item)

            yield item

        next_page_url = "https:" + response.css("a.prevnextbutact::attr(href)").get()

        logger.info(f"Next page URL: {next_page_url}")

        if next_page_url is not None and self.cur_page <= 2:
            yield response.follow(next_page_url, callback=self.parse)
