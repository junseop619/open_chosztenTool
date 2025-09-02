class Module:
    """Base class for all modules in the framework."""
    def __init__(self):
        self.name = ""
        self.description = ""
        self.options = {}
        self.type = ""

    def run(self, target):
        """The main function of the module, which takes the global target."""
        raise NotImplementedError("The run() method must be implemented by the subclass.")