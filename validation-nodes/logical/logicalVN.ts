// logicalVN.ts
import { ReasoningPathway, ValidationResult } from "../../core/types/types";

export function validateLogic(pathway: ReasoningPathway): ValidationResult {
  const hasInference = pathway.steps.every(step => !!step.inference);
  return {
    verdict: hasInference ? "valid" : "invalid",
    reason: hasInference ? undefined : "Missing inference steps",
  };
}
