"""
EMSCAD & Real-World Synthetic Benchmark Dataset Generator for JobShield.
Generates comprehensive training and evaluation data reflecting modern job & internship scams:
- Advance-fee / Security deposit scams
- Telegram & WhatsApp task fraud (YouTube like / review scams)
- Fake remote data entry / part-time typing scams
- Impersonation of major tech firms (Google, Amazon, TCS, Deloitte, etc.)
- Phishing & identity theft traps
- Fake cheque / equipment reimbursement scams
- Legitimate tech internships, corporate graduate programs, and startup roles
"""

import random
import pandas as pd
from typing import List, Dict

LEGITIMATE_TEMPLATES = [
    {
        "title": "Software Engineering Intern",
        "company": "Stripe",
        "email_domain": "stripe.com",
        "desc": (
            "We are looking for passionate Software Engineering Interns to join our Infrastructure and Payments team. "
            "You will work closely with senior engineers to design, build, and deploy reliable distributed systems. "
            "Responsibilities include writing clean Python/Go/Java code, building RESTful APIs, participating in code reviews, "
            "and testing scalable microservices. Qualifications: Currently pursuing a BS/MS in Computer Science or related STEM field. "
            "Strong fundamentals in Data Structures, Algorithms, and Object-Oriented Programming. Prior project experience in Git, Docker, "
            "and relational databases (PostgreSQL/MySQL) is an advantage. Competitive monthly stipend provided with mentor guidance."
        ),
        "telecommuting": 0,
        "salary": "$45 - $55 per hour",
    },
    {
        "title": "Data Science & ML Intern",
        "company": "Amazon Web Services",
        "email_domain": "amazon.jobs",
        "desc": (
            "Amazon is seeking a Data Science Intern to collaborate with our applied science teams on machine learning solutions. "
            "You will analyze complex datasets, build statistical models, and prototype predictive algorithms using Scikit-Learn, PyTorch, "
            "and AWS SageMaker. Basic qualifications: enrolled in an accredited degree program in CS, Statistics, or Math. Proficiency in "
            "Python and SQL is required. Experience with data wrangling using Pandas and NumPy. You will present your final project to engineering "
            "leadership at the conclusion of the 12-week internship."
        ),
        "telecommuting": 0,
        "salary": "$50 - $60 per hour",
    },
    {
        "title": "Frontend Developer Intern (React/TypeScript)",
        "company": "Vercel",
        "email_domain": "vercel.com",
        "desc": (
            "Join our design engineering team at Vercel. We are seeking a creative Frontend Intern proficient in Next.js, React, "
            "and modern CSS frameworks. In this role, you will implement accessible UI components, optimize web vitals performance, "
            "and collaborate with product designers via Figma. Candidates must demonstrate a public GitHub portfolio or deployed web projects. "
            "Strong grasp of asynchronous JavaScript, browser APIs, and component lifecycle is required."
        ),
        "telecommuting": 1,
        "salary": "$35 - $45 per hour",
    },
    {
        "title": "Graduate Trainee Engineer - 2026 Batch",
        "company": "Tata Consultancy Services (TCS)",
        "email_domain": "tcs.com",
        "desc": (
            "Tata Consultancy Services invites applications from B.E./B.Tech/MCA/M.Sc graduates for the TCS National Qualifier Test (NQT) drive. "
            "Selected candidates will undergo comprehensive training at TCS learning centers in Cloud Computing, Java Enterprise, and DevOps. "
            "Eligibility: Minimum 60% aggregate throughout 10th, 12th, and Degree without active backlogs. Note: TCS strictly never charges "
            "any recruitment fee, examination fee, or security deposit at any stage of hiring. All official communications occur via @tcs.com domain."
        ),
        "telecommuting": 0,
        "salary": "INR 3.6 - 7.0 LPA",
    },
    {
        "title": "Cybersecurity Analyst Intern",
        "company": "CrowdStrike",
        "email_domain": "crowdstrike.com",
        "desc": (
            "CrowdStrike is looking for an enthusiastic Cybersecurity Intern for our threat intelligence unit. "
            "You will assist security operations analysts with log triaging, vulnerability assessments, and SIEM monitoring. "
            "Requirements: Foundational knowledge of TCP/IP networking, Linux terminal navigation, and common web vulnerabilities (OWASP Top 10). "
            "Hands-on experience with tools like Wireshark, Nmap, or Burp Suite is desirable. Must possess strong analytical skills and ethics."
        ),
        "telecommuting": 0,
        "salary": "$38 - $48 per hour",
    },
    {
        "title": "Marketing & Social Media Intern",
        "company": "Canva",
        "email_domain": "canva.com",
        "desc": (
            "We are looking for a creative Content & Social Media Intern to support Canva's regional student ambassador program. "
            "You will brainstorm social media campaigns, analyze engagement metrics using Google Analytics, and draft compelling copy "
            "for LinkedIn, Instagram, and Twitter. Candidate should have excellent written communication skills, keen visual aesthetics, "
            "and familiarity with Canva's design suite."
        ),
        "telecommuting": 1,
        "salary": "$25 - $32 per hour",
    },
    {
        "title": "Backend Engineering Trainee",
        "company": "Infosys Limited",
        "email_domain": "infosys.com",
        "desc": (
            "Infosys is hiring enthusiastic computer science freshers for our Global Internship Program. "
            "Selected interns will be trained on Spring Boot, Microservices, and cloud deployments on Azure. "
            "Assessment includes an online coding round followed by technical interviews. Official registration is conducted exclusively "
            "through the Infosys Springboard portal. No third-party agents or fees are authorized."
        ),
        "telecommuting": 0,
        "salary": "INR 4.0 - 6.5 LPA",
    },
    {
        "title": "UI/UX Product Design Intern",
        "company": "Figma",
        "email_domain": "figma.com",
        "desc": (
            "Figma is searching for an ambitious Product Design Intern to help craft intuitive collaborative experiences. "
            "You will conduct user interviews, build wireframes, prototype high-fidelity workflows, and test usability with real customers. "
            "Requirements: Portfolio demonstrating case studies from concept to final prototypes. Empathy for users, typography knowledge, "
            "and familiarity with design tokens."
        ),
        "telecommuting": 1,
        "salary": "$42 - $52 per hour",
    },
    {
        "title": "Junior QA Automation Engineer",
        "company": "Atlassian",
        "email_domain": "atlassian.com",
        "desc": (
            "Join Atlassian's Quality Engineering team. You will write automated end-to-end tests using Cypress and Playwright, "
            "collaborate with developers to establish CI/CD quality gates in Bitbucket Pipelines, and identify regression bugs. "
            "Qualifications: BS in Engineering or equivalent practical experience. Solid programming foundation in Python or JavaScript."
        ),
        "telecommuting": 1,
        "salary": "$40 - $50 per hour",
    },
    {
        "title": "DevOps & Cloud Intern",
        "company": "Datadog",
        "email_domain": "datadoghq.com",
        "desc": (
            "We are seeking a Cloud Infrastructure Intern to help maintain our Kubernetes clusters and monitoring pipelines. "
            "Work with Terraform, Helm, Linux server administration, and Prometheus alerting. Strong shell scripting abilities "
            "and curiosity for system performance and observability required."
        ),
        "telecommuting": 0,
        "salary": "$45 - $55 per hour",
    }
]

SCAM_TEMPLATES = [
    {
        "title": "Online Part-time Assistant / YouTube Video Reviewer",
        "company": "Global Media Promotion Ltd",
        "email_domain": "gmail.com",
        "desc": (
            "URGENT HIRING! Work from home part time. Earn INR 2,000 to 5,000 daily by simply watching videos, liking YouTube posts, "
            "and rating products on Google. No skills or prior experience needed! Suitable for college students, housewives, and freshers. "
            "Immediate joining bonus of INR 500 given upon onboarding. Send message on Telegram @JobManagerHR or WhatsApp +91-9876543210 "
            "to start receiving tasks today. Guaranteed daily instant payout to your UPI/Paytm wallet."
        ),
        "telecommuting": 1,
        "salary": "INR 5,000 daily guaranteed",
    },
    {
        "title": "Data Entry Specialist / Home Typist",
        "company": "Apex Global Solutions Inc",
        "email_domain": "yahoo.com",
        "desc": (
            "Immediate vacancy for Remote Data Entry Typist. Earn $45 to $75 per hour typing simple MS Word documents from home. "
            "Flexible hours: work just 1 to 2 hours per day. We provide company laptop and typing material upon receipt of a mandatory "
            "refundable security deposit of $150 (INR 2,500) for courier dispatch insurance. The deposit is 100% refundable with your first paycheck. "
            "Contact our HR coordinator immediately via Telegram: @ApexRecruitmentBot. Limited seats remaining, apply now!"
        ),
        "telecommuting": 1,
        "salary": "$45 - $75 per hour ($12,000/month)",
    },
    {
        "title": "Google Cloud Support Intern (Direct Selection)",
        "company": "Google LLC (India Hiring Branch)",
        "email_domain": "careers-google-recruitment@gmail.com",
        "desc": (
            "Congratulations! Your profile has been shortlisted directly for Google Cloud Technical Intern role without any interview! "
            "Package: INR 12 Lakhs per annum + free MacBook Pro. To confirm your employment slot and issue the official offer letter, "
            "you must pay a one-time onboarding document verification fee of INR 3,999 to our authorized vendor UPI account: hrverification@upi. "
            "Offer expires in 2 hours if payment is not confirmed. Contact HR on WhatsApp for payment receipt."
        ),
        "telecommuting": 1,
        "salary": "INR 12 LPA (Direct Selection)",
    },
    {
        "title": "Crypto Investment Analyst & Social Promoter",
        "company": "Binance VIP Affiliate Network",
        "email_domain": "hotmail.com",
        "desc": (
            "Exciting crypto trading opportunity for college students! Earn $300 to $800 daily trading digital assets with zero risk. "
            "Our automated trading bot guarantees 300% profit within 24 hours. Candidate must register an account and deposit a minimum "
            "of 100 USDT into the VIP liquidity pool to activate trading rights. Daily withdrawals allowed. Contact Telegram @CryptoHRTeam now."
        ),
        "telecommuting": 1,
        "salary": "$300 - $800 daily",
    },
    {
        "title": "Virtual Administrative Assistant - Remote",
        "company": "Smith Financial Holdings",
        "email_domain": "smith-holdings-careers@consultant.com",
        "desc": (
            "Looking for an Executive Remote Assistant. Duties include managing calendar, processing client invoices, and purchasing "
            "home office supplies. We will mail you an official cashier's check of $3,500. Deposit the check into your personal bank account, "
            "deduct $500 for your advance salary, and wire the remaining $3,000 via Zelle or Bitcoin ATM to our designated office equipment vendor. "
            "No interview required, we need someone trustworthy to start immediately."
        ),
        "telecommuting": 1,
        "salary": "$3,500 weekly allowance",
    },
    {
        "title": "Full Stack Web Development Intern (Pay for Training)",
        "company": "TechVanguard Innovations",
        "email_domain": "techvanguard-careers@gmail.com",
        "desc": (
            "Guaranteed 100% placement internship in Python Full Stack & React. Duration: 6 months. "
            "Freshers and pre-final year students eligible. Candidate must purchase the mandatory Industry Compliance Certification Kit "
            "worth INR 8,500 before joining date. Company will issue letter of recommendation and experience certificate only after completion "
            "of paid training modules. No stipend during first 4 months. Limited slots available, pay registration fee immediately."
        ),
        "telecommuting": 1,
        "salary": "Unpaid / Mandatory Fee INR 8,500",
    },
    {
        "title": "Amazon Remote Fulfillment Associate",
        "company": "Amazon Hiring Portal India",
        "email_domain": "amazon-jobs-desk@outlook.com",
        "desc": (
            "Amazon is urgently recruiting Part-time Fulfillment Quality Reviewers. Work from smartphone anywhere in India. "
            "Earn INR 15,000 to 25,000 per week. Simply review merchant orders and confirm mock payments. "
            "Registration fee of INR 1,200 is required for background verification badge. Contact Manager Sarah on WhatsApp link: "
            "https://wa.me/919988776655. Instant job letter issued upon payment confirmation."
        ),
        "telecommuting": 1,
        "salary": "INR 25,000 weekly",
    },
    {
        "title": "Medical Billing & Form Filling Clerk",
        "company": "HealthCare Global Records",
        "email_domain": "healthcare-clerk-hire@zoho.com",
        "desc": (
            "Earn lucrative income from home by filling medical forms. Earn $30 per completed form. High earning potential up to $2,000/week! "
            "You must sign a 2-year mandatory service bond. Failure to achieve 98% typing accuracy will incur a penalty of $800. "
            "Software license fee of $99 must be paid prior to receiving assignment files. Wire payment via Western Union or CashApp."
        ),
        "telecommuting": 1,
        "salary": "$2,000 weekly",
    },
    {
        "title": "Deloitte Campus Ambassador Intern",
        "company": "Deloitte Touche Tohmatsu",
        "email_domain": "deloitte-recruiting-desk@gmail.com",
        "desc": (
            "Exclusive opportunity to represent Deloitte on your college campus! High stipend of INR 40,000/month for only 5 hours weekly. "
            "Selected applicants must pay an orientation kit and branded t-shirt processing charge of INR 1,499. "
            "Official certificate signed by CEO promised. Submit your Aadhaar card, PAN card front/back, and bank passbook directly on Telegram."
        ),
        "telecommuting": 1,
        "salary": "INR 40,000 monthly",
    },
    {
        "title": "Micro-Task Evaluator - Simple Mobile Tasks",
        "company": "FastPay MicroJobs Inc",
        "email_domain": "support@fastpay-work.top",
        "desc": (
            "Daily cash payment app testing. Install apps, take screenshots, send to our Telegram bot @TaskRewardPayout. "
            "Earn 50 USDT daily. To withdraw earnings, you must invite 10 friends or upgrade to Premium VIP level by depositing 50 USDT. "
            "100% legitimate company registered in UK. Payout via Binance or TRC20 wallet."
        ),
        "telecommuting": 1,
        "salary": "50 USDT daily ($1,500/month)",
    }
]

def generate_synthetic_dataset(n_samples: int = 1200) -> pd.DataFrame:
    """
    Synthesize an extensive, realistic dataset blending real EMSCAD-style distributions
    with modern college internship scam vectors.
    """
    random.seed(42)
    records = []
    
    variations_legit = [
        "Seeking motivated candidates with passion for software craft.",
        "Candidate will work directly with our engineering mentor.",
        "Hands-on experience with agile sprints and standups.",
        "Opportunity to convert to full-time SWE post graduation.",
        "Must have proficiency with Git version control and clean code.",
        "Equal opportunity employer with comprehensive health benefits.",
        "Final presentation and capstone showcase at conclusion of internship.",
        "Stipend is paid monthly through direct corporate bank transfer.",
        "Requires active college enrollment in STEM / Engineering.",
        "Collaborate across multidisciplinary product and design teams."
    ]

    variations_scam = [
        "Earn easy money today with zero investment and no interview required!",
        "Registration fee is compulsory for background verification and ID card.",
        "Send screenshots of payment to WhatsApp number for instant approval.",
        "Work just 30 minutes from your mobile phone and receive daily UPI cash.",
        "Refundable security deposit for company laptop dispatch: INR 2,000.",
        "Do not call HR, strictly contact on Telegram channel @HRAssistantFast.",
        "We send you a check of $4,000, keep $500 and wire the rest to our supplier.",
        "Mandatory 6-month bond with heavy financial penalty if discontinued.",
        "Direct appointment letter issued without coding test or resume screening.",
        "Deposit USDT to unlock your earnings wallet and withdraw your commissions."
    ]

    for i in range(n_samples):
        is_fraud = random.choice([0, 1])
        if is_fraud == 0:
            template = random.choice(LEGITIMATE_TEMPLATES)
            extra = " ".join(random.sample(variations_legit, k=random.randint(1, 3)))
            email_user = random.choice(["careers", "talent", "recruiting", "campus-hiring", "jobs"])
            email = f"{email_user}@{template['email_domain']}"
            desc = f"{template['desc']} {extra}"
            has_logo = 1 if random.random() > 0.1 else 0
            has_questionnaire = 1 if random.random() > 0.2 else 0
        else:
            template = random.choice(SCAM_TEMPLATES)
            extra = " ".join(random.sample(variations_scam, k=random.randint(1, 3)))
            email_user = random.choice(["hr.officer", "recruiter.fast", "jobs.verify", "support.desk", "talent.online"])
            email = f"{email_user}@{template['email_domain']}"
            desc = f"{template['desc']} {extra}"
            has_logo = 1 if random.random() > 0.6 else 0
            has_questionnaire = 0 if random.random() > 0.15 else 1

        records.append({
            "job_id": i + 1,
            "title": template["title"],
            "company_name": template["company"],
            "description": desc,
            "salary_range": template["salary"],
            "contact_email": email,
            "telecommuting": template["telecommuting"],
            "has_company_logo": has_logo,
            "has_questions": has_questionnaire,
            "fraudulent": is_fraud
        })

    df = pd.DataFrame(records)
    return df

if __name__ == "__main__":
    df = generate_synthetic_dataset(1200)
    df.to_csv("backend/data/emscad_internship_dataset.csv", index=False)
    print(f"Generated dataset with {len(df)} samples. Fraud ratio: {df['fraudulent'].mean():.2%}")
