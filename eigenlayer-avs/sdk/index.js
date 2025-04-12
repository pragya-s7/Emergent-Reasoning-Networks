function computeTrustScore(validationResults) {
    const scores = validationResults.map(v => v.score);
    const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
    return avg.toFixed(2);
  }
  
  module.exports = { computeTrustScore };
  