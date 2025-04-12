from reasoning_modules.base.module import ReasoningModule

class MacroReasoningModule(ReasoningModule):
    def __init__(self):
        super().__init__('macro')

    def run(self, subquery, knowledgeGraph):
        facts = knowledgeGraph.queryGraph("global_economy")
        logic = [
            "Interest rates are rising",
            "Market volatility has increased",
            "Inflation data suggests tightening"
        ]
        return {
            "subquery": subquery,
            "reasoningPath": logic,
            "conclusion": "Macro conditions suggest caution in investment strategy"
        }