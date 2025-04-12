// graph.js
const graph = {
    nodes: [],
    edges: []
  };
  
  function addTriple(subject, relation, object) {
    graph.nodes.push(subject, object);
    graph.edges.push({ from: subject, to: object, relation });
  }
  
  function queryGraph(entity) {
    return graph.edges.filter(e => e.from === entity || e.to === entity);
  }
  
  module.exports = { graph, addTriple, queryGraph };
  