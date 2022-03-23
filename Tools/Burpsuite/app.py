import requests
import sys

class BpParser(object):
    def __init__(self, msg):
        self.msg = msg
        self.method = self.msg[0].split(" ")[0]
        self.path = self.msg[0].split(" ")[1]
        self.protocol = self.msg[0].split(" ")[2].strip()
        if self.protocol == "HTTP/1.1":
            self.protocol_header = "http://"
        else:
            self.protocol_header = "https://"
        self.host = self.msg[1].split(" ")[1].strip()
        self.data = dict()
        self.headers = dict()
        support_method = ["GET", "POST"]
        if self.method not in support_method:
            print("[!] The {} method is not support".format(self.method))
            sys.exit()
        headers_key = ["User-Agent", "Accept", "Accept-Language", "Accept-Encoding", "DNT", "X-Forwarded-For", "Connection", "Cookie", "Upgrade-Insecure-Requests", "Pragma", "Cache-Control"]
        for m in self.msg:
            if m.split(" ")[0][:-1] in headers_key:
                self.headers[m.split(" ")[0][:-1]] = " ".join(m.split(" ")).replace(m.split(" ")[0], "").strip()

        self.location = 0
        if self.method == "POST":
            for i in range(len(msg)):
                if self.msg[i].strip() == "":
                    self.location = i+1
            # single row situation
            # print(self.msg[self.location])
            if self.msg[self.location].split("&"):
                for echo in self.msg[self.location].split("&"):
                    self.data[echo.split("=")[0]] = echo.split("=")[1]
            else:
                self.data[self.msg[self.location].split("=")[0]] = self.msg[self.location].split("=")[1]

    def to_py(self):
        __python_get_code = """
import requests
headers = {}
resp = requests.get(url={}, headers=headers)
print(resp.text)
"""
        __python_post_code = """
import requests
headers = {}
data = {}
resp = requests.post(url={}, headers=headers, data=data)
print(resp.text)        
        """
        if self.method == "GET":
            return __python_get_code.format(self.headers, self.protocol_header + self.host + self.path)

        if self.method == "POST":
            return __python_post_code.format(self.headers, self.data, self.protocol_header + self.host + self.path)

    '''
        模块加载时: config = 'Modules'
    '''
    def start(self, method='single', config=None):
        url = self.host
        if method == 'single':
            if config != 'Modules':
                print("[*] Do you need to change the URL?(y/N)")
                if input().upper() or 'N' == 'y':
                    url = input("url: ")

            try:
                if self.method == "GET":
                    resp = requests.get(url="{}".format(self.protocol_header + url + self.path), headers=self.headers, timeout=3)
                    print(resp.text)
                    return resp.text
                elif self.method == "POST":
                    resp = requests.post(url="{}".format(self.protocol_header + url + self.path), headers=self.headers, data=self.data, timeout=3)
                    print(resp.text)
                    return resp.text
            except Exception as e:
                print(e)
                return 0

        else:
            ''' Multiple url'''
            pass

    def set_cookie(self):
        pass

    def run(self):
        pass


if __name__ == '__main__':
    with open('demo.txt', 'r') as f:
        bp = BpParser(f.readlines())
        # bp.run()
        # print(bp.to_py())
        bp.start()
