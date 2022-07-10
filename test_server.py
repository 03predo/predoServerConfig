import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
#pytest -s shows log o/p

def new_connection(dut, driver):
    driver.get('http://192.168.2.102/predoServer')
    dut.expect('session available, starting to accept')
    dut.expect('accepted new fd =')
    dut.expect('connection complete')
    dut.expect('processing new request on socket')
    dut.expect('received URI = /predoServer')
    dut.expect('response headers sent')
    dut.expect('deleted request')
    
def new_max_connection(dut, driver):
    driver.get('http://192.168.2.102/predoServer')
    dut.expect('no free sessions, closing least recently used')
    dut.expect('processing ctrl message')
    dut.expect('deleting session on fd')
    dut.expect('session available, starting to accept')
    dut.expect('accepted new fd =')
    dut.expect('connection complete')
    dut.expect('processing new request on socket')
    dut.expect('received URI = /predoServer')
    dut.expect('response headers sent')
    dut.expect('deleted request')
    
def send_req(dut, driver):
    driver.get('http://192.168.2.102/predoServer')
    dut.expect('processing new request on socket')
    dut.expect('received URI = /predoServer')
    dut.expect('response headers sent')
    dut.expect('deleted request')
    
def close_connection(dut, driver):
    driver.close()
    dut.expect('deleting session on fd')
    dut.expect('httpd_server: doing select')
    
def send_shutdown(dut, driver):
    driver.get('http://192.168.2.102/stop')
    dut.expect('session available, starting to accept')
    dut.expect('accepted new fd =')
    dut.expect('connection complete')
    dut.expect('processing new request on socket')
    dut.expect('received URI = /stop')
    dut.expect('response headers sent')
    dut.expect('deleted request')
    dut.expect('doing select maxfd')
    dut.expect('processing ctrl message on')
    dut.expect('deleting session on fd')
    dut.expect('removing /predoServer')
    dut.expect('removing /stop')
    dut.expect('removing /favicon.ico')
    dut.expect('server stopped')
   
def test_single_client(dut):
    dut.expect('main: Server Started')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver1 = webdriver.Chrome(options=chrome_options)
    new_connection(dut, driver1)
    time.sleep(2)
    send_req(dut, driver1)
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

def test_basic_shutdown(dut):
    dut.expect('main: Server Started')
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)
    send_shutdown(dut, driver)
    
   
