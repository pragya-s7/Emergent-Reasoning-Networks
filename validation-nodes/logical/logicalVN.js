"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateLogic = validateLogic;
function validateLogic(pathway) {
    const hasInference = pathway.steps.every(step => !!step.inference);
    return {
        verdict: hasInference ? "valid" : "invalid",
        reason: hasInference ? undefined : "Missing inference steps",
    };
}
