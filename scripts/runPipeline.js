"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
const fileParser_1 = require("../data-ingestion/file-parser/fileParser");
const knowledgeGraph_1 = require("../core/knowledge-graph/knowledgeGraph");
const orchestrator_1 = require("../core/orchestrator/orchestrator");
const defiRM_1 = require("../reasoning-modules/defi/defiRM");
const logicalVN_1 = require("../validation-nodes/logical/logicalVN");
const avs_1 = require("../eigenlayer-avs/sdk/avs");
function runPipeline() {
    return __awaiter(this, void 0, void 0, function* () {
        const data = yield (0, fileParser_1.parseFile)("examples/defi-risk-analysis/mock.json");
        const kg = new knowledgeGraph_1.KnowledgeGraph();
        for (const d of data) {
            kg.addTriple(d.subject, d.relation, d.object);
        }
        const query = "What are the major risks facing Protocol X?";
        const subQueries = (0, orchestrator_1.decomposeQuery)(query);
        const results = [];
        for (const sq of subQueries) {
            if (sq.module === "defi") {
                const pathway = yield (0, defiRM_1.runDeFiRM)(sq.subquestion, kg);
                const verdict = yield (0, logicalVN_1.validateLogic)(pathway);
                results.push(verdict);
            }
        }
        const trust = (0, avs_1.calculateTrustScore)(results);
        console.log("Trust Score:", trust);
    });
}
// Execute the pipeline
runPipeline().catch(error => {
    console.error("Pipeline failed:", error);
    process.exit(1);
});
