import json
import uuid
from datetime import datetime


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
                 created_at=None, metadata=None):
        self.subject_id = subject_id
        self.predicate = predicate
        self.object_id = object_id
        self.confidence = confidence
        self.created_at = created_at or datetime.utcnow().isoformat()
        self.source = source
        self.version = version
        self.metadata = metadata or {}

    def to_dict(self):
        return {
            "subject_id": self.subject_id,
            "predicate": self.predicate,
            "object_id": self.object_id,
            "confidence": self.confidence,
            "created_at": self.created_at,
            "source": self.source,
            "version": self.version,
            "metadata": self.metadata
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
            metadata=data.get("metadata", {})
        )



class KnowledgeGraph:
    def __init__(self):
        self.entities = {}         # id → Entity
        self.relations = []        # List[Relation]
        self.label_to_id = {}      # label → id

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

    def save_to_json(self, filepath):
        data = {
            "entities": [e.to_dict() for e in self.entities.values()],
            "relations": [r.to_dict() for r in self.relations]
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

    def query(self, *, subject=None, predicate=None, object_=None,
              subject_type=None, object_type=None,
              min_confidence=None, after=None, before=None):
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

            results.append((subj, rel, obj))
        return results

    def __str__(self):
        lines = []
        for rel in self.relations:
            subj = self.entities[rel.subject_id]
            obj = self.entities[rel.object_id]
            lines.append(
                f"{subj.label} ({subj.type}) --{rel.predicate}--> {obj.label} ({obj.type}) "
                f"[confidence={rel.confidence}, time={rel.created_at}]"
            )
        return "\n".join(lines)
