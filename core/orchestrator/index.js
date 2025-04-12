const DeFiReasoningModule = require('../../reasoning-modules/defi/index');

function orchestrate(query, knowledgeGraph) {
  // Mocked logic: all queries go to DeFi RM
  const defiRM = new DeFiReasoningModule();
  const result = defiRM.run(query, knowledgeGraph);
  return result;
}

module.exports = { orchestrate };
