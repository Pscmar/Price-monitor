#!/usr/bin/env python3
# coding=utf-8
import json
import logging
import re
import time
from json import decoder
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options

class Crawler(object):

    def __init__(self, proxy=None):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--ignore-ssl-errors')
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        if proxy:
            proxy_address = proxy['https']
            chrome_options.add_argument('--proxy-server=%s' % proxy_address)
            logging.info('Chrome using proxy: %s', proxy['https'])
        # 设置等待策略为不等待完全加载
        # chrome_options.add_experimental_option('pageLoadStrategy', 'none')
        # caps = DesiredCapabilities().CHROME
        # caps["pageLoadStrategy"] = "none"
        self.chrome = webdriver.Chrome(options=chrome_options) #, desired_capabilities=caps
        # jd sometimes load google pic takes much time
        self.chrome.set_page_load_timeout(30)
        # set timeout for script
        self.chrome.set_script_timeout(30)

    def close(self):
        self.chrome.quit()

    def get_jd_item(self, item_id):
        item_info_dict = {"name": None, "price": None, "plus_price": None, "subtitle": None}
        url = 'https://item.jd.com/' + item_id + '.html'
        try:
            self.chrome.get(url)
            logging.info('Crawl: {}'.format(url))
            # 共60秒
            retry = 30
            while retry:
                try:
                    element = self.chrome.find_element("xpath","//*[@class='p-price']/span[2]").text
                    if element:
                        logging.info("爬取价格数据")
                        logging.info('Found price element: {}'.format(element))
                        break
                    else:
                        logging.info("价格元素出现，价格未出现重试2秒")
                        time.sleep(2)
                        retry -= 1
                except NoSuchElementException:
                    logging.info("价格元素未出现")
                    time.sleep(2)
                    retry -= 1
        except TimeoutException as e:
            logging.warning('Crawl failure: {}'.format(e.msg))
            return item_info_dict

        # 提取商品名称
        try:
            name = self.chrome.find_element("xpath","//*[@class='sku-name']").text
            item_info_dict['name'] = name
        except AttributeError as e:
            logging.warning('Crawl name failure: {}'.format(e))
        except NoSuchElementException:
            try:
                # 加油卡(如200117841739）需要改为提取name
                name = self.chrome.find_element("xpath","//*[@class='name']").text
                item_info_dict['name'] = name
            except NoSuchElementException as e:
                logging.warning('Crawl name failure: {}'.format(e.msg))

        # 提取商品价格
        try:
            price = self.chrome.find_element("xpath","//*[@class='p-price']").text
            if price:
                price_xpath = re.findall(r'-?\d+\.?\d*e?-?\d*?', price)
                if price_xpath:  # 若能提取到值
                    item_info_dict['price'] = price_xpath[0]  # 提取浮点数
        except AttributeError as e:
            logging.warning('Crawl price failure: {}'.format(e.msg))
        except NoSuchElementException as e:
            logging.warning('Crawl price failure: {}'.format(e.msg))
            return item_info_dict

        logging.info('Crawl SUCCESS: {}'.format(item_info_dict))
        return item_info_dict


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s | %(levelname)s | %(filename)s %(lineno)s | %(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.INFO)
    start = time.time()

    c = Crawler()
    # c = Crawler({'http': '125.105.32.168:7305', 'https': '171.211.32.79:2456'})

    logging.debug(c.get_jd_item('100023130207'))

    c.close()

    end = time.time()
    print("执行时间:", end - start, 's')
