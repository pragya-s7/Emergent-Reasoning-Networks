const { addTriple, queryGraph } = require('../core/knowledge-graph/graph');
const { orchestrate } = require('../core/orchestrator/index');
const { validateLogic } = require('../validation-nodes/logical/index');
const { computeTrustScore } = require('../eigenlayer-avs/sdk/index');

// Step 1: Populate a toy knowledge graph
addTriple("TokenX", "has_liquidity", "low");
addTriple("TokenX", "audit_history", "exploit_recent");

// Step 2: User query
const query = "What are the risks associated with TokenX?";

// Step 3: Orchestrate reasoning
const reasoningResult = orchestrate(query, { queryGraph });

// Step 4: Run logical validation
const logicResult = validateLogic(reasoningResult.reasoningPath);

// Step 5: Aggregate trust score
const trustScore = computeTrustScore([logicResult]);

// Step 6: Output result
console.log("\n=== Kairos Reasoning Result ===");
console.log("Query:", query);
console.log("Conclusion:", reasoningResult.conclusion);
console.log("Reasoning Path:", reasoningResult.reasoningPath);
console.log("Validation Result:", logicResult.notes);
console.log("Trust Score:", trustScore);
