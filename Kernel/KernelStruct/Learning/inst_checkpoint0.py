class InstCheckPoint0Statement:
    def __init__(self, command, args):
        self.command = command
        self.args = args


class InstCheckPoint0:
    def __init__(self):
        self.usage = {'find': None, 'of': None}
        self.instance_input = None
        self.instance_output = None
        self.steps = []
