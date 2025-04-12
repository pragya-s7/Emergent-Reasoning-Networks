import { promises as fs } from 'fs';

export async function parseFile(path: string): Promise<Record<string, any>[]> {
    const raw = await fs.readFile(path, "utf-8");
    return JSON.parse(raw); // assume a structured array of objects for MVP
}