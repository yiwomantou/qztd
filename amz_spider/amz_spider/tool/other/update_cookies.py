from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

urls = ["https://www.amazon.com", "https://www.amazon.co.uk", "https://www.amazon.de", "https://www.amazon.fr",
        "https://www.amazon.it", "https://www.amazon.es", "https://www.amazon.co.jp"]

for url in urls:
    browser = webdriver.Chrome()
    try:
        browser.get(url)
        wait = WebDriverWait(browser, 10)
        sign_key = wait.until(EC.presence_of_element_located((By.ID, 'nav-link-accountList')))
        ActionChains(browser).move_to_element_with_offset(sign_key, 1, 1).click().perform()
        input_email = wait.until(EC.presence_of_element_located((By.ID, 'ap_email')))
        input_email.send_keys('zestnation_fang@163.com')
        input_email.send_keys(Keys.ENTER)
        input_password = wait.until(EC.presence_of_element_located((By.ID, 'ap_password')))
        input_password.send_keys('qztd123456')
        input_password.send_keys(Keys.ENTER)
        time.sleep(5)
        cookie = browser.get_cookies()
        print(cookie)
    finally:
        browser.close()
    break

