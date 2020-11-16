from selenium import webdriver
import time
from datetime import datetime
import os
import random
from selenium.webdriver.firefox.options import Options
# from config import *


gecko_path = {PATH}


current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
new_folder = 'output_' + current_time
os.mkdir(new_folder)


options = Options()
# options.add_argument('-headless')
driver = webdriver.Firefox(executable_path=gecko_path, options=options)


def zipcode_change(zipcode_code):
    zipcode = '#nav-global-location-slot > span > a'
    python_button = driver.find_element_by_css_selector(zipcode)
    python_button.click()
    time.sleep(1)
    zipcode = driver.find_element_by_id("GLUXZipUpdateInput")
    zipcode.send_keys(zipcode_code)
    apply_selector = driver.find_element_by_css_selector('#GLUXZipUpdate > span > input')
    apply_selector.click()
    time.sleep(2)
    continue_selector = driver.find_element_by_css_selector(".a-popover-footer > span:nth-child(1) > span:nth-child(1) > input:nth-child(1)")
    continue_selector.click()
    return driver
    # continue_selector = driver.find_element_by_xpath("/html/body/div[7]/div/div/div[2]/span")
    # continue_selector.click()



def scrape_function(url,category):
    driver.get(url)
    time.sleep(3)
    page = 1
    file_name = os.getcwd()+'/'+new_folder+'/'+category+'_page_'+str(page)+'.html'
    print(file_name)
    # #
    time.sleep(2)
    html = driver.execute_script("return document.documentElement.outerHTML;")
    with open(file_name, 'w') as f:
        f.write(html)
    # testing the requests module


    time.sleep(1)

    # link = driver.find_element_by_partial_link_text('Next')
    # driver.execute_script("arguments[0].click();", link)

    i=0
    while i < 50:
        try:
            link = driver.find_element_by_partial_link_text('Next')
            driver.execute_script("arguments[0].click();", link)
            page = page+1
            # print(page)
            time_sleep = random.randint(5, 10)
            time.sleep(time_sleep)
            html = driver.execute_script("return document.documentElement.outerHTML;")
            file_name = os.getcwd()+'/'+new_folder+'/'+category+'_page_'+str(page)+'.html'
            with open(file_name, 'w') as f:
                f.write(html)
            i=i+1
            print(i)
        except:
            break


category_list = ["baby"]

url_list = [
"https://www.amazon.com/events/holidaydash/ref=gbps_ftr___wht_16579601?gb_f_GB-SUPPLE=dealStates:AVAILABLE%252CWAITLIST%252CWAITLISTFULL%252CEXPIRED%252CSOLDOUT,sortOrder:BY_SCORE,enforcedCategories:165796011&ie=UTF8"]

category_dic = dict(zip(url_list,category_list))


# time.sleep(3)
# zipcode_change('60606')
# #
for url, category in category_dic.items() :
    scrape_function(url,category)

driver.quit()
