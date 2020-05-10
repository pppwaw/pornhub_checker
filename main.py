from selenium.webdriver import ChromeOptions, Chrome, Firefox, FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver
from os import system
from threading import Thread, Lock
from queue import Queue
from requests import post
from json import loads
from time import time, sleep
from signal import signal, SIGINT, SIGTERM

token = ""
captcha_token = ""
cookies = {}
mail = Queue()
true = Queue()
end = False
cookie_time = 0
l = Lock()


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
    return post('https://www.pornhub.com/user/create_account_check', headers=headers, params=params, data=data,
                cookies=cookies).text


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
    l.acquire()
    global token, captcha_token, cookie_time
    if time() - 20 <= cookie_time:
        return
    driver = get_driver()
    driver.get("https://www.pornhub.com/signup")
    try:
        token = driver.find_element_by_id("token").get_attribute("value")
        captcha_token = driver.find_element_by_id("captcha_token").get_attribute("value")
    except:
        sleep(1)
        try:
            token = driver.find_element_by_id("token").get_attribute("value")
            captcha_token = driver.find_element_by_id("captcha_token").get_attribute("value")
        except:
            driver.close()
            l.release()
            return
    cookie_time = time()
    # print(driver.get_cookies())
    for i in driver.get_cookies():
        cookies[i["name"]] = i["value"]
    driver.close()
    l.release()
    # print(token, captcha_token)


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
                # print(r)
                internet = 0
                if r == '"NOK"':
                    get_cookie()
                    if count >= 2:
                        continue
                    mail.put([email, count + 1])
                else:
                    try:
                        r = loads(r)
                    except:
                        print(email, r)
                        mail.put([email, count])
                    else:
                        if r["error_message"] == "Email has been taken.":
                            true.put(email)
                            print("True|" + email)
                        else:
                            print("False|" + email)


def t_true():
    with open("true.txt", "a", encoding="utf-8") as f:
        while True:
            email = true.get()
            f.write(email + "\n")
            f.flush()


if __name__ == '__main__':
    with open("email.txt", encoding="UTF-8") as f:
        mails = f.read().split(",")
        # print(mails)
    if len(mails) <= 200:
        tc = len(mails)
    elif len(mails) <= 1000:
        tc = 200
    else:
        tc = 1000
    get_cookie()
    pool = []
    for i in range(tc):
        mail.put([mails[i], 0])
        t = Thread(target=t_check)
        pool.append(t)
        t.start()
    Thread(target=t_true, daemon=True).start()
    [mail.put([i, 0]) for i in mails[tc:]]
    end = True
