import type { NextApiRequest, NextApiResponse } from 'next';
import { IncomingForm } from 'formidable';
import { promises as fs } from 'fs';
import { exec } from 'child_process';

export const config = {
  api: {
    bodyParser: false,
  },
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'POST') {
    const form = new IncomingForm();
    form.parse(req, async (err, fields, files) => {
      if (err) {
        return res.status(500).json({ error: 'File upload failed' });
      }

      const file = files.file[0];
      const tempPath = file.filepath;
      const originalFilename = file.originalFilename || 'uploaded_file.txt';
      const newPath = `/tmp/${originalFilename}`;

      try {
        await fs.rename(tempPath, newPath);

        const command = `python3 scripts/main.py --file ${newPath} --openai-key ${fields.openai_key}`;
        exec(command, (error, stdout, stderr) => {
          if (error) {
            console.error(`exec error: ${error}`);
            return res.status(500).json({ error: 'Ingestion script failed', details: stderr });
          }
          res.status(200).json({ success: true, message: 'File ingested successfully', output: stdout });
        });
      } catch (e) {
        res.status(500).json({ error: 'File processing failed' });
      }
    });
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}
