"""
Explainable AI (XAI) & Text Highlight Module for JobShield.
Deconstructs job listing text, computes token-level attribution weights,
and produces explainable HTML/offset highlights for transparency.
"""

import re
from typing import List, Dict, Any

RISK_KEYWORDS_EXPLAIN = [
    # Critical Red Flags
    (r"\b(security deposit|laptop deposit|courier insurance|equipment fee)\b", "high", "Advance-Fee Extortion: Demanding money for hardware or courier is prohibited in legitimate hiring."),
    (r"\b(registration fee|processing fee|verification charges?|id card fee)\b", "high", "Upfront Fee: Legitimate companies absorb all onboarding and vetting costs."),
    (r"\b(cashier'?s?\s*check|deposit the check|wire transfer|western union|zelle|cashapp)\b", "high", "Financial Scam: Counterfeit check overpayment or untraceable wire fraud."),
    (r"\b(telegram|t\.me/|wa\.me/|@\w{4,20}bot)\b", "high", "Off-Platform Evasion: Directing candidates to anonymous messaging apps to prevent auditing."),
    (r"\b(usdt|crypto|bitcoin atm|trc20|liquidity pool)\b", "high", "Crypto Fraud: Digital assets are used to execute irreversible, unregulated transactions."),
    (r"\b(direct selection|without (any )?interview|guaranteed selection)\b", "high", "Deceptive Bait: Promising immediate employment without technical evaluation or interview."),
    (r"\b(watch(ing)? videos|liking? youtube|rate google apps|micro-tasks)\b", "high", "Task Fraud: Common cybercrime scam scheme targeting students with small initial tasks."),
    
    # Medium Red Flags
    (r"\b(urgent hiring|immediate joining bonus|limited slots|within \d+ hours)\b", "medium", "Urgency Manipulation: Pressure tactic designed to prevent candidate due diligence."),
    (r"\b(housewives|anyone can do|zero experience needed|no qualification)\b", "medium", "Vague Scope: Lack of specific technical or educational qualifications is typical of bulk scam campaigns."),
    (r"\b(earn (inr|\$|rs\.?)\s*\d+([,.]\d+)?\s*(daily|per day))\b", "medium", "Exaggerated Earnings: Unrealistic daily payouts designed to entice financially vulnerable students."),
    (r"\b(mandatory \d+[- ]years? bond|penalty of (inr|\$)\s*\d+)\b", "medium", "Exploitative Terms: Excessive contractual penalties or bond terms."),

    # Positive / Trust Indicators
    (r"\b(equal opportunity employer|affirmative action|401\(k\)|medical insurance)\b", "trust", "Standard Corporate Benefit: Authentic compliance with employment regulations."),
    (r"\b(code reviews?|git|version control|docker|microservices|restful api)\b", "trust", "Technical Depth: Specific engineering stack and verifiable workflows."),
    (r"\b(strictly never charges|no recruitment fee|official careers portal)\b", "trust", "Anti-Fraud Advisory: Explicit disclosure alerting candidates against unauthorized fees.")
]

class ExplainabilityEngine:
    def __init__(self):
        pass

    def explain_text(self, text: str) -> Dict[str, Any]:
        """
        Identify high/medium risk and trust phrases, and generate an annotated representation.
        """
        spans: List[Dict[str, Any]] = []
        lowered = text.lower()
        
        for pattern, risk_level, reason in RISK_KEYWORDS_EXPLAIN:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                spans.append({
                    "start": match.start(),
                    "end": match.end(),
                    "text": match.group(0),
                    "risk_level": risk_level,
                    "reason": reason
                })

        # Sort spans by starting index
        spans.sort(key=lambda x: x["start"])

        # Filter overlapping spans
        filtered_spans = []
        last_end = -1
        for s in spans:
            if s["start"] >= last_end:
                filtered_spans.append(s)
                last_end = s["end"]

        # Build formatted HTML representation
        html_parts = []
        current_idx = 0
        for s in filtered_spans:
            # Append preceding clean text
            if s["start"] > current_idx:
                html_parts.append(text[current_idx:s["start"]])
            
            # Append highlighted span
            badge_class = "highlight-high" if s["risk_level"] == "high" else ("highlight-med" if s["risk_level"] == "medium" else "highlight-trust")
            snippet = text[s["start"]:s["end"]]
            html_parts.append(f'<mark class="{badge_class}" title="{s["reason"]}" data-risk="{s["risk_level"]}">{snippet}</mark>')
            current_idx = s["end"]

        if current_idx < len(text):
            html_parts.append(text[current_idx:])

        highlighted_html = "".join(html_parts)

        # Feature contribution summary
        high_risk_count = sum(1 for s in filtered_spans if s["risk_level"] == "high")
        med_risk_count = sum(1 for s in filtered_spans if s["risk_level"] == "medium")
        trust_count = sum(1 for s in filtered_spans if s["risk_level"] == "trust")

        return {
            "annotated_html": highlighted_html,
            "spans": filtered_spans,
            "metrics": {
                "high_risk_phrases_found": high_risk_count,
                "medium_risk_phrases_found": med_risk_count,
                "trust_signals_found": trust_count
            }
        }
