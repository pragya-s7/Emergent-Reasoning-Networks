"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.calculateTrustScore = calculateTrustScore;
function calculateTrustScore(results) {
    const scoreMap = { valid: 1, ambiguous: 0.5, invalid: 0 };
    const total = results.reduce((acc, r) => acc + scoreMap[r.verdict], 0);
    return total / results.length;
}
