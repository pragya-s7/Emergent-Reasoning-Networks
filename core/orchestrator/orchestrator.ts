// orchestrator.ts
import { SubQuery } from "../types/types";

export function decomposeQuery(query: string): SubQuery[] {
  return [
    { subquestion: "What are smart contract risks?", module: "defi" },
    { subquestion: "What is sentiment from social data?", module: "sentiment" },
  ];
}
