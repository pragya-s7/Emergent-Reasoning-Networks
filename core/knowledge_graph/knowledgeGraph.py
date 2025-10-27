import json
import uuid
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional, Set
from collections import defaultdict
import math


class Entity:
    def __init__(self, label, type_, properties=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.label = label
        self.type = type_
        self.properties = properties or {}

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "type": self.type,
            "properties": self.properties
        }

    @staticmethod
    def from_dict(data):
        return Entity(
            label=data["label"],
            type_=data["type"],
            properties=data.get("properties", {}),
            id=data["id"]
        )


class Relation:
    def __init__(self, subject_id, predicate, object_id, confidence=1.0, source=None, version=None,
                 created_at=None, metadata=None, activation_count=0, last_activated=None):
        self.subject_id = subject_id
        self.predicate = predicate
        self.object_id = object_id
        self.confidence = confidence  # Edge strength (Hebbian weight)
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.source = source
        self.version = version
        self.metadata = metadata or {}

        # Hebbian plasticity fields
        self.activation_count = activation_count
        self.last_activated = last_activated

    def to_dict(self):
        return {
            "subject_id": self.subject_id,
            "predicate": self.predicate,
            "object_id": self.object_id,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "source": self.source,
            "version": self.version,
            "metadata": self.metadata,
            "activation_count": self.activation_count,
            "last_activated": self.last_activated
        }

    @staticmethod
    def from_dict(data):
        return Relation(
            subject_id=data["subject_id"],
            predicate=data["predicate"],
            object_id=data["object_id"],
            confidence=data.get("confidence", 1.0),
            created_at=data.get("created_at"),
            source=data.get("source"),
            version=data.get("version"),
            metadata=data.get("metadata", {}),
            activation_count=data.get("activation_count", 0),
            last_activated=data.get("last_activated")
        )


class KnowledgeGraph:
    """
    Knowledge Graph with Hebbian Plasticity.

    Implements "concepts that are reasoned together, connect together" - analogous
    to Hebbian learning in neural networks. Edge strengths adapt based on usage
    patterns during reasoning.
    """

    def __init__(self, hebbian_config=None):
        self.entities = {}         # id → Entity
        self.relations = []        # List[Relation]
        self.label_to_id = {}      # label → id

        # Hebbian plasticity configuration
        self.hebbian_config = hebbian_config or {
            "learning_rate": 0.1,        # How much to strengthen on activation
            "decay_rate": 0.05,          # How much to weaken unused edges
            "emergence_threshold": 3,     # Co-activations needed to create new edge
            "min_strength": 0.1,          # Below this, edges are pruned
            "max_strength": 1.0,          # Maximum edge strength
        }

        # Track co-activations for emergent connections
        self.activation_window = []     # Recent entity activations
        self.coactivation_counts = defaultdict(int)  # (e1, e2) → count

    def add_entity(self, label, type_, properties=None):
        if label in self.label_to_id:
            return self.label_to_id[label]
        ent = Entity(label, type_, properties)
        self.entities[ent.id] = ent
        self.label_to_id[label] = ent.id
        return ent.id

    def add_relation(self, subject_label, predicate, object_label, *,
                     subject_type="Thing", object_type="Thing",
                     confidence=1.0, source=None, version=None):
        subject_id = self.add_entity(subject_label, subject_type)
        object_id = self.add_entity(object_label, object_type)
        rel = Relation(subject_id, predicate, object_id, confidence, source, version)
        self.relations.append(rel)
        return rel

    # ==================== HEBBIAN PLASTICITY METHODS ====================

    def activate_relation(self, subject_label: str, predicate: str, object_label: str):
        """
        Hebbian strengthening: When an edge is used in reasoning, strengthen it.
        Implements Long-Term Potentiation (LTP) analogy.
        """
        subject_id = self.label_to_id.get(subject_label)
        object_id = self.label_to_id.get(object_label)

        if not subject_id or not object_id:
            return  # Entities don't exist

        # Find the relation
        for rel in self.relations:
            if (rel.subject_id == subject_id and
                rel.predicate == predicate and
                rel.object_id == object_id):

                # Strengthen the edge (Hebbian learning)
                learning_rate = self.hebbian_config["learning_rate"]
                max_strength = self.hebbian_config["max_strength"]

                # Asymptotic strengthening (diminishing returns)
                delta = learning_rate * (max_strength - rel.confidence)
                rel.confidence = min(max_strength, rel.confidence + delta)

                # Update activation tracking
                rel.activation_count += 1
                rel.last_activated = datetime.utcnow().isoformat()

                print(f"[Hebbian] Strengthened: {subject_label} --{predicate}--> {object_label} "
                      f"(strength: {rel.confidence:.3f}, activations: {rel.activation_count})")
                break

    def activate_entities(self, entity_labels: List[str]):
        """
        Track entity co-activations for emergent connection formation.
        When entities are activated together (in same reasoning context),
        track this for potential new edge creation.
        """
        entity_ids = [self.label_to_id.get(label) for label in entity_labels
                      if label in self.label_to_id]

        if len(entity_ids) < 2:
            return

        # Add to activation window
        timestamp = datetime.utcnow()
        self.activation_window.append((timestamp, set(entity_ids)))

        # Count co-activations for all pairs
        for i, e1 in enumerate(entity_ids):
            for e2 in entity_ids[i+1:]:
                pair = tuple(sorted([e1, e2]))
                self.coactivation_counts[pair] += 1

        # Prune old activations (keep last 100)
        if len(self.activation_window) > 100:
            self.activation_window = self.activation_window[-100:]

    def form_emergent_connections(self):
        """
        Create new edges between frequently co-activated entities.
        Implements emergent knowledge formation - insights that weren't
        explicitly stated but emerged from reasoning patterns.
        """
        threshold = self.hebbian_config["emergence_threshold"]
        new_edges = []

        for (e1_id, e2_id), count in self.coactivation_counts.items():
            if count >= threshold:
                # Check if edge already exists
                existing = False
                for rel in self.relations:
                    if ((rel.subject_id == e1_id and rel.object_id == e2_id) or
                        (rel.subject_id == e2_id and rel.object_id == e1_id)):
                        existing = True
                        break

                if not existing:
                    # Create emergent connection
                    e1 = self.entities[e1_id]
                    e2 = self.entities[e2_id]

                    # Initial strength based on co-activation frequency
                    initial_strength = min(0.5, count * 0.1)

                    new_rel = Relation(
                        subject_id=e1_id,
                        predicate="co_occurs_with",  # Emergent relation type
                        object_id=e2_id,
                        confidence=initial_strength,
                        source="hebbian_emergence",
                        version="emergent"
                    )
                    self.relations.append(new_rel)
                    new_edges.append((e1.label, e2.label, initial_strength))

                    print(f"[Hebbian] Emergent edge: {e1.label} <--> {e2.label} "
                          f"(strength: {initial_strength:.3f}, co-activations: {count})")

        # Reset co-activation counts after forming edges
        if new_edges:
            self.coactivation_counts.clear()

        return new_edges

    def apply_temporal_decay(self):
        """
        Hebbian decay: Unused edges weaken over time.
        Implements Long-Term Depression (LTD) analogy and forgetting.
        """
        now = datetime.utcnow()
        decay_rate = self.hebbian_config["decay_rate"]
        min_strength = self.hebbian_config["min_strength"]

        decayed = []
        pruned = []

        for rel in self.relations:
            # Skip edges that were never activated (from initial data)
            if rel.last_activated is None:
                continue

            # Calculate time since last activation
            last_active = datetime.fromisoformat(rel.last_activated)
            days_inactive = (now - last_active).days

            # Decay based on inactivity (exponential decay)
            if days_inactive > 0:
                decay = decay_rate * (1 - math.exp(-days_inactive / 30))  # 30-day half-life
                old_strength = rel.confidence
                rel.confidence = rel.confidence - decay  # Don't floor here, let pruning handle it

                if rel.confidence > min_strength:
                    decayed.append((
                        self.entities[rel.subject_id].label,
                        rel.predicate,
                        self.entities[rel.object_id].label,
                        old_strength,
                        rel.confidence
                    ))

        # Prune very weak edges
        self.relations = [rel for rel in self.relations
                          if rel.confidence >= min_strength or rel.last_activated is None]

        if decayed:
            print(f"[Hebbian] Decayed {len(decayed)} edges")

        return decayed

    def get_edge_strength(self, subject_label: str, predicate: str, object_label: str) -> float:
        """Get the current strength of an edge."""
        subject_id = self.label_to_id.get(subject_label)
        object_id = self.label_to_id.get(object_label)

        if not subject_id or not object_id:
            return 0.0

        for rel in self.relations:
            if (rel.subject_id == subject_id and
                rel.predicate == predicate and
                rel.object_id == object_id):
                return rel.confidence

        return 0.0

    def get_strongest_edges(self, top_k: int = 10) -> List[Tuple[str, str, str, float]]:
        """Get the strongest edges in the graph."""
        edge_strengths = []
        for rel in self.relations:
            subj = self.entities[rel.subject_id].label
            obj = self.entities[rel.object_id].label
            edge_strengths.append((subj, rel.predicate, obj, rel.confidence))

        edge_strengths.sort(key=lambda x: x[3], reverse=True)
        return edge_strengths[:top_k]

    def consolidate_memory(self):
        """
        Full consolidation cycle: Form emergent connections and apply decay.
        Should be called periodically (e.g., after each reasoning session).
        """
        print("\n[Hebbian] Running memory consolidation...")

        # Form new emergent connections
        new_edges = self.form_emergent_connections()

        # Apply temporal decay
        decayed = self.apply_temporal_decay()

        print(f"[Hebbian] Consolidation complete: {len(new_edges)} emergent edges, "
              f"{len(decayed)} decayed edges\n")

        return {
            "emergent_edges": new_edges,
            "decayed_edges": len(decayed)
        }

    # ==================== ORIGINAL METHODS ====================

    def save_to_json(self, filepath):
        data = {
            "entities": [e.to_dict() for e in self.entities.values()],
            "relations": [r.to_dict() for r in self.relations],
            "hebbian_config": self.hebbian_config,
            "coactivation_counts": {
                f"{k[0]}_{k[1]}": v for k, v in self.coactivation_counts.items()
            }
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def load_from_json(self, filepath):
        with open(filepath, "r") as f:
            data = json.load(f)

        self.entities = {}
        self.relations = []
        self.label_to_id = {}

        for e_dict in data["entities"]:
            ent = Entity.from_dict(e_dict)
            self.entities[ent.id] = ent
            self.label_to_id[ent.label] = ent.id

        for r_dict in data["relations"]:
            rel = Relation.from_dict(r_dict)
            self.relations.append(rel)

        # Load Hebbian config if present
        if "hebbian_config" in data:
            self.hebbian_config.update(data["hebbian_config"])

        # Load co-activation counts if present
        if "coactivation_counts" in data:
            self.coactivation_counts = defaultdict(int)
            for key, val in data["coactivation_counts"].items():
                e1, e2 = key.split("_")
                self.coactivation_counts[(e1, e2)] = val

    def query(self, *, subject=None, predicate=None, object_=None,
          subject_type=None, object_type=None,
          min_confidence=None, after=None, before=None,
          metadata_filter=None):
        results = []
        for rel in self.relations:
            subj = self.entities[rel.subject_id]
            obj = self.entities[rel.object_id]

            if subject and subj.label != subject:
                continue
            if subject_type and subj.type != subject_type:
                continue
            if object_ and obj.label != object_:
                continue
            if object_type and obj.type != object_type:
                continue
            if predicate and rel.predicate != predicate:
                continue
            if min_confidence and rel.confidence < min_confidence:
                continue
            if after and rel.created_at < after:
                continue
            if before and rel.created_at > before:
                continue
            if metadata_filter:
                for k, v in metadata_filter.items():
                    if rel.metadata.get(k) != v:
                        break
                else:
                    results.append((subj, rel, obj))
                continue

            results.append((subj, rel, obj))
        return results

    def __str__(self):
        lines = []
        for rel in self.relations:
            subj = self.entities[rel.subject_id]
            obj = self.entities[rel.object_id]
            lines.append(
                f"{subj.label} ({subj.type}) --{rel.predicate}--> {obj.label} ({obj.type}) "
                f"[strength={rel.confidence:.2f}, activations={rel.activation_count}]"
            )
        return "\n".join(lines)
