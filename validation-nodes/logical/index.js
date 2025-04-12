function validateLogic(reasoningPath) {
    const isValid = reasoningPath && reasoningPath.length >= 2;
    return {
      valid: isValid,
      score: isValid ? 0.85 : 0.2,
      notes: isValid ? "Logical flow looks valid" : "Not enough reasoning"
    };
  }
  
  module.exports = { validateLogic };
  