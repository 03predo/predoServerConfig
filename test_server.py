import time
import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#pytest -s shows log o/p

def new_connection(dut, driver):
    driver.get('http://192.168.2.102/predoServer')
    dut.expect('httpd_accept_conn: session available, starting to accept')
    dut.expect('httpd_accept_conn: accepted new fd =')
    dut.expect('connection complete')
    dut.expect('httpd_req_new')
    dut.expect('read_block: received HTTP request block size =')
    dut.expect('httpd_req_delete')
    dut.expect('success')
    
def new_max_connection(dut, driver):
    driver.get('http://192.168.2.102/predoServer')
    dut.expect('httpd_accept_conn: no free sessions, closing least recently used')
    dut.expect('httpd_server: processing ctrl message')
    #dut.expect('httpd_sess_delete: fd =')
    dut.expect('httpd_accept_conn: session available, starting to accept')
    dut.expect('httpd_accept_conn: accepted new fd =')
    dut.expect('connection complete')
    dut.expect('httpd_req_new')
    dut.expect('read_block: received HTTP request block size =')
    dut.expect('success')
    
def new_req(dut, driver):
    driver.get('http://192.168.2.102/predoServer')
    dut.expect('httpd_req_new')
    dut.expect('read_block: received HTTP request block size =')
    dut.expect('httpd_req_delete')
    dut.expect('success')
    
def close_connection(dut, driver):
    driver.close()
    dut.expect('httpd_sess_delete: fd =')
    dut.expect('httpd_server: doing select')
   
def test_single_client(dut):
    dut.expect('main: Server Started')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver1 = webdriver.Chrome(options=chrome_options)
    new_connection(dut, driver1)
    time.sleep(2)
    new_req(dut, driver1)
    time.sleep(1)
    close_connection(dut, driver1)
    time.sleep(1)
    driver1 = webdriver.Chrome(options=chrome_options)
    new_connection(dut, driver1)
    time.sleep(1)
    close_connection(dut, driver1)
    time.sleep(1)
    
def test_multi_client(dut):
    dut.expect('main: Server Started')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver1 = webdriver.Chrome(options=chrome_options)
    driver2 = webdriver.Chrome(options=chrome_options)
    driver3 = webdriver.Chrome(options=chrome_options)
    driver4 = webdriver.Chrome(options=chrome_options)
    new_connection(dut, driver1)
    time.sleep(3)
    new_connection(dut, driver2)
    time.sleep(3)
    new_connection(dut, driver3)
    time.sleep(3)
    new_max_connection(dut, driver4)
    time.sleep(5)
    close_connection(dut, driver2)
    time.sleep(1)  
    close_connection(dut, driver3)
    time.sleep(1)  
    close_connection(dut, driver4)
    time.sleep(1)    
