import type { NextApiRequest, NextApiResponse } from 'next';
import fs from 'fs';
import path from 'path';

/**
 * Mock: Parse local Gensyn stats file generated during RL Swarm runs.
 * In production: Replace this with actual on-chain data querying from Gensyn smart contracts or local socket.
 */
export default function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const statsPath = path.resolve(process.cwd(), 'gensyn_stats/mock_stats.json');
    const data = fs.readFileSync(statsPath, 'utf-8');
    const stats = JSON.parse(data);
    res.status(200).json(stats);
  } catch (err) {
    res.status(500).json({ error: 'Could not load Gensyn stats' });
  }
}
