from multiprocessing import freeze_support
from time import sleep
import selenium.webdriver as webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pandas as pd
from itertools import cycle
from kakaomap_crawl import save_dataframe
from address_convert import dataframe_loc_convert
from csv_postprocess import postprocess_df


def crawl_review_data():
    df_rows = []
    search = input("검색어를 입력하세요 : ")
    driver = webdriver.Chrome()
    base_url = 'https://map.kakao.com'
    driver.get(base_url)
    sleep(1)
    search_window = driver.find_element_by_xpath('//*[@id="search.keyword.query"]')
    search_window.send_keys(search)
    sleep(1)
    search_window.send_keys(Keys.RETURN)

    sleep(1.5)
    search_more = driver.find_element_by_xpath('//*[@id="info.search.place.more"]')
    search_more.send_keys(Keys.ENTER)
    sleep(1)
    driver.find_element_by_xpath(f'//*[@id="info.search.page.no1"]').send_keys(Keys.ENTER)
    sleep(1)
    total_row_nums = int(driver.find_element_by_xpath('//*[@id="info.search.place.cnt"]').text)
    for page in cycle(['no2', 'no3', 'no4', 'no5', 'next']):
        try:
            mac_names = driver.find_elements_by_xpath(
                f'//*[@id="info.search.place.list"]/li/div[3]/strong/a[2]')
            addresses = driver.find_elements_by_xpath(
                f'//*[@id="info.search.place.list"]/li/div[5]/div[2]/p[1]')
            addresses2 = driver.find_elements_by_xpath(
                f'//*[@id="info.search.place.list"]/li/div[5]/div[2]/p[2]')
            scores = driver.find_elements_by_xpath(
                f'//*[@id="info.search.place.list"]/li/div[4]/span[1]/em')
            links = driver.find_elements_by_xpath(
                f'//*[@id="info.search.place.list"]/li/div[4]/a')
            for m, a1, a2, s, l in zip(mac_names, addresses, addresses2, scores, links):
                try:
                    row = {
                        'mac_name': m.text,
                        'address': a1.text,
                        'address2': a2.text,
                        'score': s.text,
                        'link': l.get_attribute('href')
                    }
                    df_rows.append(row)
                    sleep(0.1)
                except Exception as e:
                    print(e)
        except NoSuchElementException as e:
            print(f'{e}')
            continue
        except StaleElementReferenceException as e:
            print(f'{e}')
            continue
        try:
            next_page = driver.find_element_by_xpath(f'//*[@id="info.search.page.{page}"]')
            if total_row_nums <= len(df_rows):
                break
            elif next_page.is_enabled():
                next_page.send_keys(Keys.ENTER)
                sleep(1)
            else:
                break
        except Exception as e:
            print('next page error, break out!')
            break

    dataframe = pd.DataFrame(data=df_rows)
    save_path = save_dataframe(search, dataframe)
    print("저장완료")

    # sleep(1.5)
    # search_more = driver.find_element_by_xpath('//*[@id="info.search.place.more"]')
    # search_more.send_keys(Keys.ENTER)
    # sleep(1)
    # total_row_nums = int(driver.find_element_by_xpath('//*[@id="info.search.place.cnt"]').text)
    # for page in cycle(['no2', 'no3', 'no4', 'no5', 'next']):
    #     for i in range(1, list_row_nums):
    #         try:
    #             row = {
    #                 'mac_name': driver.find_element_by_xpath(
    #                     f'//*[@id="info.search.place.list"]/li[{i}]/div[3]/strong/a[2]').text,
    #                 'address': driver.find_element_by_xpath(
    #                     f'//*[@id="info.search.place.list"]/li[{i}]/div[5]/div[2]/p[1]').text,
    #                 'address2': driver.find_element_by_xpath(
    #                     f'//*[@id="info.search.place.list"]/li[{i}]/div[5]/div[2]/p[2]').text,
    #                 'score': driver.find_element_by_xpath(
    #                     f'//*[@id="info.search.place.list"]/li[{i}]/div[4]/span[1]/em').text,
    #                 'link': driver.find_element_by_xpath(
    #                     f'//*[@id="info.search.place.list"]/li[{i}]/div[4]/a').get_attribute('href')
    #             }
    #
    #             df_rows.append(row)
    #         except NoSuchElementException as e:
    #             print(f'{i} th list {e}')
    #             continue
    #         except StaleElementReferenceException as e:
    #             print(f'{i} th list {e}')
    #             continue
    #     try:
    #         next_page = driver.find_element_by_xpath(f'//*[@id="info.search.page.{page}"]')
    #         if total_row_nums <= len(df_rows):
    #             break
    #         elif next_page.is_enabled():
    #             next_page.send_keys(Keys.ENTER)
    #             driver.implicitly_wait(0.5)
    #         else:
    #             break
    #     except Exception as e:
    #         print('next page error, break out!')
    #         break
    #
    # dataframe = pd.DataFrame(data=df_rows)
    # save_dataframe(search, dataframe)
    # print("저장완료")
    for row in df_rows:
        row['num_review'] = 0
        row['reviews'] = []
        row['scores'] = []
        row['dates'] = []
        driver.get(row['link'])
        sleep(1)
        try:
            num_reviews = driver.find_element_by_xpath('//*[@id="mArticle"]/div[5]/div[2]/a/span[1]').text
            row['num_review'] = num_reviews
        except:
            print('num_reviews error... maybe no review yet')
            continue
        num_pages, num_last = divmod(int(num_reviews), 5)
        if (num_last == 0) and (num_pages > 0): num_pages -= 1
        num_pages += 1
        for idx, page in enumerate(cycle([2, 3, 4, 5])):
            try:
                review_elems = driver.find_elements_by_xpath('//*[@id="mArticle"]/div[5]/div[4]/ul/li/div[2]/p/span')
                review_scores = driver.find_elements_by_xpath('//*[@id="mArticle"]/div[5]/div[4]/ul/li/div[1]/div/em')
                review_dates = driver.find_elements_by_xpath(
                    '//*[@id="mArticle"]/div[5]/div[4]/ul/li/div[2]/div/span[3]')
                for elem, score, date in zip(review_elems, review_scores, review_dates):
                    row['reviews'].append(elem.text)
                    row['scores'].append(score.text)
                    row['dates'].append(date.text)
                sleep(0.5)
                if page > num_pages:
                    break
            except Exception as e:
                print(e, 'review appending failed...')
                continue
            try:
                next_page = driver.find_element_by_xpath(f'//*[@id="mArticle"]/div[5]/div[4]/div/a[{page - 1}]')
                next_page.send_keys(Keys.RETURN)
                sleep(0.5)
            except Exception as e:
                print(e, 'next page failed.')
                continue
            if idx + 2 > num_pages:
                break

    dataframe = pd.DataFrame(data=df_rows)
    save_path = save_dataframe(search + '_review', dataframe)
    print("저장완료")
    return save_path


if __name__ == '__main__':
    freeze_support()
    save_path = crawl_review_data()
    postprocess_df(save_path)

