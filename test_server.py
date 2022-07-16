import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import socket
import os
#pytest -s shows log o/p
class TestSeleniumRequests:
    def new_connection(self, dut, driver, ip):
        driver.get(ip + '/predoServer')
        dut.expect('session available, starting to accept')
        dut.expect('accepted new fd =')
        dut.expect('connection complete')
        dut.expect('processing new request on socket')
        dut.expect('received URI = /predoServer')
        dut.expect('response headers sent')
        dut.expect('deleted request')
        
    def new_max_connection(self, dut, driver, ip):
        driver.get(ip + '/predoServer')
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
        
    def send_req(self, dut, driver, ip):
        driver.get(ip + '/predoServer')
        dut.expect('processing new request on socket')
        dut.expect('received URI = /predoServer')
        dut.expect('response headers sent')
        dut.expect('deleted request')
        
    def close_connection(self, dut, driver):
        driver.close()
        dut.expect('deleting session on fd')
        dut.expect('httpd_server: doing select')
        
    def send_shutdown(self, dut, driver, ip):
        driver.get(ip + '/stop')
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
    
    def test_single_client(self, dut):
        ip = 'http://' + str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started', timeout=60)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver1 = webdriver.Chrome(options=chrome_options)
        self.new_connection(dut, driver1, ip)
        time.sleep(2)
        self.send_req(dut, driver1, ip)
        time.sleep(1)
        self.close_connection(dut, driver1)
        time.sleep(1)
        driver1 = webdriver.Chrome(options=chrome_options)
        self.new_connection(dut, driver1, ip)
        time.sleep(1)
        self.close_connection(dut, driver1)
        time.sleep(1)
        
    def test_multi_client(self, dut):
        ip = 'http://' + str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver1 = webdriver.Chrome(options=chrome_options)
        driver2 = webdriver.Chrome(options=chrome_options)
        driver3 = webdriver.Chrome(options=chrome_options)
        driver4 = webdriver.Chrome(options=chrome_options)
        self.new_connection(dut, driver1, ip)
        time.sleep(3)
        self.new_connection(dut, driver2, ip)
        time.sleep(3)
        self.new_connection(dut, driver3, ip)
        time.sleep(3)
        self.new_max_connection(dut, driver4, ip)
        time.sleep(5)
        self.close_connection(dut, driver2)
        time.sleep(1)  
        self.close_connection(dut, driver3)
        time.sleep(1)  
        self.close_connection(dut, driver4)
        time.sleep(1)

    def test_basic_shutdown(self, dut):
        ip = 'http://' + str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        self.send_shutdown(dut, driver, ip)

class TestTcpRequests:  
    def tcp_connection(self, dut, ip):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((ip, 80))
        dut.expect('session available, starting to accept')
        dut.expect('accepted new fd =')
        dut.expect('connection complete')
        return clientSocket

    def tcp_req(self, dut, clientSocket, data):
        clientSocket.send(data.encode())
        dut.expect('processing new request on socket')

    def tcp_recv(self, dut, clientSocket):
        dataFromServer = clientSocket.recv(1024)
        dut.expect('response headers sent')
        return dataFromServer.decode()
    
    def tcp_close(self, dut, clientSocket):
        clientSocket.close()
        dut.expect('deleting session')
        

    def test_basic_tcp(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        clientSocket1 = self.tcp_connection(dut, ip)
        dut.expect('active sockets: 1')
        data = "GET /predoServer HTTP/1.1\r\nHost:192.168.2.102\r\n\n\n"
        self.tcp_req(dut, clientSocket1, data)
        dut.expect('received URI = /predoServer')
        dataFromServer = self.tcp_recv(dut, clientSocket1)
        dut.expect('deleted request')
        assert("HTTP/1.1 200 OK" in dataFromServer)
        clientSocket2 = self.tcp_connection(dut, ip)
        dut.expect('active sockets: 2')
        data = "GET /predoServer HTTP/1.1\r\nHost:192.168.2.102\r\n\n\n"
        self.tcp_req(dut, clientSocket2, data)
        dut.expect('received URI = /predoServer')
        dataFromServer = self.tcp_recv(dut, clientSocket2)
        dut.expect('deleted request')
        assert("HTTP/1.1 200 OK" in dataFromServer)
        clientSocket1.close()
        dut.expect('active sockets: 1')
        time.sleep(3)
        clientSocket2.close()
        dut.expect('active sockets: 0')
        time.sleep(3)
    
    def base_invalid_req(self, dut, req, errno):
        ip = str(os.environ.get('ESP_IP'))
        clientSocket = self.tcp_connection(dut, ip)
        dut.expect('active sockets: 1')
        self.tcp_req(dut, clientSocket, req)
        dut.expect('parser error = ' + str(errno))
        dut.expect('400 Bad Request - Bad request syntax')
        dataFromServer = self.tcp_recv(dut, clientSocket)
        dut.expect('deleting session')
        dut.expect('active sockets: 0')
        assert("HTTP/1.1 400 Bad Request" in dataFromServer)
     
    def test_invalid_method(self, dut):
        dut.expect('main: Server Started')
        req = "NA /predoServer HTTP/1.1\r\nHost:192.168.2.102\r\n\n\n"
        self.base_invalid_req(dut, req, 16) #HPE_INVALID_METHOD = 16
        req = "GE /predoServer HTTP/1.1\r\nHost:192.168.2.102\r\n\n\n"
        self.base_invalid_req(dut, req, 16)
    
    def test_invalid_url(self, dut):
        dut.expect('main: Server Started')
        req = "GET predoServer HTTP/1.1\r\nHost:192.168.2.102\r\n\n\n"
        self.base_invalid_req(dut, req, 17) #HPE_INVALID_METHOD = 17
        req = "GET ?predoServer HTTP/1.1\r\nHost:192.168.2.102\r\n\n\n"
        self.base_invalid_req(dut, req, 17)
        req = "GET /predo?Server HTTP/1.1\r\nHost:192.168.2.102\r\n\n\n"
        self.base_invalid_req(dut, req, 17)

