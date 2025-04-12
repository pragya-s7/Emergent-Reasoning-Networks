"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.KnowledgeGraph = void 0;
class KnowledgeGraph {
    constructor() {
        this.triples = new Set();
    }
    addTriple(subject, relation, object) {
        // Serialize the triple as a string with a delimiter that won't appear in the data
        this.triples.add(`${subject}|||${relation}|||${object}`);
    }
    query(subject, relation) {
        return [...this.triples]
            .map(triple => triple.split('|||'))
            .filter(([s, r, _]) => (subject === undefined || s === subject) &&
            (relation === undefined || r === relation));
    }
    // Helper method to get all triples
    getAllTriples() {
        return [...this.triples].map(triple => triple.split('|||'));
    }
}
exports.KnowledgeGraph = KnowledgeGraph;
