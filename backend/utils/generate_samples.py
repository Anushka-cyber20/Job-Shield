"""
Generate Sample PDF Offer Letter and Batch CSV for College Project Demonstration.
"""

import csv
from pypdf import PdfWriter
import io

def create_sample_batch_csv():
    rows = [
        {
            "title": "Software Development Engineer Intern",
            "company": "Amazon Web Services",
            "salary": "$52/hour",
            "contact_email": "aws-campus@amazon.com",
            "description": "AWS is hiring SWE Interns for S3 Distributed Storage. Build Go/Java microservices, participate in design reviews, and deploy to AWS. Equal opportunity employer."
        },
        {
            "title": "YouTube Video Liker & Reviewer (Work From Home)",
            "company": "Global Media Review",
            "salary": "INR 4,000 daily guaranteed",
            "contact_email": "parttime.jobs@gmail.com",
            "description": "URGENT HIRING! Earn INR 2,000 to 5,000 daily watching videos and liking YouTube channels. Direct payment to UPI. Contact Telegram @MediaPayoutHR immediately."
        },
        {
            "title": "Graduate Engineer Trainee - 2026 Batch",
            "company": "Tata Consultancy Services (TCS)",
            "salary": "INR 4.5 LPA",
            "contact_email": "campus.recruiting@tcs.com",
            "description": "TCS National Qualifier Test drive for 2026 batch. TCS strictly never charges any registration fee or security deposit at any stage."
        },
        {
            "title": "Data Entry Typist - Laptop Courier Deposit Required",
            "company": "Apex Global Solutions",
            "salary": "$60/hour",
            "contact_email": "apex-jobs@yahoo.com",
            "description": "Earn $60 per hour typing Word documents from home. Mandatory refundable security deposit of $150 (INR 2,500) required for laptop courier dispatch insurance."
        },
        {
            "title": "Frontend React Engineer Intern",
            "company": "Vercel",
            "salary": "$40/hour",
            "contact_email": "careers@vercel.com",
            "description": "Design engineering team at Vercel. Develop Next.js and Tailwind components. Requires familiarity with TypeScript, React, and Git."
        },
        {
            "title": "Direct Selection Technical Specialist (No Interview)",
            "company": "Google LLC India Hiring",
            "salary": "INR 14 LPA",
            "contact_email": "google-recruiting-desk@gmail.com",
            "description": "Direct appointment letter issued for Google Technical role without test or interview. Pay document verification charge of INR 2,999 to secure offer slot."
        },
        {
            "title": "Junior Python Full Stack Intern (Mandatory Training Kit)",
            "company": "TechVanguard Innovations",
            "salary": "Unpaid / Fee INR 8,500",
            "contact_email": "techvanguard-careers@gmail.com",
            "description": "6 months unpaid internship. Students must purchase industrial training kit worth INR 8,500 before starting. Mandatory 2-year service bond with penalty."
        },
        {
            "title": "Cloud Operations Intern",
            "company": "Datadog",
            "salary": "$45/hour",
            "contact_email": "jobs@datadoghq.com",
            "description": "Maintain Kubernetes clusters and Prometheus alerts. Shell scripting and Linux fundamentals required. Mentor assigned for 12 weeks."
        }
    ]
    
    with open("samples/sample_placement_batch.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "company", "salary", "contact_email", "description"])
        writer.writeheader()
        writer.writerows(rows)
    print("Created samples/sample_placement_batch.csv")

def create_sample_fake_offer_pdf():
    # Build a clean PDF with PDF structure using minimal bytes
    # A standard text PDF format
    content_stream = (
        "BT\n"
        "/F1 18 Tf\n"
        "50 720 Td\n"
        "(APEX GLOBAL CONSULTING SERVICES - APPOINTMENT LETTER) Tj\n"
        "/F1 11 Tf\n"
        "0 -30 Td\n"
        "(Ref: AGCS/HR/2026/89412                                     Date: February 20, 2026) Tj\n"
        "0 -25 Td\n"
        "(Dear Candidate,) Tj\n"
        "0 -20 Td\n"
        "(We are pleased to offer you the position of Remote Technical Data Specialist.) Tj\n"
        "0 -20 Td\n"
        "(Your monthly remuneration will be fixed at INR 65,000 per month.) Tj\n"
        "0 -25 Td\n"
        "(MANDATORY ONBOARDING & HARDWARE DISPATCH TERMS:) Tj\n"
        "0 -20 Td\n"
        "(1. The company will deliver a pre-configured Apple MacBook Air to your address.) Tj\n"
        "0 -20 Td\n"
        "(2. As per company insurance policy, you must transfer a REFUNDABLE SECURITY DEPOSIT) Tj\n"
        "0 -20 Td\n"
        "(   of INR 2,500 via UPI (apexoperations@upi) for courier dispatch insurance.) Tj\n"
        "0 -20 Td\n"
        "(3. This deposit is 100% refundable and will be credited back with your first stipend.) Tj\n"
        "0 -25 Td\n"
        "(4. To complete onboarding, send payment screenshot to our Telegram HR @ApexCoordinator.) Tj\n"
        "0 -30 Td\n"
        "(Sincerely,) Tj\n"
        "0 -20 Td\n"
        "(HR Recruitment Team - Apex Global) Tj\n"
        "ET\n"
    )
    
    pdf_obj = f"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>
endobj
4 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>
endobj
5 0 obj
<< /Length {len(content_stream.encode('utf-8'))} >>
stream
{content_stream}endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000227 00000 n 
0000000305 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
{370 + len(content_stream.encode('utf-8'))}
%%EOF"""

    with open("samples/sample_fake_offer_letter.pdf", "wb") as f:
        f.write(pdf_obj.encode("utf-8"))
    print("Created samples/sample_fake_offer_letter.pdf")

if __name__ == "__main__":
    create_sample_batch_csv()
    create_sample_fake_offer_pdf()
