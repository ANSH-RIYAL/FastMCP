import pandas as pd
from collections import Counter

class SurveyAnalyzerTools:
    def extract_themes(self, responses: list) -> dict:
        """
        Extract common themes from survey responses (simple keyword frequency).
        """
        keywords = ['usability', 'performance', 'price', 'support']
        found = []
        for response in responses:
            for kw in keywords:
                if kw in response.lower():
                    found.append(kw)
        theme_counts = Counter(found)
        themes = [theme for theme, count in theme_counts.most_common()]
        return {'themes': themes}

    def compute_frequencies(self, data: pd.DataFrame) -> dict:
        """
        Compute response frequencies and confidence intervals (basic stats).
        """
        if 'satisfaction' in data.columns:
            satisfied = data['satisfaction'].sum()
            total = len(data)
            rate = satisfied / total if total else 0
            # 95% CI for proportion
            import math
            ci = 1.96 * ((rate * (1 - rate)) / total) ** 0.5 if total else 0
            return {'satisfaction_rate': round(rate, 2), 'ci': round(ci, 2)}
        return {'satisfaction_rate': None, 'ci': None}

    def generate_summary_report(self, insights: dict) -> dict:
        """
        Generate a summary report from insights.
        """
        report = f"Survey Summary:\nThemes: {insights.get('themes', [])}\nSatisfaction Rate: {insights.get('satisfaction_rate', 'N/A')}"
        return {'report': report} 