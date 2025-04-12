class ReasoningModule {
    constructor(name) {
      this.name = name;
    }
  
    run(subquery, knowledgeGraph) {
      throw new Error("run() not implemented");
    }
  }
  
  module.exports = ReasoningModule;
  