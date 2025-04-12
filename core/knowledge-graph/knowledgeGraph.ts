export class KnowledgeGraph {
    private triples: Set<string> = new Set();
  
    addTriple(subject: string, relation: string, object: string) {
        // Serialize the triple as a string with a delimiter that won't appear in the data
        this.triples.add(`${subject}|||${relation}|||${object}`);
    }
  
    query(subject?: string, relation?: string): string[][] {
        return [...this.triples]
            .map(triple => triple.split('|||'))
            .filter(([s, r, _]) => 
                (subject === undefined || s === subject) && 
                (relation === undefined || r === relation)
            );
    }

    // Helper method to get all triples
    getAllTriples(): string[][] {
        return [...this.triples].map(triple => triple.split('|||'));
    }
}