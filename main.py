from selenium.webdriver import ChromeOptions, Chrome, Firefox, FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from os import system
from threading import Thread, Lock
from queue import Queue
from requests import post
from json import loads
from time import time
token = ""
captcha_token = ""
mail = Queue()
true = Queue()
end = False
cookie_time=0


def check(email):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': 'https://www.pornhub.com',
        'Connection': 'keep-alive',
        'Referer': 'https://www.pornhub.com/signup',
    }
    data = {
        'token': token,
        'g-recaptcha-response': captcha_token,
        'captcha_type': 'v3',
        'redirect': '',
        'check_what': 'email',
        'taste_profile': '',
        'email': email,
        'username': '',
        'password': ''
    }
    params = {'token': token}
    return post('https://www.pornhub.com/user/create_account_check', headers=headers, params=params, data=data).text


def get_driver() -> WebDriver:
    if not system("chromedriver --version"):
        o = ChromeOptions()
        o.add_argument("--headless")
        return Chrome(options=o)
    elif not system("geckodriver --version"):
        o = FirefoxOptions()
        o.headless = True
        return Firefox(options=o)
    else:
        raise FileNotFoundError("Please put Firefox or Chrome driver in program's dir or path")


def get_cookie():
    global token, captcha_token, cookie_time
    if time() - 20 <= cookie_time:
        return
    driver = get_driver()
    driver.get("https://www.pornhub.com/signup")
    token = driver.find_element_by_id("token").get_attribute("value")
    captcha_token = driver.find_element_by_id("captcha_token").get_attribute("value")
    cookie_time = time()
    driver.close()


def t_check():
    internet = 0
    while True:
        try:
            email, count = mail.get_nowait()
        except:
            if end:
                return
        else:
            try:
                r = check(email)
            except Exception as e:
                internet += 1
                if internet >= 3:
                    raise e
            else:
                internet = 0
                if r == '"NOK"':
                    if count >= 2:
                        continue
                    mail.put([email, count + 1])
                else:
                    r = loads(r)
                    if r["error_message"] == "Email has been taken.":
                        true.put(email)


if __name__ == '__main__':
    pass
