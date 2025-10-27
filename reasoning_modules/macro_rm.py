from reasoning_modules.base.module import ReasoningModule
import datetime
import pandas as pd
import os

class MacroReasoningModule(ReasoningModule):
    def __init__(self, data_path='reasoning_modules/data/macro_data.csv'):
        super().__init__('macro')
        self.data_path = data_path
        self.sources = {
            "local_data_file": "Local Macroeconomic Data CSV",
        }

    def run(self, subquery, knowledgeGraph):
        """Analyzes macroeconomic data from a local CSV file."""
        if not os.path.exists(self.data_path):
            return self._error_response("Data file not found.")

        try:
            df = pd.read_csv(self.data_path)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values(by='Date', ascending=False)
        except Exception as e:
            return self._error_response(f"Failed to parse data file: {e}")

        if len(df) < 2:
            return self._error_response("Insufficient data for trend analysis.")

        # Get the two most recent data points
        latest = df.iloc[0]
        previous = df.iloc[1]

        # Perform simple trend analysis
        reasoning_steps = []
        interest_rate_trend = latest['InterestRate'] - previous['InterestRate']
        inflation_trend = latest['InflationRate'] - previous['InflationRate']

        # Step 1: Analyze Interest Rates
        if interest_rate_trend > 0:
            ir_inference = "Monetary policy is tightening."
        elif interest_rate_trend < 0:
            ir_inference = "Monetary policy is loosening."
        else:
            ir_inference = "Monetary policy is holding steady."
        reasoning_steps.append({
            "step": "Analyze interest rate trends",
            "data": f"Latest interest rate is {latest['InterestRate']:.2f}%, change of {interest_rate_trend:.2f} from previous quarter.",
            "source": self.sources["local_data_file"],
            "inference": ir_inference
        })

        # Step 2: Analyze Inflation
        if inflation_trend > 0:
            inf_inference = "Inflationary pressures are increasing."
        elif inflation_trend < 0:
            inf_inference = "Inflationary pressures are decreasing."
        else:
            inf_inference = "Inflation is stable."
        reasoning_steps.append({
            "step": "Assess inflation indicators",
            "data": f"Latest inflation rate is {latest['InflationRate']:.2f}%, change of {inflation_trend:.2f} from previous quarter.",
            "source": self.sources["local_data_file"],
            "inference": inf_inference
        })

        conclusion = self._synthesize_conclusion(ir_inference, inf_inference)

        return {
            "subquery": subquery,
            "timestamp": datetime.datetime.now().isoformat(),
            "reasoningPath": reasoning_steps,
            "sources": self.sources,
            "conclusion": conclusion,
            "confidence": 0.90,
            "relevantMetrics": {
                "latest_interest_rate": latest['InterestRate'],
                "interest_rate_trend": interest_rate_trend,
                "latest_inflation_rate": latest['InflationRate'],
                "inflation_trend": inflation_trend
            }
        }

    def _synthesize_conclusion(self, ir_inference, inf_inference):
        return f"Macroeconomic analysis suggests: {ir_inference} {inf_inference}"

    def _error_response(self, error_message):
        return {
            "subquery": "",
            "timestamp": datetime.datetime.now().isoformat(),
            "reasoningPath": [],
            "sources": self.sources,
            "conclusion": f"Error in MacroReasoningModule: {error_message}",
            "confidence": 0.0,
            "relevantMetrics": {}
        }