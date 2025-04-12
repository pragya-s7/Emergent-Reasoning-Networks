class ReasoningModule:
    def __init__(self, name):
        self.name = name

    def run(self, subquery, knowledgeGraph, **kwargs):
        raise NotImplementedError("Subclasses must implement the run() method.")
