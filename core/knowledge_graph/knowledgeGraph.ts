// TypeScript wrapper for Python KnowledgeGraph
import { spawn } from 'child_process';

export class KnowledgeGraph {
  async load_from_json(path: string) {
    return new Promise((resolve, reject) => {
      const process = spawn('python3', [
        'core/knowledge_graph/knowledgeGraph.py',
        'load',
        path
      ]);
      
      process.on('close', (code) => {
        if (code === 0) {
          resolve(true);
        } else {
          reject(new Error('Failed to load knowledge graph'));
        }
      });
    });
  }
}