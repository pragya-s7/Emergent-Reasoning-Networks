import datetime
from typing import Dict, Any, List, Optional

class ReasoningModule:
    """
    Base class for all reasoning modules in the Kairos system.
    
    Reasoning modules are specialized AI agents that process sub-queries
    and return structured reasoning steps with sources and conclusions.
    """
    
    def __init__(self, name: str):
        """
        Initialize a reasoning module.
        
        Args:
            name: Unique identifier for this reasoning module
        """
        self.name = name
        self.sources = {}  # Default empty sources dictionary
    
    def run(self, subquery: str, knowledgeGraph: Any) -> Dict[str, Any]:
        """
        Execute the reasoning process on a subquery using the knowledge graph.
        
        Args:
            subquery: The specific question or task for this module
            knowledgeGraph: The knowledge graph containing relevant facts
            
        Returns:
            A dictionary containing the reasoning path, conclusion, and metadata
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("run() not implemented")
    
    def format_output(self, subquery: str, reasoning_steps: List[Dict[str, Any]], 
                     conclusion: str, confidence: float = 0.5,
                     relevant_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format the module output in a standardized way.
        
        Args:
            subquery: The original subquery
            reasoning_steps: List of reasoning step dictionaries
            conclusion: The final conclusion
            confidence: Confidence score (0.0 to 1.0)
            relevant_metrics: Optional metrics relevant to this reasoning
            
        Returns:
            Standardized output dictionary
        """
        return {
            "module": self.name,
            "subquery": subquery,
            "timestamp": datetime.datetime.now().isoformat(),
            "reasoningPath": reasoning_steps,
            "sources": self.sources,
            "conclusion": conclusion,
            "confidence": confidence,
            "relevantMetrics": relevant_metrics or {}
        }
    
    def validate_reasoning_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate that reasoning steps have the required fields.
        
        Args:
            steps: List of reasoning step dictionaries
            
        Returns:
            Validated and possibly fixed reasoning steps
        """
        validated_steps = []
        for i, step in enumerate(steps):
            validated_step = {
                "step": step.get("step", f"Step {i+1}"),
                "data": step.get("data", ""),
                "source": step.get("source", "Unknown"),
                "inference": step.get("inference", "")
            }
            validated_steps.append(validated_step)
        return validated_steps