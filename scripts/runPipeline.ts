import { parseFile } from "../data-ingestion/file-parser/fileParser";
import { KnowledgeGraph } from "../core/knowledge-graph";
import { decomposeQuery } from "../core/orchestrator";
import { runDeFiRM } from "../reasoning-modules/defi/defiRM";
import { validateLogic } from "../validation-nodes/logical/logicalVN";
import { calculateTrustScore } from "../eigenlayer-avs/sdk/avs";

const data = parseFile("examples/defi-risk-analysis/mock.json");
const kg = new KnowledgeGraph();

for (const d of data) {
  kg.addTriple(d.subject, d.relation, d.object);
}

const query = "What are the major risks facing Protocol X?";
const subQueries = decomposeQuery(query);

const results = [];

for (const sq of subQueries) {
  if (sq.module === "defi") {
    const pathway = runDeFiRM(sq.subquestion, kg);
    const verdict = validateLogic(pathway);
    results.push(verdict);
  }
}

const trust = calculateTrustScore(results);
console.log("Trust Score:", trust);
