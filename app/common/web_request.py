import requests, subprocess, json, copy


class HttpRequest:

    def __init__(self):
        self.headers = {
            "Connnection": "keep-alive",
            "Accept": "*/*",
            "User-Agent": "",
            "Accept-Encoding": "gzip,deflate,br"
        }

    def get_request(self, url, header=None, body=None):
        headers = copy.deepcopy(self.headers)
        if header:
            headers.update(header)
        r = requests.get(url=url, headers=headers, params=body)
        res = {
            "status_code": r.status_code,
            "response_data": r.text,
            "response_time": r.elapsed.total_seconds()
        }
        print("res: ", res)
        return res

    def post_request(self, url, header=None, body=None):
        headers = copy.deepcopy(self.headers)
        if header:
            headers.update(header)
        r = requests.post(url=url, headers=headers, json=body)
        res = {
            "status_code": r.status_code,
            "response_data": r.text,
            "response_time": r.elapsed.total_seconds()
        }
        print("res: ", res)
        return res


if __name__ == '__main__':
    from common import ExecuteCMD

    e = ExecuteCMD()
    output = e.execute()
    token = output["tokenType"] + " " + output["accessToken"]
    r = HttpRequest()
    url = "https://shared-apim-prd.azure-api.net/dashboard/domains"
    header = {"Authorization": token}
    r.get_request(url, header)