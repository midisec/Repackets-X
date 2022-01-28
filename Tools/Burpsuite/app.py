

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
        self.useragent = self.msg[2].replace("User-Agent: ", "").strip()

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

    def run(self):
        print(self.msg)
        print(self.method)
        print(self.path)
        print(self.host)
        print(self.useragent)


if __name__ == '__main__':
    with open('demo.txt', 'r') as f:
        bp = BpParser(f.readlines())
        # bp.run()
        print(bp.to_py())