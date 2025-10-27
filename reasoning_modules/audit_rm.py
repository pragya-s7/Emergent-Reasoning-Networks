from reasoning_modules.base.module import ReasoningModule
import datetime
import json
import os

class SecurityAuditReasoningModule(ReasoningModule):
    def __init__(self, rules_path='reasoning_modules/data/security_rules.json'):
        super().__init__('security-audit')
        self.rules = self._load_rules(rules_path)
        self.sources = {
            "knowledge_graph": "Internal Knowledge Graph",
            "security_rules": "Internal Security Rule Set"
        }

    def _load_rules(self, rules_path):
        """Loads security rules from a JSON file."""
        if not os.path.exists(rules_path):
            print(f"Warning: Rules file not found at {rules_path}")
            return []
        with open(rules_path, 'r') as f:
            return json.load(f).get('rules', [])

    def run(self, subquery, knowledgeGraph):
        """Applies security rules to the knowledge graph to find vulnerabilities."""
        reasoning_steps = []
        triggered_rules = set()
        vulnerability_count = 0
        source_triples = []

        # Simplified rule engine
        for entity_id, entity in knowledgeGraph.entities.items():
            for rule in self.rules:
                is_violated, evidence = self._check_rule(rule, entity, knowledgeGraph)
                if is_violated:
                    triggered_rules.add(rule['name'])
                    vulnerability_count += 1
                    reasoning_steps.append({
                        "step": f"Rule Triggered: {rule['name']}",
                        "data": f"Entity '{entity.label}' (Type: {entity.type}) matched the rule.",
                        "source": self.sources["security_rules"],
                        "inference": rule['inference']
                    })
                    if evidence:
                        source_triples.append(evidence)

        if not reasoning_steps:
            conclusion = "No security vulnerabilities found based on the current rule set."
            confidence = 0.95
        else:
            conclusion = f"Security audit completed. Found {vulnerability_count} potential vulnerabilities based on {len(triggered_rules)} triggered rules."
            confidence = 0.80

        return {
            "subquery": subquery,
            "timestamp": datetime.datetime.now().isoformat(),
            "reasoningPath": reasoning_steps,
            "sources": self.sources,
            "conclusion": conclusion,
            "confidence": confidence,
            "source_triples": source_triples, # Add source_triples to the output
            "relevantMetrics": {
                "rules_checked": len(self.rules),
                "rules_triggered": len(triggered_rules),
                "vulnerabilities_found": vulnerability_count
            }
        }

    def _check_rule(self, rule, entity, knowledgeGraph):
        """Checks if a single entity violates a given rule."""
        conditions = rule.get('conditions', {})
        
        if 'all' in conditions:
            for condition in conditions['all']:
                match, evidence = self._evaluate_condition(condition, entity, knowledgeGraph)
                if not match:
                    return False, None
            return True, evidence # Return evidence from the last condition
        elif 'any' in conditions:
            for condition in conditions['any']:
                match, evidence = self._evaluate_condition(condition, entity, knowledgeGraph)
                if match:
                    return True, evidence
            return False, None
        return False, None

    def _evaluate_condition(self, condition, entity, knowledgeGraph):
        """Evaluates a single condition against an entity or its relations, returning a boolean and evidence."""
        fact = condition.get('fact')
        if not fact or len(fact) < 4:
            return False, None

        source, attribute, operator, value = fact

        if source == 'entity':
            entity_value = getattr(entity, attribute, None)
            if operator == '==' and entity_value == value:
                return True, f"{entity.label} --is_a--> {value}"
            if operator == '!=' and entity_value != value:
                return True, None # No specific triple for negation

        if source == 'relation':
            for rel in knowledgeGraph.relations:
                if rel.subject_id == entity.id:
                    rel_value = getattr(rel, attribute, None)
                    if operator == '==' and rel_value == value:
                        obj = knowledgeGraph.entities[rel.object_id]
                        return True, f"{entity.label} --{rel.predicate}--> {obj.label}"
            
            if operator == '!=':
                 if not any(getattr(rel, attribute, None) == value for rel in knowledgeGraph.relations if rel.subject_id == entity.id):
                     return True, None # No specific triple for negation

        return False, None