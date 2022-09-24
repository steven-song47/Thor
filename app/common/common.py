from subprocess import Popen, PIPE
import json, yaml


class ExecuteCMD:

    def __init__(self):
        self.az_login_for_prod = "az account get-access-token --resource api://c3ccb5fe-51db-4266-a96b-a3521f234405"

    def execute(self, cmd=None, shell=True):
        output = ""
        if not cmd:
            cmd = self.az_login_for_prod
        p = Popen(cmd, shell=shell, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        for line in iter(p.stdout.readline, b''):
            # print("line:", line)
            output += str(line, "UTF-8")
            if not Popen.poll(p) is None:
                if line == "":
                    break
        p.stdout.close()
        output = json.loads(output)
        # print(output)
        return output


class YamlOperation:

    def __init__(self):
        self.default_path = "../data/"

    def write_yaml(self, name, data, path=None):
        if path:
            file_path = path + name
        else:
            file_path = self.default_path + name
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(yaml.dump(data, allow_unicode=True, sort_keys=False))

    def read_yaml(self, name, path=None):
        if path:
            file_path = path + name
        else:
            file_path = self.default_path + name
        with open(file_path, encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            print(data)
        return data


class SendEmail:

    def __init__(self):
        pass


if __name__ == '__main__':
    # e = ExecuteCMD()
    # e.execute()
    y = YamlOperation()
    y.write_yaml("test", {"name": "test", "list": ["v1", "v2"]})
    y.read_yaml("test")