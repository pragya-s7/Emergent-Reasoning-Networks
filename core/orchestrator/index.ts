// TypeScript wrapper for Python orchestrator
import { spawn } from 'child_process';

export function orchestrate({ query, knowledge_graph, anthropic_key, run_validation, alignment_profile }: any) {
  // Call Python orchestrator through a subprocess
  return new Promise((resolve, reject) => {
    const process = spawn('python3', [
      'core/orchestrator/index.py',
      JSON.stringify({ query, knowledge_graph, anthropic_key, run_validation, alignment_profile })
    ]);
    
    let result = '';
    process.stdout.on('data', (data) => {
      result += data;
    });
    
    process.on('close', (code) => {
      if (code === 0) {
        resolve(JSON.parse(result));
      } else {
        reject(new Error('Orchestrator failed'));
      }
    });
  });
}