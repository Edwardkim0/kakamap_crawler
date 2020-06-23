from multiprocessing import freeze_support
from time import sleep

import selenium.webdriver as webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from itertools import cycle
import pandas as pd
import os
from datetime import datetime


def save_dataframe(search_name, df):
    now = datetime.now()
    save_dir = 'data'
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, now.strftime("%Y-%m-%d_%H_%M_") + search_name + '.csv')
    df.to_csv(save_path, sep='\t')

def crawl_data(web_driver_path):
    df_rows = []
    scrolltime = 1.5
    list_row_nums = 16
    search = input("검색어를 입력하세요 : ")
    driver = webdriver.Chrome()
    base_url = 'https://map.kakao.com'
    driver.get(base_url)
    search_infos = {}
    sleep(1)
    search_window = driver.find_element_by_xpath('//*[@id="search.keyword.query"]')
    search_window.send_keys(search)
    sleep(1)
    search_window.send_keys(Keys.RETURN)

    sleep(1.5)
    search_more = driver.find_element_by_xpath('//*[@id="info.search.place.more"]')
    search_more.send_keys(Keys.ENTER)
    sleep(1)
    total_row_nums = int(driver.find_element_by_xpath('//*[@id="info.search.place.cnt"]').text)
    for page in cycle(['no2', 'no3', 'no4', 'no5', 'next']):
        for i in range(1, list_row_nums):
            try:
                row = {
                    'mac_name': driver.find_element_by_xpath(
                        f'//*[@id="info.search.place.list"]/li[{i}]/div[3]/strong/a[2]').text,
                    'address': driver.find_element_by_xpath(
                        f'//*[@id="info.search.place.list"]/li[{i}]/div[5]/div[2]/p[1]').text,
                    'address2': driver.find_element_by_xpath(
                        f'//*[@id="info.search.place.list"]/li[{i}]/div[5]/div[2]/p[2]').text,
                    'score': driver.find_element_by_xpath(
                        f'//*[@id="info.search.place.list"]/li[{i}]/div[4]/span[1]/em').text
                }
                df_rows.append(row)
            except NoSuchElementException as e:
                print(f'{i} th list {e}')
                continue
            except StaleElementReferenceException as e:
                print(f'{i} th list {e}')
                break
        try:
            next_page = driver.find_element_by_xpath(f'//*[@id="info.search.page.{page}"]')
            if total_row_nums <= len(df_rows):
                break
            elif next_page.is_enabled():
                next_page.send_keys(Keys.ENTER)
            else:
                break
        except Exception as e:
            print('next page error, break out!')
            break

    # dataframe = pd.DataFrame(data=df_rows, columns=['매장명', '도로명주소', '지번주소', '평점'])
    dataframe = pd.DataFrame(data=df_rows)
    save_dataframe(search, dataframe)
    print("저장완료")


if __name__ == '__main__':
    web_driver_path = "usr/local/bin/chromedriver"
    freeze_support()
    crawl_data(web_driver_path)