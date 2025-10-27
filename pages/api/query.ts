import type { NextApiRequest, NextApiResponse } from 'next';
import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';
import os from 'os';

interface QueryRequest {
  query: string;
  anthropic_key?: string;
  kg_path?: string;
  run_validation?: boolean;
  alignment_profile?: any;
  knowledge_graph?: any;
}

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  try {
    const { query, anthropic_key, kg_path, run_validation, alignment_profile, knowledge_graph }: QueryRequest = req.body;

    if (!query) {
      return res.status(400).json({ error: 'Query is required' });
    }

    let kgPath = kg_path || path.join(process.cwd(), 'output', 'knowledge_graph.json');
    let tempKgPath: string | null = null;

    if (knowledge_graph) {
      tempKgPath = path.join(os.tmpdir(), `kg_${Date.now()}.json`);
      fs.writeFileSync(tempKgPath, JSON.stringify(knowledge_graph, null, 2));
      kgPath = tempKgPath;
    }

    // Prepare arguments for Python script
    const scriptPath = path.join(process.cwd(), 'scripts', 'run_orchestrator.py');
    const args = [
      '--query', query,
      '--kg-path', kgPath,
    ];

    if (anthropic_key) {
      args.push('--anthropic-key', anthropic_key);
    }

    if (run_validation !== false) {
      args.push('--run-validation');
    }

    if (alignment_profile) {
      args.push('--alignment-profile', JSON.stringify(alignment_profile));
    }

    // Execute Python orchestrator
    const python = spawn('python3', [scriptPath, ...args]);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        console.error('Python orchestrator error:', stderr);
        return res.status(500).json({
          error: 'Reasoning process failed',
          details: stderr
        });
      }

      try {
        const result = JSON.parse(stdout);

        // Calculate trust score if validation was run
        if (result.validation && Object.keys(result.validation).length > 0) {
          const scores = Object.values(result.validation)
            .filter((v: any) => v && typeof v.score === 'number')
            .map((v: any) => v.score);

          if (scores.length > 0) {
            const trustScore = scores.reduce((a: number, b: number) => a + b, 0) / scores.length;
            result.trust_score = parseFloat(trustScore.toFixed(2));
          }
        }

        if (tempKgPath) {
          fs.unlinkSync(tempKgPath);
        }

        res.status(200).json(result);
      } catch (parseError) {
        console.error('Failed to parse orchestrator output:', stdout);
        res.status(500).json({
          error: 'Failed to parse reasoning results',
          output: stdout
        });
      }
    });

  } catch (error: any) {
    console.error('API error:', error);
    res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}