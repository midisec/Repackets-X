import requests


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

        self.headers = dict()
        headers_key = ["User-Agent", "Accept", "Accept-Language", "Accept-Encoding", "DNT", "X-Forwarded-For", "Connection", "Upgrade-Insecure-Requests"]
        for m in self.msg:
            if m.split(" ")[0][:-1] in headers_key:
                self.headers[m.split(" ")[0][:-1]] = " ".join(m.split(" ")).replace(m.split(" ")[0], "").strip()

    def to_py(self):
        __python_get_code = """
        import requests
        headers = dict()
        headers["User-Agent"] = {}
        resp = requests.get(url={}, headers=headers)
        print(resp.text)
        """
        if self.method == "GET":
            return __python_get_code.format(self.useragent, self.protocol_header + self.host + self.path)


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

            resp = requests.get(url="{}".format(self.protocol_header + url + self.path), headers=self.headers)

            print(self.headers)

        else:
            ''' Multiple url'''
            pass



    def run(self):
        pass


if __name__ == '__main__':
    with open('demo.txt', 'r') as f:
        bp = BpParser(f.readlines())
        # bp.run()
        # print(bp.to_py())
        bp.start()