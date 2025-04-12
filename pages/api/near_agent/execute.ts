import type { NextApiRequest, NextApiResponse } from 'next';
import { orchestrate } from '../../../core/orchestrator/index';
import { KnowledgeGraph } from '../../../core/knowledge_graph/knowledgeGraph';
import { computeTrustScore } from '../../../eigenlayer-avs/sdk/index';

// Add these interfaces at the top of the file
interface ValidationResult {
  logical?: { score: number };
  grounding?: { score: number };
  novelty?: { score: number };
  [key: string]: any;
}

interface OrchestrationResult {
  reasoning: {
    conclusion: string;
    [key: string]: any;
  };
  validation: ValidationResult;
}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.status(405).end(`Method ${req.method} Not Allowed`);
    return;
  }

  try {
    const { query, openai_key, alignment_profile } = req.body;

    if (!query || !openai_key) {
      return res.status(400).json({ error: "Missing required query or OpenAI key" });
    }

    // Load latest KG
    const kg = new KnowledgeGraph();
    await kg.load_from_json("output/knowledge_graph.json");

    // Run Kairos orchestrator
    // Update the orchestrate call with type annotation
    const result = await orchestrate({
      query,
      knowledge_graph: kg,
      openai_key,
      run_validation: true,
      alignment_profile
    }) as OrchestrationResult;

    const trust_score = computeTrustScore(Object.values(result.validation));

    res.status(200).json({
      reasoning: result.reasoning,
      validation: result.validation,
      trust_score: parseFloat(trust_score)
    });

  } catch (err) {
    console.error("NEAR Agent Error:", err);
    res.status(500).json({ error: "NEAR Agent execution failed" });
  }
}
