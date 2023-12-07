#!/usr/bin/env python3
"""
    *******************************************************************************************
    HashimotoBot: Hashimoto Automation Bot
    Author: Ali Toori, Python Developer [Bot Builder]
    Website: https://boteaz.com
    YouTube: https://youtube.com/@AliToori
    *******************************************************************************************
"""
import os
import re
import pickle
import random
import datetime
from time import sleep
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains


class Hashimoto:

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        options.add_argument("--start-maximized")
        # options.add_argument(F'--user-agent={self.get_random_user_agent()}')
        # options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.actions = ActionChains(self.driver)
        self.first_time = True

    # Login to the website for smooth processing
    def login(self,):
        print('Signing-in to the website ... ')
        login_url = 'https://www.Hashimotostraat.nl/customer/account/login/'
        # Login to the website
        if os.path.isfile(r'HashimotoRes\\Cookies.pkl'):
            self.driver.get(login_url)
            print('Loading cookies ...')
            cookies = pickle.load(open(r'HashimotoRes\\Cookies.pkl', 'rb'))
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        else:
            self.driver.get(login_url)
            with open(r'HashimotoRes\User_Account.txt') as f:
                content = f.readlines()
            user = [x.strip() for x in content][0].split(':')
            print('Please login manually ! You have 60seconds to loging.')
            print('Your Email:', user[0], ', Your Password:', user[1])
            sleep(60)
            # WebDriverWait(self.driver, 100).until(EC.visibility_of_element_located((By.NAME, 'login[username]')))
            # self.driver.find_element_by_class_name('login[username]').send_keys(user[0])
            # self.driver.find_element_by_class_name('login[password]').send_keys(user[1])
            # self.driver.find_element_by_id('submitLoginForm').click()
            # Store user cookies for later use
            pickle.dump(self.driver.get_cookies(), open(r'HashimotoRes\\Cookies.pkl', 'wb'))

    def get_product(self, url):
        with open(r'HashimotoRes\User_Account.txt') as f:
            content = f.readlines()
        user = [x.strip() for x in content][0].split(':')
        # print('Your Email:', user[0], 'Password:', user[1])
        # Login to the website
        # self.login()
        print('Processing product purchase ...')
        df = pd.read_csv(r'HashimotoRes\\ProductLinks.csv', index_col=None).drop_duplicates()
        shipping_details = pd.read_csv(r'HashimotoRes\\ShippingDetails.csv', index_col=None).drop_duplicates()
        old_prices = ['$ 2,500.00', '$ 2,500.00', '$ 2,000.00']
        for index, row in df.iterrows():
            product_bought = False
            item = row['product_category']
            print('Item Number:', index + 1, ', URL:', item)
            self.driver.get(url=item)
            # Wait while the product get available
            print("Waiting for the product ...")
            while product_bought is False:
                # Wait for 1500 mSeconds
                sleep(1.5)
                # Refresh the page
                self.driver.refresh()
                # Check the status
                WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.CLASS_NAME, 'collection-grid-item')))
                for item in self.driver.find_elements_by_class_name('collection-grid-item'):
                    # # If price is not in old prices then it is a new item
                    # if str(item.find_element_by_css_selector(
                    #     '.product-price.product-item-price').text).strip() not in old_prices:
                    #
                    try:
                        btn_out_of_stock = item.find_element_by_class_name('product-item-badge')
                        print('Product is not yet uploaded:', datetime.datetime.today())
                        if str(btn_out_of_stock.text).strip() == 'Out of stock':
                            continue
                    except:
                        print('Product just get uploaded:', datetime.datetime.today())
                        # Go to the URL
                        self.driver.get(item.find_element_by_tag_name('a').get_attribute('href'))
                        # Wait and click Buy button
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.CLASS_NAME, 'shopify-payment-button')))
                        self.driver.find_element_by_class_name('shopify-payment-button').find_element_by_tag_name('button').click()
                        # Checkout
                        print('Product Checking out:', datetime.datetime.today())
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'checkout_email')))
                        self.driver.find_element_by_id('checkout_email').send_keys(shipping_details.iloc[0]['email'])
                        sleep(0.1)
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'checkout_shipping_address_first_name')))
                        self.driver.find_element_by_id('checkout_shipping_address_first_name').send_keys(shipping_details.iloc[0]['firstName'])
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'checkout_shipping_address_last_name')))
                        self.driver.find_element_by_id('checkout_shipping_address_last_name').send_keys(shipping_details.iloc[0]['lastName'])
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'checkout_shipping_address_address1')))
                        address = self.driver.find_element_by_id('checkout_shipping_address_address1')
                        self.actions.move_to_element(address)
                        address.send_keys(shipping_details.iloc[0]['address'])
                        sleep(0.1)
                        WebDriverWait(self.driver, 40).until(
                            EC.visibility_of_element_located((By.ID, 'checkout_shipping_address_zip')))
                        zip_code = self.driver.find_element_by_id('checkout_shipping_address_zip')
                        self.actions.move_to_element(zip_code)
                        zip_code.send_keys(str(shipping_details.iloc[0]['zipCode']))
                        sleep(0.1)
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'checkout_shipping_address_city')))
                        city = self.driver.find_element_by_id('checkout_shipping_address_city')
                        self.actions.move_to_element(city)
                        city.send_keys(shipping_details.iloc[0]['city'])
                        sleep(0.1)
                        # WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.NAME, 'checkout[shipping_address][phone]')))
                        # phone_number = self.driver.find_element_by_name('checkout[shipping_address][phone]')
                        # self.actions.move_to_element(phone_number)
                        # phone_number.send_keys(str(shipping_details.iloc[0]['phone']))
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'continue_button')))
                        # Wait and click on Continue Shipping button
                        pay = self.driver.find_element_by_id('continue_button')
                        self.actions.move_to_element(pay)
                        pay.click()
                        # Payment
                        # Wait for another Continue button and click
                        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.ID, 'continue_button')))
                        self.driver.find_element_by_id('continue_button').click()
                        # Wait for Card number
                        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.ID, 'number')))
                        self.driver.find_element_by_id('number').send_keys(str(shipping_details.iloc[0]['cardNumber']))
                        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.ID, 'name')))
                        self.driver.find_element_by_id('name').send_keys(str(shipping_details.iloc[0]['cardName']))
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'expiry')))
                        card_expiry = self.driver.find_element_by_id('expiry')
                        self.actions.move_to_element(card_expiry)
                        card_expiry.send_keys(str(shipping_details.iloc[0]['cardExpiry']))
                        sleep(0.1)
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'verification_value')))
                        self.driver.find_element_by_id('verification_value').send_keys(str(shipping_details.iloc[0]['CVV']))
                        WebDriverWait(self.driver, 40).until(EC.visibility_of_element_located((By.ID, 'checkout_different_billing_address_false')))
                        check_box = self.driver.find_element_by_id('checkout_different_billing_address_false')
                        self.actions.move_to_element(check_box)
                        check_box.click()
                        self.driver.find_element_by_tag_name('html').send_keys(Keys.END)
                        WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.ID, 'continue_button')))
                        self.driver.find_element_by_id('continue_button').click()
                        print('Product has been purchased successfully:', datetime.datetime.today())
                        sleep(60)

    def finish(self):
        try:
            self.driver.close()
            self.driver.quit()
        except WebDriverException as exc:
            print('Problem occurred while closing the WebDriver instance ...', exc.args)


def main():
    hashimoto = Hashimoto()
    # The main homepage URL (AKA base URL)ere
    product_link = 'https://hashimotocontemporary.myshopify.com/collections/prints/sandra-chevrier?sort_by=created-descending'
    # try:
    hashimoto.get_product(url=product_link)
    # except WebDriverException as exc:
    #     print('Exception in WebDriver:', exc.msg)
        # hashimoto.finish()


if __name__ == '__main__':
    main()
