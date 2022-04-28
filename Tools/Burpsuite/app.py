import requests
import sys
import re
import urllib.parse
from requests_toolbelt.multipart.encoder import MultipartEncoder
from Common.module.request.headers.keys import read_default_header_keys, read_extend_header_keys

class BpParser(object):
    def __init__(self, msg):
        self.msg = msg
        self.method = self.msg[0].split(" ")[0]
        self.file_upload_flag = False
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
        # headers_key = ["User-Agent", "Accept", "Accept-Language", "Accept-Encoding", "Referer", "DNT", "X-Forwarded-For", "Connection", "Cookie", "Upgrade-Insecure-Requests", "Content-Type", "Content-Length", "Pragma", "Cache-Control"]
        headers_key = []
        headers_key = headers_key + read_default_header_keys() + read_extend_header_keys()
        for m in self.msg:
            if m.split(" ")[0][:-1] in headers_key:
                self.headers[m.split(" ")[0][:-1]] = " ".join(m.split(" ")).replace(m.split(" ")[0], "").strip()

        self.location = 0
        if self.method == "POST":
            for i in range(len(msg)):
                if self.msg[i].strip() == "":
                    self.location = i+1
                    break

            # print(self.msg[self.location])
            if self.msg[self.location].startswith("---"):
                # form-data
                # Same as above
                self.file_upload_flag = True
                self.boundary = self.msg[self.location].strip()
                file_content_keys = ["Content-Disposition", "Content-Type"]
                self.file_content_header = dict()
                self.file_content = ""
                self.file_content_start_location = 0
                for index in range(self.location, len(msg)):
                    # print(msg[index].strip())
                    if msg[index].startswith("------------------------"):
                        continue
                    elif msg[index].strip() == "":
                        self.file_content_start_location = index + 1
                        break
                    else:
                        if msg[index].strip().split(" ")[0][:-1] in file_content_keys:
                            self.file_content_header[msg[index].split(" ")[0][:-1]] = msg[index].strip().replace(msg[index].split(" ")[0], "").strip()
                # print(self.file_content_header)
                # print(self.file_content_header["Content-Disposition"])
                pat = r'(?P<type>.*?); name="(?P<name>.*?)"; filename="(?P<filename>.*?)"'
                file_msg = re.search(pat, self.file_content_header["Content-Disposition"])
                if file_msg:
                    self.file_content_type = file_msg['type']
                    self.file_content_name = file_msg['name']
                    self.file_content_file_name = file_msg['filename']
                else:
                    print("[!] The file content header may error")
                    sys.exit()

                for index in range(self.file_content_start_location, len(msg)):
                    if msg[index].startswith("------------------------"):
                        break
                    else:
                        self.file_content = self.file_content + msg[index].strip() + "\n"
                # print(self.file_content)

            else:
                # single row situation
                # just post some data
                if self.msg[self.location].split("&"):
                    for echo in self.msg[self.location].split("&"):
                        self.data[urllib.parse.unquote(echo.split("=")[0].replace("+", " "))] = urllib.parse.unquote(echo.split("=")[1].replace("+", " "))
                else:
                    self.data[urllib.parse.unquote(self.msg[self.location].split("=")[0].replace("+", " "))] = urllib.parse.unquote(self.msg[self.location].split("=")[1].replace("+", " "))

    def to_py(self):
        __python_get_code = """
import requests
headers = {}
resp = requests.get(url="{}", headers=headers)
print(resp.text)
"""
        __python_post_code = """
import requests
headers = {}
data = {}
resp = requests.post(url="{}", headers=headers, data=data)
print(resp.text)        
        """
        __python_post_file_content_code = """
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
headers = {0}
fileDict = dict()
fileDict["{1}"] = ("{2}", r'''{3}''', "{4}")
m = MultipartEncoder(fields=fileDict, boundary="-------{5}")
headers['Content-Type'] = m.content_type
resp = requests.post(url="{6}", headers=headers, data=m, timeout=3)
print(resp.text)
"""

        if self.method == "GET":
            return __python_get_code.format(self.headers, self.protocol_header + self.host + self.path)

        if self.method == "POST" and self.file_upload_flag == False:
            return __python_post_code.format(self.headers, self.data, self.protocol_header + self.host + self.path)

        if self.method == "POST" and self.file_upload_flag:
            return __python_post_file_content_code.format(self.headers,
                                                          self.file_content_name, self.file_content_file_name,
                                                          self.file_content.strip(), self.file_content_header['Content-Type'],
                                                          self.boundary.replace("-", ""),
                                                          self.protocol_header + self.host + self.path
                                                          )
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
                elif self.method == "POST" and self.file_upload_flag == False:
                    resp = requests.post(url="{}".format(self.protocol_header + url + self.path), headers=self.headers, data=self.data, timeout=3)
                    print(resp.status_code)
                    print(resp.text)
                    return resp.text
                elif self.method == "POST" and self.file_upload_flag:
                    fileDict = {"{}".format(self.file_content_name): (
                        "{}".format(self.file_content_file_name), r'''{}'''.format(self.file_content),
                        "{}".format(self.file_content_header['Content-Type']))}
                    m = MultipartEncoder(fields=fileDict, boundary="-------{}".format(self.boundary.replace("-", "")))
                    self.headers['Content-Type'] = m.content_type
                    resp = requests.post(url="{}".format(self.protocol_header + url + self.path), headers=self.headers, data=m, timeout=3)
                    print(resp.text)

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
        print(bp.to_py())
        bp.start()
