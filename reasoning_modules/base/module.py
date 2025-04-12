class ReasoningModule:
    def __init__(self, name):
        self.name = name

    def run(self, subquery, knowledgeGraph):
        raise NotImplementedError("run() not implemented")