import type { NextApiRequest, NextApiResponse } from 'next';
import { registerIP } from '../../../scripts/register_story';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'POST') {
    try {
      const { ip_metadata, nft_metadata } = req.body;
      
      // Call the registerIP function
      const result = await registerIP({ ip_metadata, nft_metadata });
      
      res.status(200).json(result);
    } catch (error) {
      console.error('Error registering IP:', error);
      res.status(500).json({ error: 'Failed to register IP' });
    }
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}