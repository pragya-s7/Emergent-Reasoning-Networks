import type { NextApiRequest, NextApiResponse } from 'next';

// Mock response data
const mockResponse = {
  reasoning: {
    module_used: "defi_risk",
    conclusion: "The DeFi protocol shows moderate risk due to centralization concerns and limited audit history.",
    reasoningPath: [
      { 
        step: "Liquidity Analysis", 
        data: "Protocol has $25M TVL across 3 pools", 
        inference: "Moderate liquidity, not enough to absorb large market movements" 
      },
      { 
        step: "Smart Contract Risk", 
        data: "One audit by CertiK completed in 2022", 
        inference: "Limited audit history increases technical risk" 
      },
      { 
        step: "Centralization Analysis", 
        data: "3 admin keys with multisig (2/3)", 
        inference: "Some centralization risk exists" 
      }
    ]
  },
  validation: {
    logical: {
      valid: true,
      score: 0.92,
      feedback: "Reasoning follows logical structure and conclusions are supported by evidence."
    },
    grounding: {
      valid: true,
      score: 0.85,
      feedback: "All claims are grounded in verifiable data from the knowledge graph."
    },
    novelty: {
      valid: true,
      score: 0.78,
      feedback: "Analysis provides some novel insights about centralization risks."
    }
  }
};

export default function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method === 'POST') {
    // Simulate processing delay
    setTimeout(() => {
      res.status(200).json(mockResponse);
    }, 1500);
  } else {
    res.setHeader('Allow', ['POST']);
    res.status(405).end(`Method ${req.method} Not Allowed`);
  }
}