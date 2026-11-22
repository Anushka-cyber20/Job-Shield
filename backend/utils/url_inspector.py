"""
Deep URL & Job Portal Inspector for JobShield.
Analyzes domain reputation, detects typosquatting, shorteners, and scrapes job page content.
"""

import re
import urllib.parse
from typing import Dict, Any, List
import requests
from bs4 import BeautifulSoup

KNOWN_SHORTENERS = [
    "bit.ly", "tinyurl.com", "rb.gy", "cutt.ly", "is.gd", "t.co", "ow.ly", "shorturl.at"
]

GENERIC_FORM_PROVIDERS = [
    "forms.gle", "docs.google.com", "formsite.com", "typeform.com", "jotform.com"
]

BRAND_KEYWORDS = [
    "google", "amazon", "microsoft", "tcs", "infosys", "wipro", "deloitte",
    "accenture", "apple", "meta", "netflix", "ibm", "cognizant"
]

SUSPICIOUS_TLDS = [
    ".xyz", ".top", ".click", ".work", ".monster", ".fit", ".rest",
    ".buzz", ".loan", ".racing", ".online", ".surf", ".site", ".ru", ".cn"
]

def inspect_url(raw_url: str) -> Dict[str, Any]:
    """
    Inspects domain authenticity, detects phishing signals, and retrieves page text if possible.
    """
    cleaned_url = raw_url.strip()
    if not cleaned_url.startswith(("http://", "https://")):
        cleaned_url = "https://" + cleaned_url

    parsed = urllib.parse.urlparse(cleaned_url)
    hostname = (parsed.hostname or "").lower()
    
    url_flags: List[Dict[str, str]] = []
    is_shortener = any(short in hostname for short in KNOWN_SHORTENERS)
    is_form_host = any(form in hostname or form in parsed.path for form in GENERIC_FORM_PROVIDERS)
    
    # 1. Shortener Check
    if is_shortener:
        url_flags.append({
            "type": "Shortened / Obfuscated Link",
            "severity": "MEDIUM",
            "detail": f"Domain '{hostname}' is a URL shortening service. Scammers often use shorteners to mask final phishing destinations."
        })

    # 2. Form Provider Check
    if is_form_host:
        url_flags.append({
            "type": "Third-Party / Unofficial Form Application",
            "severity": "MEDIUM",
            "detail": "Application is hosted on an unauthenticated free form provider (Google Forms/Typeform) rather than an official ATS (Workday, Greenhouse, Lever)."
        })

    # 3. Suspicious TLD Check
    has_bad_tld = False
    for tld in SUSPICIOUS_TLDS:
        if hostname.endswith(tld):
            has_bad_tld = True
            url_flags.append({
                "type": f"High-Risk Phishing TLD ({tld})",
                "severity": "HIGH",
                "detail": f"The domain uses the '{tld}' top-level domain, commonly leveraged in fast-flux phishing campaigns."
            })
            break

    # 4. Brand Typosquatting / Impersonation Check
    # e.g., 'careers-google-verify.com' or 'tcs-hiring-portal.net'
    for brand in BRAND_KEYWORDS:
        if brand in hostname:
            official_domains = [f"{brand}.com", f"{brand}.in", f"{brand}.org", f"{brand}.co"]
            if not any(hostname == off or hostname.endswith("." + off) for off in official_domains):
                url_flags.append({
                    "type": f"Brand Typosquatting / Spoofing ({brand.upper()})",
                    "severity": "CRITICAL",
                    "detail": f"Hostname '{hostname}' contains '{brand}', but does not belong to the authentic corporate domain hierarchy."
                })

    # 5. Page Content Extraction (Safely with timeout)
    page_text = ""
    page_title = ""
    fetch_success = False
    status_code = None

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 JobShield-Audit"
        }
        resp = requests.get(cleaned_url, headers=headers, timeout=5, allow_redirects=True)
        status_code = resp.status_code
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Remove scripts & styles
            for elem in soup(["script", "style", "noscript", "svg"]):
                elem.extract()
            
            page_title = soup.title.string.strip() if soup.title and soup.title.string else ""
            raw_text = soup.get_text(separator=" ", strip=True)
            # Normalize whitespace
            page_text = re.sub(r"\s+", " ", raw_text)[:3000] # limit 3000 chars for analysis
            fetch_success = True
    except Exception as e:
        fetch_error = str(e)
    
    return {
        "url": cleaned_url,
        "hostname": hostname,
        "is_shortener": is_shortener,
        "is_form_host": is_form_host,
        "url_flags": url_flags,
        "fetch_success": fetch_success,
        "status_code": status_code,
        "extracted_title": page_title,
        "extracted_text": page_text
    }
