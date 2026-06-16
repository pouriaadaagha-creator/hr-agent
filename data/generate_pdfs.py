"""
Run this script once to generate all sample HR PDF documents inside /data.
Usage: python data/generate_pdfs.py
"""

import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos


class HRDocument(FPDF):
    """Base PDF class with consistent header/footer styling."""

    def __init__(self, title: str):
        super().__init__()
        self.doc_title = title
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_fill_color(30, 60, 120)
        self.set_text_color(255, 255, 255)
        self.cell(
            0, 12, "Acme Corporation - Human Resources",
            fill=True, align="C",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        self.set_font("Helvetica", "I", 10)
        self.set_text_color(80, 80, 80)
        self.cell(
            0, 8, self.doc_title, align="C",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()} | Confidential - Internal Use Only", align="C")

    def section_title(self, text: str) -> None:
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(220, 230, 245)
        self.set_text_color(20, 40, 100)
        self.cell(
            0, 9, text, fill=True,
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        self.set_text_color(0, 0, 0)
        self.ln(2)

    def body_text(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(3)

    def bullet(self, items: list[str]) -> None:
        self.set_font("Helvetica", "", 10)
        indent = 8
        for item in items:
            self.set_x(self.l_margin + indent)
            width = self.w - self.l_margin - indent - self.r_margin
            self.multi_cell(width, 6, f"-  {item}")
        self.ln(2)


# ---------------------------------------------------------------------------
# 1. Employee Handbook
# ---------------------------------------------------------------------------

def generate_employee_handbook(output_dir: str) -> None:
    pdf = HRDocument("Employee Handbook - Version 3.2 | Effective: January 2024")

    pdf.section_title("1. Working Hours")
    pdf.body_text(
        "Standard working hours at Acme Corporation are Monday through Friday, "
        "9:00 AM to 6:00 PM, with a one-hour unpaid lunch break, resulting in an "
        "8-hour productive workday. Core hours during which all employees must be "
        "available are 10:00 AM to 4:00 PM."
    )
    pdf.bullet([
        "Total weekly hours: 40 hours",
        "Core hours: 10:00 AM - 4:00 PM (mandatory attendance)",
        "Flexible start: employees may begin between 8:00 AM and 10:00 AM",
        "All hours beyond 40 per week are classified as overtime",
    ])

    pdf.section_title("2. Annual Leave Policy")
    pdf.body_text(
        "All full-time employees are entitled to 26 working days of paid annual leave "
        "per calendar year. Part-time employees receive leave on a pro-rata basis. "
        "Leave accrues at a rate of 2.17 days per month."
    )
    pdf.bullet([
        "New employees: leave begins accruing from the first day of employment",
        "Maximum carry-over: 10 days into the following calendar year",
        "Unused leave beyond carry-over limit is forfeited on December 31",
        "Leave encashment is not permitted except upon resignation",
        "Requests must be submitted at least 5 working days in advance via HR portal",
    ])

    pdf.section_title("3. Sick Leave")
    pdf.body_text(
        "Employees are entitled to 15 days of paid sick leave per calendar year. "
        "Sick leave does not carry over to the next year and cannot be encashed."
    )
    pdf.bullet([
        "Absences of 1-2 days: self-declaration accepted",
        "Absences of 3 or more consecutive days: medical certificate required",
        "Sick leave beyond 15 days will be treated as unpaid leave",
        "Chronic illness cases are handled individually by HR in consultation with management",
    ])

    pdf.section_title("4. Overtime Policy")
    pdf.body_text(
        "Overtime is defined as any work performed beyond the standard 40-hour work week "
        "or outside the hours of 9:00 AM to 6:00 PM on weekdays. All overtime must be "
        "pre-approved by the employee's direct manager."
    )
    pdf.bullet([
        "Weekday overtime (after 6:00 PM): compensated at 1.5x the hourly rate",
        "Weekend work (Saturday/Sunday): compensated at 2x the hourly rate",
        "Public holiday work: compensated at 2.5x the hourly rate",
        "Overtime exceeding 20 hours/month requires VP-level approval",
        "Alternatively, employees may opt for compensatory time off at the same multiplier",
    ])

    pdf.section_title("5. Remote Work Policy")
    pdf.body_text(
        "Acme Corporation supports a hybrid work model. Employees may work remotely "
        "up to 2 days per week after successfully completing their 6-month probation period."
    )
    pdf.bullet([
        "Remote work days must be agreed upon with the direct manager weekly",
        "Employees must be reachable during core hours (10 AM - 4 PM) on remote days",
        "A stable internet connection of at least 10 Mbps is required",
        "Remote work privilege may be revoked for performance or attendance issues",
        "Fully remote arrangements require VP of HR approval",
    ])

    pdf.section_title("6. Dress Code")
    pdf.body_text(
        "Acme Corporation maintains a business casual dress code from Monday to Thursday. "
        "Fridays are designated as casual days."
    )
    pdf.bullet([
        "Business casual: collared shirts, blouses, trousers, chinos, smart dresses",
        "Not permitted: ripped clothing, beachwear, offensive graphics, open-toed shoes (client days)",
        "Client-facing days: business formal is required regardless of day of week",
        "Casual Fridays: neat casual attire; no sportswear",
    ])

    pdf.section_title("7. Employee Conduct")
    pdf.body_text(
        "All employees are expected to maintain the highest standard of professional "
        "conduct. This includes treating all colleagues, clients, and visitors with "
        "respect and dignity."
    )
    pdf.bullet([
        "Zero tolerance for harassment, discrimination, or bullying of any kind",
        "Conflicts of interest must be disclosed to HR in writing immediately",
        "Company assets and data must not be used for personal gain",
        "Social media posts that misrepresent the company are prohibited",
        "Violations may result in disciplinary action up to and including termination",
    ])

    path = os.path.join(output_dir, "employee_handbook.pdf")
    pdf.output(path)
    print(f"  Created: {path}")


# ---------------------------------------------------------------------------
# 2. Insurance Policy
# ---------------------------------------------------------------------------

def generate_insurance_policy(output_dir: str) -> None:
    pdf = HRDocument("Group Health Insurance Policy - Plan Year 2024")

    pdf.section_title("1. Insurance Activation")
    pdf.body_text(
        "Health insurance coverage is activated on the first day of employment for "
        "all full-time employees. Part-time employees working more than 30 hours per "
        "week are also eligible. Coverage begins immediately - there is no waiting period."
    )
    pdf.bullet([
        "Provider: ShieldCare Health Insurance Group",
        "Policy number format: ACM-2024-XXXXXX (issued within 3 working days of joining)",
        "Digital insurance card available via the ShieldCare mobile app within 48 hours",
        "Physical card mailed to home address within 10 working days",
    ])

    pdf.section_title("2. Dependent Coverage")
    pdf.body_text(
        "Employees may enroll eligible dependents within 30 days of their own enrollment "
        "or a qualifying life event (marriage, birth, adoption). Dependent premiums are "
        "partially subsidized by the company."
    )
    pdf.bullet([
        "Eligible dependents: legal spouse, domestic partner (registered), children up to age 26",
        "Company subsidy for spouse coverage: 50% of premium",
        "Company subsidy for child coverage: 75% of premium per child (max 3 children)",
        "Enrollment changes outside the 30-day window require a qualifying life event",
    ])

    pdf.section_title("3. Coverage Details")
    pdf.body_text(
        "The company plan provides comprehensive in-patient and out-patient coverage "
        "through a nationwide network of hospitals and clinics."
    )
    pdf.bullet([
        "In-patient hospitalization: covered up to $500,000 per year",
        "Out-patient consultations: covered up to $3,000 per year",
        "Specialist referrals: covered after GP referral (pre-authorization required above $1,000)",
        "Emergency room visits: fully covered with no co-pay within network",
        "Prescription drugs: 80% covered for formulary drugs; 50% for non-formulary",
        "Mental health sessions: up to 20 sessions per year covered at 100%",
        "Dental: annual checkups and basic procedures covered up to $800/year",
        "Vision: one eye exam and $300 toward glasses or contacts per year",
        "Pre-existing conditions: covered from day one - no exclusion period",
    ])

    pdf.section_title("4. Reimbursement Process")
    pdf.body_text(
        "For services received at network providers, billing is handled directly. "
        "For out-of-network services or direct payments, employees must submit a "
        "reimbursement claim within 90 days of the service date."
    )
    pdf.bullet([
        "Submit claims via the ShieldCare employee portal or mobile app",
        "Required documents: itemized receipt, diagnosis code, doctor's note",
        "Processing time: 7-10 business days after submission",
        "Reimbursement paid directly to employee bank account on file with HR",
        "Claims older than 90 days will not be accepted",
        "Disputes: contact HR Benefits team at benefits@acmecorp.com",
    ])

    path = os.path.join(output_dir, "insurance_policy.pdf")
    pdf.output(path)
    print(f"  Created: {path}")


# ---------------------------------------------------------------------------
# 3. Leave Policy
# ---------------------------------------------------------------------------

def generate_leave_policy(output_dir: str) -> None:
    pdf = HRDocument("Leave Policy - Comprehensive Guide | Effective: January 2024")

    pdf.section_title("1. Annual Leave")
    pdf.body_text(
        "All permanent full-time employees are entitled to 26 working days of paid "
        "annual leave per calendar year. Leave is accrued at 2.17 days per completed month."
    )
    pdf.bullet([
        "Entitlement: 26 working days per year",
        "Accrual: 2.17 days/month from date of joining",
        "Carry-over: maximum 10 days may be carried into the next calendar year",
        "Minimum leave request: half a day",
        "Advanced notice: minimum 5 working days for leave of 3 days or fewer",
        "Advanced notice: minimum 10 working days for leave exceeding 3 consecutive days",
        "Manager approval is mandatory before leave is confirmed",
        "Leave during probation is limited to 5 days and requires VP approval",
    ])

    pdf.section_title("2. Sick Leave")
    pdf.body_text(
        "Employees are entitled to 15 days of paid sick leave per calendar year. "
        "Sick leave resets on January 1 each year and does not carry over."
    )
    pdf.bullet([
        "Entitlement: 15 working days per year",
        "Self-certification accepted for 1-2 consecutive days",
        "Medical certificate required for 3 or more consecutive days",
        "Sick leave beyond 15 days in a year is treated as unpaid unless covered by long-term illness policy",
        "Employees on sick leave must notify their manager by 9:30 AM on the first day of absence",
    ])

    pdf.section_title("3. Marriage Leave")
    pdf.body_text(
        "Employees are entitled to paid marriage leave upon their own marriage. "
        "This benefit applies once during the period of employment."
    )
    pdf.bullet([
        "Entitlement: 5 working days of paid leave",
        "Must be taken within 30 days of the marriage date",
        "Proof of marriage (marriage certificate) required upon return",
        "This leave is in addition to annual leave entitlement",
    ])

    pdf.section_title("4. Maternity & Paternity Leave")
    pdf.body_text(
        "Acme Corporation provides generous parental leave to support employees "
        "welcoming a new child through birth or adoption."
    )
    pdf.bullet([
        "Maternity leave: 16 weeks fully paid for eligible employees",
        "Eligibility for maternity: employed for at least 6 months before expected due date",
        "Paternity leave: 4 weeks fully paid",
        "Adoption leave: primary caregiver receives 16 weeks; secondary caregiver receives 4 weeks",
        "Leave may begin up to 2 weeks before the due date",
        "HR must be notified at least 8 weeks before the expected start of parental leave",
        "Employees may request up to an additional 8 weeks of unpaid parental leave",
    ])

    pdf.section_title("5. Emergency Leave")
    pdf.body_text(
        "Emergency leave is granted for unexpected urgent situations involving an "
        "employee's immediate family or personal crisis."
    )
    pdf.bullet([
        "Entitlement: up to 3 days per incident, maximum 6 days per year",
        "Qualifying events: death or serious illness of an immediate family member, "
        "natural disaster affecting primary residence, serious personal medical emergency",
        "Immediate family: spouse, children, parents, siblings",
        "Notify manager and HR as soon as possible - documentation may be requested",
        "Emergency leave beyond 6 days per year is subject to VP of HR approval",
        "Emergency leave is separate from sick leave and annual leave",
    ])

    pdf.section_title("6. Public Holidays")
    pdf.body_text(
        "Employees are entitled to all gazetted public holidays. When a public holiday "
        "falls on a weekend, the next working day is observed as a substitute holiday."
    )
    pdf.bullet([
        "Approximately 12 public holidays per year",
        "Holiday schedule is published on the HR portal by November 30 each year",
        "Work on public holidays is compensated at 2.5x the hourly rate",
    ])

    path = os.path.join(output_dir, "leave_policy.pdf")
    pdf.output(path)
    print(f"  Created: {path}")


# ---------------------------------------------------------------------------
# 4. Onboarding Policy
# ---------------------------------------------------------------------------

def generate_onboarding_policy(output_dir: str) -> None:
    pdf = HRDocument("Onboarding Policy - New Employee Guide | HR-OB-2024")

    pdf.section_title("1. First-Day Procedures")
    pdf.body_text(
        "Your first day at Acme Corporation is designed to make you feel welcome and "
        "ensure you have everything needed to start contributing. Please arrive at "
        "9:00 AM and report to the reception desk, where the HR coordinator will meet you."
    )
    pdf.bullet([
        "Arrival time: 9:00 AM on your first day",
        "Report to: Main Reception, 3rd Floor, Acme Tower",
        "Bring: government-issued photo ID and signed offer letter",
        "HR induction session: 9:30 AM - 11:30 AM (mandatory)",
        "IT setup and system access: 11:30 AM - 1:00 PM",
        "Lunch with your manager and team: 1:00 PM",
        "Department orientation: 2:00 PM - 5:00 PM",
        "HR portal registration must be completed by end of day 1",
    ])

    pdf.section_title("2. Equipment Assignment")
    pdf.body_text(
        "All new employees are issued standard equipment on their first day. "
        "Equipment is logged against the employee record and must be returned "
        "in good condition upon separation from the company."
    )
    pdf.bullet([
        "Standard laptop: 14-inch business laptop with pre-installed software suite",
        "Mobile phone: issued to Senior Associate level and above",
        "Access card: office and floor access activated by end of day 1",
        "Software licenses: Microsoft 365, Slack, Jira, Confluence, HR portal",
        "Additional equipment requests: submitted via IT helpdesk within first week",
        "Damaged or lost equipment: employee is liable for replacement cost if due to negligence",
    ])

    pdf.section_title("3. Training Process")
    pdf.body_text(
        "Acme Corporation's structured onboarding training spans the first 90 days. "
        "All training milestones are tracked in the HR portal and are mandatory "
        "unless formally waived by the department head."
    )
    pdf.bullet([
        "Week 1: Mandatory compliance training (Code of Conduct, Data Privacy, Security Awareness)",
        "Week 1: HR systems and benefits orientation (self-paced, 3 hours)",
        "Week 2-4: Role-specific technical training delivered by your team lead",
        "Month 2: Cross-functional shadowing sessions (min. 2 departments)",
        "Month 3: Skills assessment and 90-day performance review with manager",
        "All mandatory e-learning modules must be completed within 14 days of joining",
        "Training completion certificates are stored in the employee's HR file",
    ])

    pdf.section_title("4. Probation Period")
    pdf.body_text(
        "All new employees serve a probation period during which performance, "
        "conduct, and cultural fit are assessed. The standard probation period "
        "is 6 months from the date of joining."
    )
    pdf.bullet([
        "Standard probation: 6 months",
        "Performance reviews during probation: at 1 month, 3 months, and 6 months",
        "Benefits available during probation: full health insurance, salary, sick leave",
        "Benefits restricted during probation: annual leave limited to 5 days; no remote work",
        "Probation extension: manager may extend probation by up to 3 months with HR approval",
        "Confirmation of employment: issued in writing within 5 days of successful probation completion",
        "During probation, either party may terminate with 2 weeks' written notice",
        "Post-probation notice period: as stated in the individual employment contract (typically 1-3 months)",
    ])

    pdf.section_title("5. Buddy Program")
    pdf.body_text(
        "Every new employee is assigned an Onboarding Buddy - a peer colleague "
        "who will help you navigate the company culture and answer informal questions "
        "during your first 90 days."
    )
    pdf.bullet([
        "Buddy is assigned before your start date and will reach out on day 1",
        "Weekly check-ins with your buddy are encouraged during the first month",
        "Buddy is a peer resource, not a manager - no reporting relationship",
        "Feedback on the buddy program is collected at the 90-day review",
    ])

    path = os.path.join(output_dir, "onboarding_policy.pdf")
    pdf.output(path)
    print(f"  Created: {path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    output_dir = os.path.dirname(os.path.abspath(__file__))
    print("Generating HR sample PDF documents...")
    generate_employee_handbook(output_dir)
    generate_insurance_policy(output_dir)
    generate_leave_policy(output_dir)
    generate_onboarding_policy(output_dir)
    print("All documents generated successfully.")
