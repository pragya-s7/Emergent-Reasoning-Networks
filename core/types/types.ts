// types.ts
export type Query = {
    question: string;
  };
  
  export type SubQuery = {
    subquestion: string;
    module: string;
  };
  
  export type ReasoningStep = {
    claim: string;
    evidence?: string[];
    inference?: string;
  };
  
  export type ReasoningPathway = {
    steps: ReasoningStep[];
  };
  
  export type ValidationResult = {
    verdict: "valid" | "invalid" | "ambiguous";
    reason?: string;
  };
  
  export type TrustScore = number;
  