from ..common.common import ExecuteCMD
from ..common.web_request import HttpRequest


def monitor_api_task(cmd, task_id):
    print("start job")
    e = ExecuteCMD()
    output = e.execute()
    token = output["tokenType"] + " " + output["accessToken"]
    r = HttpRequest()
    url = "https://shared-apim-prd.azure-api.net/dashboard/domains"
    header = {"Authorization": token}
    r.get_request(url, header)
