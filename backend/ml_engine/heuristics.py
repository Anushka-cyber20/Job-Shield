"""
Deterministic Security & Domain Intelligence Engine for JobShield.
Performs pattern matching, recruiter email verification, financial trap detection,
and linguistic threat scoring.
"""

import re
from typing import Dict, List, Any, Optional

WELL_KNOWN_TECH_FIRMS = [
    "google", "amazon", "microsoft", "apple", "meta", "facebook", "netflix",
    "tcs", "tata consultancy", "infosys", "wipro", "cognizant", "accenture",
    "deloitte", "ibm", "capgemini", "hcl", "tech mahindra", "ey", "kpmg",
    "pwc", "goldman sachs", "jpmorgan", "morgan stanley", "stripe", "uber",
    "adobe", "cisco", "oracle", "salesforce", "intel", "nvidia"
]

FREE_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com",
    "zoho.com", "yandex.com", "mail.com", "proton.me", "protonmail.com",
    "icloud.com", "gmx.com", "aol.com"
]

SUSPICIOUS_TLDS = [
    ".top", ".xyz", ".click", ".work", ".monster", ".fit", ".rest",
    ".buzz", ".loan", ".racing", ".online", ".surf", ".site", ".ru", ".cn"
]

FINANCIAL_TRAP_PATTERNS = [
    (r"(refundable|mandatory|compulsory)?\s*(security|laptop|equipment|insurance)\s*(deposit|fee|charge|amount)", "Security Deposit Extortion", "HIGH"),
    (r"(registration|processing|verification|onboarding|id card|badge)\s*(fee|charges?|cost|payment|amount)", "Upfront Registration / Verification Fee", "HIGH"),
    (r"(training|certification|compliance kit)\s*(fee|charge|cost|worth|purchase)", "Pay-for-Training Scam Trap", "HIGH"),
    (r"(cashier'?s?\s*check|deposit\s*(the|this|our)\s*che?ck|wire\s*the\s*rest|buy\s*supplies\s*from\s*vendor)", "Fake Cheque / Overpayment Fraud", "HIGH"),
    (r"(usdt|crypto|trc20|erc20|bitcoin atm|binance|liquidity pool)", "Cryptocurrency / Unregulated Asset Transaction", "HIGH"),
    (r"(western union|moneygram|zelle|cashapp|venmo|gift card)", "Untraceable Money Transfer Demanded", "HIGH"),
    (r"(upi\s*(id|handle|transfer|payment)?\s*[:=-]?\s*[\w.-]+@[\w.-]+)", "Direct Personal UPI Payment Solicitation", "HIGH"),
]

CHANNEL_TRAP_PATTERNS = [
    (r"(telegram|t\.me/|@[\w_]{4,30}\s*(bot|hr|team|recruitment|job))", "Off-Platform Telegram Redirection", "HIGH"),
    (r"(wa\.me/|api\.whatsapp\.com|whatsapp\s*(only|number|group|hr))", "Off-Platform WhatsApp Recruiter Routing", "MEDIUM"),
    (r"(do not call|strictly text|no phone calls|only chat)", "Refusal of Direct Telephonic / Video Verification", "MEDIUM"),
    (r"(bit\.ly|tinyurl\.com|is\.gd|cutt\.ly|rb\.gy)/[\w-]+", "Obfuscated / Shortened Link in Recruitment Notice", "MEDIUM"),
]

LINGUISTIC_TRAP_PATTERNS = [
    (r"(direct selection|selected directly|direct appointment|without (any )?(interview|test|screening))", "Guaranteed Direct Selection Without Assessment", "HIGH"),
    (r"(urgent hiring|immediate joining bonus|limited slots remaining|apply within \d+ hours)", "High-Pressure Urgency & Scarcity Tactic", "MEDIUM"),
    (r"(watch(ing)? videos|liking? (youtube|tiktok|reels)|rating? apps?|google reviews?|typing without test)", "Micro-Task / Video Liking Scam Signature", "HIGH"),
    (r"(earn (inr|\$|rs\.?)\s*\d+([,.]\d+)?\s*(daily|per day|hourly|per hour|each day))", "Unrealistic Daily Guaranteed Payout", "HIGH"),
    (r"(housewives|college students|anyone can do|zero experience needed|no qualification)", "Vague / Overly Broad Eligibility Trap", "LOW"),
    (r"(surrender original (documents|certificates|degrees)|submit passbook|aadhaar front and back)", "Identity Document / Financial Theft Solicitation", "HIGH"),
    (r"(mandatory \d+[- ]years? bond|penalty of (inr|\$)\s*\d+)", "Exploitative Service Bond Penalty", "HIGH")
]

class HeuristicsEngine:
    def __init__(self):
        pass

    def evaluate(self, title: str, company: str, description: str, 
                 salary: str = "", contact_email: str = "", portal_url: str = "") -> Dict[str, Any]:
        text_full = f"{title} {company} {description} {salary} {contact_email} {portal_url}".lower()
        flags: List[Dict[str, Any]] = []
        
        financial_score = 0
        contact_score = 0
        linguistic_score = 0
        company_score = 0
        salary_score = 0

        # 1. Company Impersonation with Free Email Check
        norm_company = company.lower().strip()
        norm_email = contact_email.lower().strip()
        
        is_known_firm = any(firm in norm_company for firm in WELL_KNOWN_TECH_FIRMS)
        email_domain = norm_email.split("@")[-1] if "@" in norm_email else ""
        is_free_email = email_domain in FREE_EMAIL_DOMAINS

        if is_known_firm and is_free_email:
            flags.append({
                "rule": "Major Enterprise Impersonation (Free Email)",
                "category": "Company Legitimacy",
                "severity": "CRITICAL",
                "detail": f"Claims to represent prominent firm '{company}', but uses free webmail domain '@{email_domain}'. Legitimate corporate recruiters use official corporate domains.",
                "penalty": 40
            })
            company_score += 40
        elif is_free_email and norm_email:
            flags.append({
                "rule": "Free Webmail Recruiter Address",
                "category": "Company Legitimacy",
                "severity": "MEDIUM",
                "detail": f"Recruiter contact '{contact_email}' is hosted on a free public provider (@{email_domain}) rather than an authenticated organization domain.",
                "penalty": 15
            })
            company_score += 15

        # 2. Suspicious TLD / Phishing Check
        for tld in SUSPICIOUS_TLDS:
            if tld in portal_url.lower() or tld in email_domain:
                flags.append({
                    "rule": f"High-Risk Top-Level Domain ({tld})",
                    "category": "Company Legitimacy",
                    "severity": "HIGH",
                    "detail": f"The domain uses '{tld}', an extension frequently associated with disposable phishing campaigns and unregulated job scams.",
                    "penalty": 20
                })
                company_score += 20
                break

        # 3. Financial Traps & Advance Fees
        for pattern, rule_name, severity in FINANCIAL_TRAP_PATTERNS:
            matches = list(re.finditer(pattern, text_full, re.IGNORECASE))
            if matches:
                penalty = 30 if severity == "HIGH" else 15
                financial_score += penalty
                snippet = matches[0].group(0)
                flags.append({
                    "rule": rule_name,
                    "category": "Financial Risk",
                    "severity": severity,
                    "detail": f"Detected upfront payment request or suspicious transaction phrase: '{snippet}'. Legitimate employers never charge candidates for equipment, registration, or onboarding.",
                    "matched_text": snippet,
                    "penalty": penalty
                })

        # 4. Off-Platform Channel Traps
        for pattern, rule_name, severity in CHANNEL_TRAP_PATTERNS:
            matches = list(re.finditer(pattern, text_full, re.IGNORECASE))
            if matches:
                penalty = 25 if severity == "HIGH" else 12
                contact_score += penalty
                snippet = matches[0].group(0)
                flags.append({
                    "rule": rule_name,
                    "category": "Contact Risk",
                    "severity": severity,
                    "detail": f"Redirects candidates off legitimate hiring channels: '{snippet}'. Scammers use encrypted messengers (Telegram/WhatsApp) to evade platform moderation and paper trails.",
                    "matched_text": snippet,
                    "penalty": penalty
                })

        # 5. Linguistic Threats & Urgency
        for pattern, rule_name, severity in LINGUISTIC_TRAP_PATTERNS:
            matches = list(re.finditer(pattern, text_full, re.IGNORECASE))
            if matches:
                penalty = 20 if severity == "HIGH" else (10 if severity == "MEDIUM" else 5)
                linguistic_score += penalty
                snippet = matches[0].group(0)
                flags.append({
                    "rule": rule_name,
                    "category": "Linguistic & Psychological",
                    "severity": severity,
                    "detail": f"Employs coercive or deceptive psychological framing: '{snippet}'.",
                    "matched_text": snippet,
                    "penalty": penalty
                })

        # 6. Salary Anomaly Scoring
        norm_sal = f"{salary} {description}".lower()
        if re.search(r"(\$|usd|inr|rs\.?)\s*(1000|2000|3000|5000|10000)\s*(daily|day|each day)", norm_sal) or \
           re.search(r"(\b500\b|\b1000\b|\b2000\b|\b3000\b)\s*usdt", norm_sal) or \
           re.search(r"(40|50|60|70|80|90|100)\s*lpa.*(intern|fresher|data entry)", norm_sal):
            flags.append({
                "rule": "Statistically Aberrant Salary / Stipend",
                "category": "Salary Anomaly",
                "severity": "HIGH",
                "detail": "Promised compensation deviates drastically from industry standard for entry-level / intern roles. Unusually inflated pay is the most common bait used in deceptive job offers.",
                "penalty": 25
            })
            salary_score += 25

        # Normalize component scores to [0, 100]
        financial_risk = min(100, financial_score)
        contact_risk = min(100, contact_score)
        linguistic_risk = min(100, linguistic_score)
        company_risk = min(100, company_score)
        salary_risk = min(100, salary_score)

        # Weighted aggregate heuristic fraud probability
        composite_heuristic_score = min(100, int(
            financial_risk * 0.35 +
            contact_risk * 0.25 +
            company_risk * 0.20 +
            linguistic_risk * 0.12 +
            salary_risk * 0.08
        ))

        return {
            "composite_score": composite_heuristic_score,
            "financial_risk": financial_risk,
            "contact_risk": contact_risk,
            "linguistic_risk": linguistic_risk,
            "company_risk": company_risk,
            "salary_risk": salary_risk,
            "flags": flags
        }
