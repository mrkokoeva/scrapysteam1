import scrapy
from spider_steam.items import SpiderSteamItem
import re

class SteamproductspiderSpider(scrapy.Spider):
    name = 'SteamProductSpider'
    allowed_domains = ['store.steampowered.com']
    start_urls = ['http://store.steampowered.com/']

    queries = ["инди", "новелла", "board game"]

    def start_requests(self):  # придется переписать start_requests - функция, которая работает с GET-запросами
        osn_url = "https://store.steampowered.com/search/?term="
        for query in self.queries:
            link = osn_url + query + "&page="
            for page in range(1, 10):
                link_1 = link + str(page)
                yield scrapy.Request(url=link_1, callback=self.search)

    def search(self, response):
        x_path = '//*[@id="search_resultsRows"]/a'
        chunks = response.xpath(x_path)
        for chunk in chunks:
            link = chunk.xpath('./@href').get()
            price = chunk.xpath('.//div[@class="col search_price  responsive_secondrow"]/text()').get()
            if price is not None:
                price = re.sub('[\r\t\n ]', '', price)
            else:
                price = chunk.xpath('.//strike/text()').get()
                price = re.sub('[\r\t\n ]', '', price)
            if 'app' not in link:
                continue
            COOKIES = {
                'birthtime' : '470682001',
                'lastagecheckage' : '1-0-1985'
            }
            yield scrapy.Request(url=link, callback=self.parse, cookies=COOKIES, meta={'price' : price})


    def parse(self, response):
        item = SpiderSteamItem()
        name = response.xpath('//*[@id="appHubAppName"]/text()').get()
        item['name'] = name
        item['price'] = response.meta['price']
        developer_name = response.xpath('//*[@id="appHeaderGridContainer"]/div[2]/a/text()').get()
        item['developer_name'] = developer_name
        category = response.xpath('//*[@id="tabletGrid"]/div[1]/div[2]/div[1]/div[1]//text()').extract()
        category = " / ".join(category[:-2])
        category = re.sub('[\t\r\n]', '', category)
        item["category"] = category
        reviews = response.xpath('//*[@id="userReviews"]/div/div[2]//text()').extract()
        reviews = ''.join(reviews)
        reviews = re.sub('[\t\r\n]', '', reviews)
        item['review'] = reviews
        release_date = response.xpath('//*[@id="game_highlights"]/div[1]/div/div[3]/div[2]/div[2]/text()').get()
        item['release_date'] = release_date
        tags = response.xpath('//*[@id="glanceCtnResponsiveRight"]/div[2]/div[2]//text()').extract()
        tags = '/'.join(tags)
        tags = re.sub('[\t\r\n]', '', tags)
        item['tags'] = tags
        platforms = response.xpath('//*[contains(@id, "game_area_purchase_section")]/div[1]/span/@class').extract()
        platforms = '/'.join(platforms)
        platforms = re.sub('platform_img', '', platforms)
        item['platforms'] = platforms
        return item