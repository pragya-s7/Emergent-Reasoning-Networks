import { parseFile } from "../data-ingestion/file-parser/fileParser";
import { KnowledgeGraph } from "../core/knowledge-graph/knowledgeGraph";
import { decomposeQuery } from "../core/orchestrator/orchestrator";
import { runDeFiRM } from "../reasoning-modules/defi/defiRM";
import { validateLogic } from "../validation-nodes/logical/logicalVN";
import { calculateTrustScore } from "../eigenlayer-avs/sdk/avs";
import { ValidationResult, ReasoningPathway } from "../core/types/types";

async function runPipeline() {
    const data = await parseFile("examples/defi-risk-analysis/mock.json");
    const kg = new KnowledgeGraph();

    for (const d of data) {
        kg.addTriple(d.subject, d.relation, d.object);
    }

    const query = "What are the major risks facing Protocol X?";
    const subQueries = decomposeQuery(query);

    const results: ValidationResult[] = [];

    for (const sq of subQueries) {
        if (sq.module === "defi") {
            const pathway: ReasoningPathway = await runDeFiRM(sq.subquestion, kg);
            const verdict: ValidationResult = await validateLogic(pathway);
            results.push(verdict);
        }
    }

    const trust = calculateTrustScore(results);
    console.log("Trust Score:", trust);
}

// Execute the pipeline
runPipeline().catch(error => {
    console.error("Pipeline failed:", error);
    process.exit(1);
});