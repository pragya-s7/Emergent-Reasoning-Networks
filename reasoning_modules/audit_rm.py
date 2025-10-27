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
        """Applies security rules to the knowledge graph, including emergent knowledge."""
        reasoning_steps = []
        triggered_rules = set()
        vulnerable_entities = set()
        source_triples = []

        # --- Step 1: Check for Emergent Knowledge ---
        query_entities = [e for e in knowledgeGraph.entities.values() if e.label.lower() in subquery.lower()]
        for entity in query_entities:
            # Check for emergent relations
            emergent_relations = knowledgeGraph.query(subject=entity.label, predicate="co_occurs_with")
            emergent_relations.extend(knowledgeGraph.query(object_=entity.label, predicate="co_occurs_with"))

            for subj, rel, obj in emergent_relations:
                reasoning_steps.append({
                    "step": "Leverage Emergent Knowledge",
                    "data": f"Found emergent link: {subj.label} --{rel.predicate}--> {obj.label}",
                    "source": "hebbian_emergence",
                    "inference": f"The frequent co-activation of '{subj.label}' and '{obj.label}' suggests a potential relationship that warrants investigation."
                })
                # Now, check the rules for the newly linked entity
                linked_entity = obj if subj.label == entity.label else subj
                for rule in self.rules:
                    is_violated, evidence_list = self._check_rule(rule, linked_entity, knowledgeGraph)
                    if is_violated:
                        triggered_rules.add(rule['name'])
                        vulnerable_entities.add(linked_entity.label)
                        if evidence_list:
                            source_triples.extend(evidence_list)


        # --- Step 2: Standard Rule Engine ---
        for entity_id, entity in knowledgeGraph.entities.items():
            for rule in self.rules:
                is_violated, evidence_list = self._check_rule(rule, entity, knowledgeGraph)
                if is_violated:
                    if rule['name'] not in triggered_rules: # Avoid duplicate rule triggers
                        triggered_rules.add(rule['name'])
                        vulnerable_entities.add(entity.label)
                        reasoning_steps.append({
                            "step": f"Rule Triggered: {rule['name']}",
                            "data": f"Entity '{entity.label}' (Type: {entity.type}) matched the rule.",
                            "source": self.sources["security_rules"],
                            "inference": rule['inference']
                        })
                        if evidence_list:
                            source_triples.extend(evidence_list)

        if not reasoning_steps:
            conclusion = "No security vulnerabilities found based on the current rule set."
            confidence = 0.95
        else:
            vulnerability_names = set()
            for triple in source_triples:
                if "--has_vulnerability-->" in triple:
                    vulnerability_names.add(triple.split("-->")[1].strip())
            conclusion = f"Security audit completed. Found {len(vulnerable_entities)} vulnerable entities: {', '.join(vulnerable_entities)}. Issues found related to: {', '.join(triggered_rules)}. Vulnerabilities: {', '.join(vulnerability_names)}."
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
                "vulnerabilities_found": len(vulnerable_entities)
            }
        }

    def _check_rule(self, rule, entity, knowledgeGraph):
        """Checks if a single entity violates a given rule, aggregating evidence."""
        conditions = rule.get('conditions', {})
        aggregated_evidence = []

        if 'all' in conditions:
            for condition in conditions['all']:
                match, evidence = self._evaluate_condition(condition, entity, knowledgeGraph)
                if not match:
                    return False, None
                if evidence:
                    aggregated_evidence.append(evidence)
            return True, aggregated_evidence
        
        elif 'any' in conditions:
            for condition in conditions['any']:
                match, evidence = self._evaluate_condition(condition, entity, knowledgeGraph)
                if match:
                    # For 'any', we return with the first match found
                    return True, [evidence] if evidence else []
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
                return True, None # This is an entity check, not a relation, so no triple evidence
            if operator == '!=' and entity_value != value:
                return True, None

        if source == 'relation':
            entity_relations = [r for r in knowledgeGraph.relations if r.subject_id == entity.id]

            if operator == '==':
                for rel in entity_relations:
                    if getattr(rel, attribute, None) == value:
                        obj = knowledgeGraph.entities[rel.object_id]
                        return True, f"{entity.label} --{rel.predicate}--> {obj.label}"
            
            elif operator == '!=':
                # This condition is met if NO relation with the specified attribute and value exists.
                if not any(getattr(rel, attribute, None) == value for rel in entity_relations):
                    # This is a non-existence claim, not a triple, so GroundingVN should ignore it.
                    return True, f"INFO: Entity '{entity.label}' has no relation of type '{value}'"

        return False, None