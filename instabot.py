import time
from tqdm import tqdm
import json

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


ACCOUNT = ''
class InstaScrapper():
    '''
    InstagramBot. Collects user profiles with images, image locations, image subscription.
    '''

    def __init__(self, username, password, testing=False):
        self.username = username
        self.password = password
        self.testing = testing
        self.accounts = set()
        self.driver = webdriver.Chrome("./chromedriver")
        self.ec = EC
        self.by = By
        self.webDriverWait = WebDriverWait
        if not self.testing:
            try:
                with open(f'data/accounts{ACCOUNT}.txt', 'r') as acc_file:
                    for acc in acc_file:
                        self.accounts.add(acc.split('\n')[0])
            except FileNotFoundError:
                pass

            try:
                with open(f'data/data{ACCOUNT}.txt', 'r') as json_file:
                    self.data = json.load(json_file)
            except FileNotFoundError:
                self.data = {}

    def login(self):
        self.driver.get("https://www.instagram.com/")

        username_cell = self.webDriverWait(self.driver, 10).until(
            self.ec.element_to_be_clickable((self.by.CSS_SELECTOR, "input[name='username']")))
        password_cell = self.webDriverWait(self.driver, 10).until(
            self.ec.element_to_be_clickable((self.by.CSS_SELECTOR, "input[name='password']")))

        username_cell.clear();
        password_cell.clear();
        username_cell.send_keys(self.username)
        password_cell.send_keys(self.password)

        log_in = self.webDriverWait(self.driver, 10).until(
            self.ec.element_to_be_clickable((self.by.CSS_SELECTOR, "button[type='submit']"))).click()

        time.sleep(3)

    def explore_hashtag(self, hashtag):
        self.driver.get("https://www.instagram.com/explore/tags/" + hashtag.replace('#', '') + '/')

    def explore_user(self, user_name):
        self.driver.get("https://www.instagram.com" + '/' + user_name.replace('/', '') + '/')

    def collect_usernames_from_hashtag(self, hashtag, n_users):
        '''
        :param hashtag: hashtah to search
        :param n_users: number of users to collect by hashtag
        '''
        pbar = tqdm(total=n_users)

        print(f"Collecting {n_users} users from hashtag: #{hashtag}")

        start_n_users = end_n_users = len(self.accounts)

        self.explore_hashtag(hashtag)

        self.webDriverWait(self.driver, 10).until(
            self.ec.element_to_be_clickable((self.by.CLASS_NAME, '_9AhH0'))).click()

        while end_n_users - start_n_users < n_users:

            try:
                self.webDriverWait(self.driver, 10).until(
                    self.ec.presence_of_element_located((
                        self.by.XPATH, "//a[@class='sqdOP yWX7d     _8A5w5   ZIAjV ']")))

                user_name = self.driver.find_element_by_xpath("//a[@class='sqdOP yWX7d     _8A5w5   ZIAjV ']").text
                if user_name not in self.accounts:
                    pbar.update(1)
                    self.accounts.add(user_name)
                    with open(f"data/accounts{ACCOUNT}.txt", 'a') as acc_file:
                        acc_file.write(user_name + '\n')
                end_n_users = len(self.accounts)
            except:
                print('Sleeping three minutes')
                time.sleep(60 * 3)

            self.webDriverWait(self.driver, 10).until(
                self.ec.element_to_be_clickable((
                    self.by.CLASS_NAME, 'coreSpriteRightPaginationArrow'))).click()

        with open(f'data/accounts{ACCOUNT}.txt', 'w') as f:
            for acc in self.accounts:
                f.write(acc + '\n')
        pbar.close()

    def build_database(self):
        '''
        Collects user profiles from collected accounts and builds a json data
        of type data[username] = user_info
        '''
        iteration = 0
        self.error_counter = 0
        for user_name in tqdm(self.accounts):
            if user_name not in self.data:
                iteration += 1
                self.collect_user_data(user_name)
                time.sleep(4)

            if iteration % 200 == 0 and iteration != 0:
                print('Saving collected data')
                with open(f'data/data{ACCOUNT}.txt', 'w') as out_file:
                    json.dump(self.data, out_file)
                print('Done')

            if self.error_counter >= 5:
                print('Breaking becaus of errors')
                break

    def collect_user_data(self, user_name):

        user_name = user_name.replace('/', '')
        suffix = '/?__a=1'
        json_url = "https://www.instagram.com/" + user_name + suffix
        self.driver.get(json_url)
        # time.sleep(1)
        try:
            self.webDriverWait(self.driver, 10).until(
                self.ec.presence_of_element_located((
                    self.by.TAG_NAME, "pre")))
            json_string = self.driver.find_element_by_tag_name('pre').text
            user_data = json.loads(json_string)

            if 'message' in user_data:
                sleep_time = 10
                self.error_counter += 1
                print(f'Sleeping for {sleep_time} minutes ')
                time.sleep(sleep_time* 60)
            else:
                if not self.testing:
                    self.data[user_name] = user_data
                else:
                    return {user_name: user_data}

        except:
            print('Sleeping three minutes')
            time.sleep(3 * 60)

    def collect_from_current_point(self, n_users):
        '''
        To use this func. Open up instagram; search for some hashtag; open up on some image.
        Function will slide through photos and will collect usernames.
        '''
        collected_url = set()
        for _ in tqdm(range(n_users)):
            collected_url.add(self.driver.current_url)
            self.webDriverWait(self.driver, 10).until(
                self.ec.element_to_be_clickable((
                    self.by.CLASS_NAME, 'coreSpriteRightPaginationArrow'))).click()
        self.collected_url = collected_url
        for url in tqdm(collected_url):
            self.driver.get(url)

            try:
                self.webDriverWait(self.driver, 10).until(
                    self.ec.presence_of_element_located((
                        self.by.XPATH, "//a[@class='sqdOP yWX7d     _8A5w5   ZIAjV ']")))

                user_name = self.driver.find_element_by_xpath("//a[@class='sqdOP yWX7d     _8A5w5   ZIAjV ']").text
                if user_name not in self.accounts:
                    self.accounts.add(user_name)
                    with open(f"data/accounts{ACCOUNT}.txt", 'a') as acc_file:
                        acc_file.write(user_name + '\n')
            except:
                pass

        with open(f'data/accounts{ACCOUNT}.txt', 'w') as f:
            for acc in self.accounts:
                f.write(acc + '\n')

    def collect_from_url(self, collected_url):
        '''
        This func collect usernames from given url of user post
        '''

        for url in tqdm(collected_url):
            self.driver.get(url)

            try:
                self.webDriverWait(self.driver, 10).until(
                    self.ec.presence_of_element_located((
                        self.by.XPATH, "//a[@class='sqdOP yWX7d     _8A5w5   ZIAjV ']")))

                user_name = self.driver.find_element_by_xpath("//a[@class='sqdOP yWX7d     _8A5w5   ZIAjV ']").text
                if user_name not in self.accounts:
                    self.accounts.add(user_name)
                    with open(f"data/accounts{ACCOUNT}.txt", 'a') as acc_file:
                        acc_file.write(user_name + '\n')
            except:
                pass

        with open(f'data/accounts{ACCOUNT}.txt', 'w') as f:
            for acc in self.accounts:
                f.write(acc + '\n')
