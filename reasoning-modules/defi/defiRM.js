"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.runDeFiRM = runDeFiRM;
function runDeFiRM(subquery, kg) {
    return {
        steps: [
            {
                claim: "Protocol X has low liquidity",
                evidence: ["Triple: Protocol X - hasLiquidity - Low"],
                inference: "Low liquidity implies high slippage risk",
            },
            {
                claim: "Protocol X has not been audited",
                evidence: ["Triple: Protocol X - hasAudit - False"],
                inference: "Lack of audits increases risk of exploit",
            },
        ],
    };
}
