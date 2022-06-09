import yaml


class readYAML:

    def __init__(self, path):
        self.path = path
        yaml.warnings({'YAMLLoadWarning': False})

    def get_config(self):
        stream = open(self.path, mode="r", encoding="utf-8")
        data = yaml.load(stream)
        stream.close()
        return data