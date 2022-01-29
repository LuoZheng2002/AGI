class Process:
    next_id = 0

    def __init__(self, parent_id, method_id):
        self.parent_id = parent_id
        self.method_id = method_id
        self.children_id = []
        self.registers = []
        self.id = Process.next_id
        Process.next_id += 1


class ProcessManager:

    def __init__(self):
        self.processes = []

    def create_process(self, caller_id, method_id) -> int:
        self.processes.append(Process(caller_id, method_id))
        return Process.next_id - 1

    def destroy_process(self, proc_id):
        for i, proc in enumerate(self.processes):
            if proc.id == proc_id:
                self.processes.pop(i)
                return
        assert False
