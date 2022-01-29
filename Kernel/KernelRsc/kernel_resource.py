from Kernel.KernelRsc.knowledge_driver import KnowledgeDriver
from Kernel.KernelRsc.process_manager import ProcessManager
from Kernel.KernelRsc.resource_manager import ResourceManager


class KernelResource:
    def __init__(self):
        self.kd = KnowledgeDriver()
        self.rsc_mng = ResourceManager()
        self.proc_mng = ProcessManager()


kr = KernelResource()
