import fs from 'fs';
import path from 'path';
import type { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  const logPath = path.resolve(process.cwd(), 'gensyn_logs.txt');

  if (!fs.existsSync(logPath)) {
    return res.status(404).json({ error: 'Log file not found' });
  }

  const content = fs.readFileSync(logPath, 'utf-8');
  const lines = content.split('\n').filter(line =>
    line.match(/peer|vote|round|identity|sync|connected|train/i)
  );

  res.status(200).json({ lines });
}
