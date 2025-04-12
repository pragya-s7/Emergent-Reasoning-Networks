// avs.ts
import { ValidationResult } from "../../core/type/types";

export function calculateTrustScore(results: ValidationResult[]): number {
  const scoreMap = { valid: 1, ambiguous: 0.5, invalid: 0 };
  const total = results.reduce((acc, r) => acc + scoreMap[r.verdict], 0);
  return total / results.length;
}
