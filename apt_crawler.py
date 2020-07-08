from multiprocessing import freeze_support
from time import sleep

import selenium.webdriver as webdriver
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from itertools import cycle
import pandas as pd
from utils.address_convert import dataframe_loc_convert
from utils.csv_postprocess import postprocess_df
from utils.data_process import save_dataframe


def click_nolink_for_scrollDown(driver, scrollDown_num=100):
    url = driver.current_url
    while True:
        try:
            body = driver.find_element_by_xpath('/html/body')
        except:
            driver.refresh()
            sleep(1)
        body.click()
        sleep(0.1)
        if url == driver.current_url:
            break
        else:
            driver.execute_script("window.history.go(-1)")
    sleep(0.1)
    for i in range(scrollDown_num):
        sleep(0.1)
        body.send_keys(Keys.PAGE_DOWN)


def run_apt_crawler(basis_name='loc_name'):
    file_path = '../company_list/starbucksDT_location_info_20200707.csv'
    starbucks_data = pd.read_csv(file_path, sep='\t', index_col=0)
    starbucks_names = starbucks_data[basis_name].values

    navermap_url = 'https://map.naver.com/v5/?c=14129714.3131993,4512237.8197019,15,0,0,0,dh'
    driver = webdriver.Chrome()

    # search_window = driver.find_element_by_xpath('//*[@id="container"]/div[1]/app-base/search-box/div/div[2]/span')
    # search_window = driver.find_element_by_xpath('//*[@id="input_search1593739639254"]')
    df_rows = []
    for name in starbucks_names:
        driver.get(navermap_url)
        sleep(3)
        # driver.execute_script("arguments[0].setAttribute('text', '" + name + "')", search_window)
        ele = driver.find_element_by_class_name('btn_search')
        sleep(0.1)
        driver.execute_script("arguments[0].click();", ele)
        sleep(0.1)
        search_window = driver.find_element_by_class_name('input_box').find_element_by_class_name('input_search')
        sleep(0.5)
        search_window.send_keys(name)
        sleep(0.2)
        search_window.send_keys(Keys.ENTER)
        sleep(1)
        searched_window = driver.find_element_by_class_name('input_box').find_element_by_class_name('input_search')
        apt_search = ' 주변 아파트'
        searched_window.send_keys(apt_search)
        sleep(0.2)
        searched_window.send_keys(Keys.ENTER)
        sleep(3)
        search_lists = driver.find_elements_by_class_name('link_search')
        if len(search_lists):
            search_lists[0].click()
            sleep(2)
            infos = driver.find_elements_by_class_name('estate_text_box')
            apt_name = driver.find_element_by_class_name('summary_title')
            try:
                date = infos[0].text
                num = infos[3].text.split(' ')[0]
                price = infos[4].text
            except Exception as e:
                print(e)
                date = ''
                num = ''
                price = ''
            row = {
                '지점명' : name,
                '아파트명' : apt_name.text,
                '주소' : driver.find_element_by_class_name('end_title').text,
                '준공년월' : date,
                '세대' : num,
                '가격' : price
            }
            df_rows.append(row)

        dataframe = pd.DataFrame(data=df_rows)
        save_path = save_dataframe('apt_review', dataframe)
        print(f"{save_path} 저장완료")


    dataframe = pd.DataFrame(data=df_rows)
    save_path = save_dataframe('apt_review', dataframe)
    print(f"{save_path} 저장완료")
    return save_path



if __name__ == '__main__':
    # freeze_support()
    # save_path = crawl_data()
    # save_path = dataframe_loc_convert(save_path, 'address')

    # save_path = 'data/2020-06-25_16_23_스타벅스dt.csv'
    run_apt_crawler(basis_name='지점')
    # save_path = postprocess_df(save_path, basis_name='address')
    # review_crawl(save_path, basis_column='address')
