import type { NextApiRequest, NextApiResponse } from 'next';
import { client } from '../../../scripts/utils';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { ipId } = req.body;
    try {
      const result = await client.getIPMetadata(ipId); // You’d implement this in `utils.ts`
      res.status(200).json(result);
    } catch (err) {
      console.error('Error fetching IP:', err);
      res.status(500).json({ error: 'Failed to fetch IP metadata' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
