import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import socket
import os
#pytest -s shows log o/p
class SeleniumRequests:
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

class TcpRequests:  
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

class TestBasicFunctionality(SeleniumRequests, TcpRequests):
    def test_single_client(self, dut):
        ip = 'http://' + str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started', timeout=60)
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver1 = webdriver.Chrome(options=chrome_options)
        super().new_connection(dut, driver1, ip)
        time.sleep(2)
        super().send_req(dut, driver1, ip)
        time.sleep(1)
        super().close_connection(dut, driver1)
        time.sleep(1)
        driver1 = webdriver.Chrome(options=chrome_options)
        super().new_connection(dut, driver1, ip)
        time.sleep(1)
        super().close_connection(dut, driver1)
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
        super().new_connection(dut, driver1, ip)
        time.sleep(3)
        super().new_connection(dut, driver2, ip)
        time.sleep(3)
        super().new_connection(dut, driver3, ip)
        time.sleep(3)
        super().new_max_connection(dut, driver4, ip)
        time.sleep(5)
        super().close_connection(dut, driver2)
        time.sleep(1)  
        super().close_connection(dut, driver3)
        time.sleep(1)  
        super().close_connection(dut, driver4)
        time.sleep(1)
        
    def test_basic_shutdown(self, dut):
        ip = 'http://' + str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        super().send_shutdown(dut, driver, ip)
        
    def test_basic_tcp(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        clientSocket1 = super().tcp_connection(dut, ip)
        dut.expect('active sockets: 1')
        data = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().tcp_req(dut, clientSocket1, data)
        dut.expect('received URI = /predoServer')
        dataFromServer = super().tcp_recv(dut, clientSocket1)
        dut.expect('deleted request')
        assert("HTTP/1.1 200 OK" in dataFromServer)
        clientSocket2 = super().tcp_connection(dut, ip)
        dut.expect('active sockets: 2')
        data = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().tcp_req(dut, clientSocket2, data)
        dut.expect('received URI = /predoServer')
        dataFromServer = super().tcp_recv(dut, clientSocket2)
        dut.expect('deleted request')
        assert("HTTP/1.1 200 OK" in dataFromServer)
        super().tcp_close(dut, clientSocket1)
        dut.expect('active sockets: 1')
        time.sleep(3)
        super().tcp_close(dut, clientSocket2)
        dut.expect('active sockets: 0')
        time.sleep(1)
    
    def test_multi_tcp(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        clientSocket1 = super().tcp_connection(dut, ip)
        dut.expect('active sockets: 1')
        clientSocket2 = super().tcp_connection(dut, ip)
        dut.expect('active sockets: 2')
        clientSocket3 = super().tcp_connection(dut, ip)
        dut.expect('active sockets: 3')
        data = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        clientSocket1.send(data.encode())
        clientSocket2.send(data.encode())
        clientSocket3.send(data.encode())
        dut.expect('processing new request on socket')
        dataFromServer = super().tcp_recv(dut, clientSocket1)
        dut.expect('deleted request')
        assert("HTTP/1.1 200 OK" in dataFromServer)
        dut.expect('processing new request on socket')
        dataFromServer = super().tcp_recv(dut, clientSocket2)
        dut.expect('deleted request')
        assert("HTTP/1.1 200 OK" in dataFromServer)
        dut.expect('processing new request on socket')
        dataFromServer = super().tcp_recv(dut, clientSocket3)
        dut.expect('deleted request')
        assert("HTTP/1.1 200 OK" in dataFromServer)
        
class TestParser(TcpRequests):
    def test_invalid_method(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        req = "NA /predoServer HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 16) #HPE_INVALID_METHOD = 16
        req = "GE /predoServer HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 16)
    
    def test_invalid_url(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        req = "GET predoServer HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 17) #HPE_INVALID_METHOD = 17
        req = "GET ?predoServer HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 17)
        req = "GET /predo?Server HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 17)
    
    def test_invalid_HTTP(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        req = "GET /predoServer XTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 28) #HPE_INVALID_CONSTANT = 28
        req = "GET /predoServer HTTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 28)
        req = "GET /predoServer HTTPX/1.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 28)
        
    def test_invalid_version(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        req = "GET /predoServer HTTP/99.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 14)
        time.sleep(1)
        req = "GET /predoServer HTTP/9999.1\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 14)
        time.sleep(1)
        req = "GET /predoServer HTTP/1.9999\r\nHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 14)
        time.sleep(1)
        
    def test_invalid_LF(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        req = "GET /predoServer HTTP/1.1\r\rHost:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 23)
        time.sleep(1)
        req = "GET /predoServer HTTP/1.1\r Host:" + ip + "\r\n\n\n"
        super().base_invalid_req(dut, req, 23)
        time.sleep(1)
        req = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\rDummyField:DummyValue\r\n\n\n"
        super().base_invalid_req(dut, req, 23)
        time.sleep(1)
        
    def test_invalid_header_field_token(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        req = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\r\nDummy/Field:DummyValue\r\n\n\n"
        super().base_invalid_req(dut, req, 24)
        time.sleep(1)
        req = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\r\nDummyFieldDummyValue\r\n\n\n"
        super().base_invalid_req(dut, req, 24)
        time.sleep(1)
        
    def test_invalid_header_field_token(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        req = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\r\nDummy/Field:DummyValue\r\n\n\n"
        super().base_invalid_req(dut, req, 24)
        time.sleep(1)
        req = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\r\nDummyFieldDummyValue\r\n\n\n"
        super().base_invalid_req(dut, req, 24)
        time.sleep(1)
        
    def test_parser_overflow(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        uri = "X"
        for x in range(500):
            uri += "X"
        req = "GET /" + uri + " HTTP/1.1\r\nHos"
        clientSocket = super().tcp_connection(dut, ip)
        dut.expect('active sockets: 1')
        super().tcp_req(dut, clientSocket, req)
        dut.expect('request URI/header too long')
        dut.expect('414 URI Too Long - URI is too long')
        dataFromServer = self.tcp_recv(dut, clientSocket)
        dut.expect('deleting session')
        dut.expect('active sockets: 0')
        assert("HTTP/1.1 414 URI Too Long" in dataFromServer)
        time.sleep(1)
        ip = str(os.environ.get('ESP_IP'))
        field = "X"
        for x in range(10000):
            field += "X"
        req = "GET /predoServer HTTP/1.1\r\nHost:" + field
        clientSocket = super().tcp_connection(dut, ip)
        dut.expect('active sockets: 1')
        super().tcp_req(dut, clientSocket, req)
        dut.expect('request URI/header too long')
        dut.expect('431 Request Header Fields Too Large')
        dataFromServer = self.tcp_recv(dut, clientSocket)
        dut.expect('deleting session')
        dut.expect('active sockets: 0')
        assert("HTTP/1.1 431 Request Header Fields Too Large" in dataFromServer)
        time.sleep(1)
        
class TestStress(SeleniumRequests, TcpRequests):
    def test_single_client_stress(self, dut):
        ip = str(os.environ.get('ESP_IP'))
        dut.expect('main: Server Started')
        req = "GET /predoServer HTTP/1.1\r\nHost:" + ip + "\r\n\n\n"
        clientSocket = super().tcp_connection(dut, ip)
        for x in range(100):
            super().tcp_req(dut, clientSocket, req)
            dataFromServer = super().tcp_recv(dut, clientSocket)
            assert("HTTP/1.1 200 OK" in dataFromServer or "<!DOCTYPE html>" in dataFromServer)
        super().tcp_close(dut, clientSocket)
        for x in range(100):
            clientSocket = super().tcp_connection(dut, ip)
            super().tcp_close(dut, clientSocket)
        
    def test_multi_client_stress(self, dut):
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
        driverList = [driver1, driver2, driver3, driver4]
        for x in range(100):
            for driver in driverList:
                super().new_connection(dut, driver, ip)
        
        super().close_connection(dut, driver2)
        super().close_connection(dut, driver3)
        super().close_connection(dut, driver4)