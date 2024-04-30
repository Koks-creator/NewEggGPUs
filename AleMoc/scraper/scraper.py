from dataclasses import dataclass
from random import choice
import re
import os
from datetime import datetime
from itertools import groupby
from collections import defaultdict
import logging
from time import perf_counter
from typing import Union, List, Tuple
import requests
from requests_html import HTML, AsyncHTMLSession
import asyncio
from bs4 import BeautifulSoup
import json
from tqdm.asyncio import tqdm

from AleMoc.config import Config
from AleMoc.TurboLogger import CustomLogger

FIELDS = Config.FIELDS
REVIEW_FIELDS = Config.REVIEW_FIELDS
SCRAPE_ELEMENTS = Config.SCRAPE_ELEMENTS


@dataclass
class NewEggScraper:
    proxy: Union[str, bool] = f"{Config.PROJECT_MAIN_PATH}/scraper/proxy.txt"
    user_agents: Union[str, bool] = f"{Config.PROJECT_MAIN_PATH}/scraper/userAgents.txt"
    per_page: str = "60"
    log_level: int = logging.DEBUG
    _category_id: str = "100007709"
    _base_url: str = f"https://www.newegg.com/p/pl"

    def __post_init__(self) -> None:
        self.scraper_logger = CustomLogger(logger_name="Scraper", log_file_name=f"{Config.PROJECT_MAIN_PATH}/{Config.LOGS_FOLDER}/scraperLogs.txt",
                                           logger_log_level=self.log_level).create_logger()
        if self.proxy:
            with open(self.proxy) as proxy_f:
                self.proxy_list = proxy_f.read().split("\n")

        if self.user_agents:
            with open(self.user_agents) as user_agents_f:
                self.user_agents_list = user_agents_f.read().split("\n")

        self.scraper_logger.debug("Initializing with parameters:\n"
                                  f"-Proxy: {self.proxy} \n"
                                  f"-UserAgents: {self.user_agents} \n"
                                  f"-PerPage: {self.per_page} \n"
                                  )

    def get_random_user_agent(self) -> Union[dict, None]:
        user_agent = choice(self.user_agents_list)
        return {"User-Agent": user_agent} if self.user_agents else None

    def get_random_proxy(self) -> Union[dict, None]:
        proxy_line = choice(self.proxy_list)
        ip, port, login, password = proxy_line.split(":")

        if self.proxy:
            return {
                "http": f"http://{login}:{password}@{port}:{port}"
            }
        return None

    def get_urls(self,  phrase: str, execution_id: str, max_pages: int = 0) -> dict:

        link = f"{self._base_url}?SrchInDesc={phrase}&N={self._category_id}&PageSize={self.per_page}"
        self.scraper_logger.info(f"{link=}")
        self.scraper_logger.debug(f"{link=}")
        response = requests.get(link, proxies=self.get_random_proxy(), headers=self.get_random_user_agent())
        html = HTML(html=response.text)

        pagination_links = []
        links = defaultdict(dict)
        allowed_pages = list(range(1, max_pages+1))

        self.scraper_logger.info(f"[Execution id: {execution_id}] Getting pagination")
        for link in html.links:
            if "&page=" in link:
                page_num = int(link.split("&page=")[1])
                if max_pages and len(pagination_links)+1 > max_pages:
                    break

                if page_num in allowed_pages or not max_pages:
                    self.scraper_logger.debug(f"[Execution id: {execution_id}] Link: {link}")
                    pagination_links.append(link)

        self.scraper_logger.info(f"[Execution id: {execution_id}] Getting products")
        for p_num, p_link in enumerate(pagination_links):
            self.scraper_logger.info(f"[Execution id: {execution_id}] Pages checked: {p_num+1}/{len(pagination_links)}")
            self.scraper_logger.debug(f"[Execution id: {execution_id}] Product link: {p_link}")

            response = requests.get(p_link, proxies=self.get_random_proxy(), headers=self.get_random_user_agent())
            html = HTML(html=response.text)
            links[f"page{p_num}"] = {
                "pageUrl": p_link,
                "productLinks": list(set([link for link in html.links if "/p/" in link and "#" not in link
                                 and "&page=" not in link if "?N=" not in link]))
            }

        return links

    async def scrape(self, session: AsyncHTMLSession, links: list, page_num: str, i: int, execution_id: str) \
            -> Tuple[List[dict], List[dict]]:
        scraped_products = []
        scraped_reviews = []
        progress_bar = tqdm(total=len(links), desc=f"[Execution id: {execution_id}] Processing page {page_num} (this bar xdd)",
                            leave=True, position=0)
        await asyncio.sleep(i)
        for link in links:
            await asyncio.sleep(1)  # don't touch
            with await session.get(link, headers=self.get_random_user_agent(),
                                   proxies=self.get_random_proxy()) as response:
                if response.status_code == 200:
                    product_specs = defaultdict(dict)
                    soup = BeautifulSoup(response.content, "html.parser")

                    details = soup.find(SCRAPE_ELEMENTS["Details"]["Tag"], SCRAPE_ELEMENTS["Details"]["Attr"])
                    spec_tables = details.find_all_next(SCRAPE_ELEMENTS["SpecTables"]["Tag"],
                                                        SCRAPE_ELEMENTS["SpecTables"]["Attr"])

                    product_title = soup.find(SCRAPE_ELEMENTS["ProductTitle"]["Tag"],
                                              SCRAPE_ELEMENTS["ProductTitle"]["Attr"]).text.strip()

                    price = soup.find(SCRAPE_ELEMENTS["Price"]["Tag"],
                                      SCRAPE_ELEMENTS["Price"]["Attr"]).text.replace("$", "").strip()
                    currency = "$"
                    product_id = link.split("/p/")[1]

                    # Create specs with nulls only
                    product_specs[product_id]["ProductTitle"] = product_title
                    product_specs[product_id]["Url"] = link
                    product_specs[product_id]["Price"] = price
                    product_specs[product_id]["Currency"] = currency
                    for field_name, fields in FIELDS.items():
                        for f in fields:
                            product_specs[product_id][f.replace(" ", "").replace("-", "")] = None

                    for table in spec_tables:
                        caption = table.find_next(SCRAPE_ELEMENTS["Caption"]["Tag"]).text
                        if caption in FIELDS.keys():
                            tbody = table.find_next(SCRAPE_ELEMENTS["Tbody"]["Tag"])
                            trs = tbody.find_all(SCRAPE_ELEMENTS["Trs"]["Tag"])
                            for tr in trs:
                                spec_name = tr.find(SCRAPE_ELEMENTS["SpecName"]["Tag"]).text.strip()
                                if spec_name in FIELDS[caption]:
                                    spec_val = tr.find(SCRAPE_ELEMENTS["SpecVal"]["Tag"]).text
                                    product_specs[product_id][spec_name.replace(" ", "").replace("-", "")] = spec_val
                    scraped_products.append(product_specs)

                    pattern = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.DOTALL)

                    # Find all matches
                    reviews = {}
                    matches = pattern.findall(str(soup))
                    for match in matches:
                        if "reviewCount" in match:
                            reviews = json.loads(match)

                    if "review" in reviews.keys():
                        product_reviews = defaultdict(list)
                        for review in reviews["review"]:
                            review_data = defaultdict(dict)
                            for db_field, json_field in REVIEW_FIELDS.items():
                                splitted = json_field.split("_")
                                if len(splitted) > 1:
                                    review_data[db_field] = review[splitted[0]][splitted[1]]
                                else:
                                    review_data[db_field] = review[json_field]
                            product_reviews[product_id].append(review_data)
                        scraped_reviews.append(product_reviews)
                else:
                    self.scraper_logger.info(
                        f"[Execution id: {execution_id}] Wrong status code: {response.status_code}, url: {link}")

                progress_bar.update(1)
        return scraped_products, scraped_reviews

    async def init_tasks(self, links: dict, execution_id: str) -> asyncio.gather:

        tasks = []
        session = AsyncHTMLSession()
        for ind, item in enumerate(links.items()):
            pag_link, prod_links = item[1]["pageUrl"], item[1]["productLinks"]
            tasks.append(self.scrape(session, prod_links, item[0], ind+1, execution_id))

        return await asyncio.gather(*tasks)

    def run(self, links: dict, execution_id: str) -> Tuple[List, List]:
        products = []
        reviews = []

        self.scraper_logger.info(f"[Execution id: {execution_id}] Starting")
        start = perf_counter()

        res = asyncio.run(self.init_tasks(links, execution_id))
        for r in res:
            products.extend(r[0])
            reviews.extend(r[1])
        self.scraper_logger.info(f"[Execution id: {execution_id}] Scraping took: {round(perf_counter() - start, 2)}s")

        self.scraper_logger.debug(f"[Execution id: {execution_id}] {products=}")
        self.scraper_logger.debug(f"[Execution id: {execution_id}] {reviews=}")

        # return list(itertools.chain(*products)), list(itertools.chain(*reviews))
        key_func = lambda d: next(iter(d))
        products = [next(group) for key, group in groupby(sorted(products, key=key_func), key=key_func)]
        reviews = [next(group) for key, group in groupby(sorted(reviews, key=key_func), key=key_func)]
        return products, reviews

    @staticmethod
    def save2json(filename: str, data: list) -> None:
        with open(filename, "w") as json_f:
            json.dump(data, json_f, indent=4)

    def start_scraping(self, phrase: str, max_pages: int = 0, execution_id: str = "0", save: bool = True) -> Tuple[List[dict], List[dict], str]:
        links = self.get_urls(max_pages=max_pages, phrase=phrase, execution_id=execution_id)
        # print(links)
        prods, reviews = self.run(links, execution_id)

        full_folder = ""
        if save:
            time_now = datetime.now().strftime('%d%m%Y_%H%M%S%f')[:-3]
            main_folder = rf"{Config.PROJECT_MAIN_PATH}/{Config.SINK_FOLDER}/"
            folder_name = f"data_{execution_id}_{time_now}"
            full_folder = f"{main_folder}{folder_name}"
            os.mkdir(full_folder)
            self.save2json(f"{full_folder}/Products_{execution_id}_{time_now}.json", prods)
            self.save2json(f"{full_folder}/Reviews_{execution_id}_{time_now}.json", reviews)
        return prods, reviews, full_folder


if __name__ == '__main__':
    sc = NewEggScraper(log_level=logging.INFO)
    sc.start_scraping(phrase="rtx+3060", max_pages=0)
