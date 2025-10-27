from reasoning_modules.base.module import ReasoningModule
import datetime
import json
import os

class CorporateCommunicationsReasoningModule(ReasoningModule):
    def __init__(self, data_path='reasoning_modules/data/corporate_comms.json'):
        super().__init__('corporate-communications')
        self.data_path = data_path
        self.sources = {
            "local_comms_file": "Local Corporate Communications JSON",
        }

    def run(self, subquery, knowledgeGraph):
        """Analyzes corporate communications from a local JSON file."""
        if not os.path.exists(self.data_path):
            return self._error_response("Data file not found.")

        try:
            with open(self.data_path, 'r') as f:
                all_announcements = json.load(f).get('announcements', [])
        except Exception as e:
            return self._error_response(f"Failed to parse data file: {e}")

        # Find the project name in the subquery (simple keyword matching)
        project_name = self._find_project_in_query(subquery, knowledgeGraph)

        if not project_name:
            return self._error_response("Could not identify a project in the query.")

        project_announcements = [ann for ann in all_announcements if ann.get('project', '').lower() == project_name.lower()]

        if not project_announcements:
            return self._error_response(f"No announcements found for project: {project_name}")

        reasoning_steps = []
        sentiments = []
        for ann in project_announcements:
            reasoning_steps.append({
                "step": f"Analyzed Announcement: {ann['title']}",
                "data": ann['content'],
                "source": self.sources["local_comms_file"],
                "inference": f"The announcement has a '{ann['sentiment']}' sentiment."
            })
            sentiments.append(ann['sentiment'])

        conclusion = self._synthesize_conclusion(project_name, sentiments)
        avg_sentiment = self._calculate_avg_sentiment(sentiments)

        return {
            "subquery": subquery,
            "timestamp": datetime.datetime.now().isoformat(),
            "reasoningPath": reasoning_steps,
            "sources": self.sources,
            "conclusion": conclusion,
            "confidence": 0.88,
            "relevantMetrics": {
                "announcements_analyzed": len(project_announcements),
                "average_sentiment_score": avg_sentiment
            }
        }

    def _find_project_in_query(self, subquery, knowledgeGraph):
        """A simple method to find a project name in the query."""
        # Look for known projects from the KG in the query text
        for entity in knowledgeGraph.entities.values():
            if entity.type == 'Project' and entity.label.lower() in subquery.lower():
                return entity.label
        # Fallback for simple cases
        words = subquery.split()
        for i, word in enumerate(words):
            if word.lower() == 'project' and i + 1 < len(words):
                return words[i+1]
        return None

    def _calculate_avg_sentiment(self, sentiments):
        score = 0
        for s in sentiments:
            if s == 'positive': score += 1
            if s == 'negative': score -= 1
        return score / len(sentiments) if sentiments else 0

    def _synthesize_conclusion(self, project_name, sentiments):
        positive_count = sentiments.count('positive')
        negative_count = sentiments.count('negative')
        neutral_count = sentiments.count('neutral')
        return f"Analysis of {len(sentiments)} announcements for '{project_name}' shows: {positive_count} positive, {neutral_count} neutral, and {negative_count} negative communications."

    def _error_response(self, error_message):
        return {
            "subquery": "",
            "timestamp": datetime.datetime.now().isoformat(),
            "reasoningPath": [],
            "sources": self.sources,
            "conclusion": f"Error in CorporateCommunicationsReasoningModule: {error_message}",
            "confidence": 0.0,
            "relevantMetrics": {}
        }