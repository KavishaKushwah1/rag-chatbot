"""
Generates a realistic fictional company knowledge base across HR,
engineering, product, compliance, and confidential-manager tiers —
enough breadth to test multi-doc retrieval, ACL filtering, and
fallback-on-no-match. Run once: python scripts/generate_sample_docs.py
"""
import os

OUT_DIR = "data/sample_docs"

DOCS = {
    # ---------- Tier 1: Company policies ----------
    "hr_pto_policy.md": {"permission": "hr", "text": """# Acme Corp — Paid Time Off (PTO) Policy

All full-time employees accrue 1.5 days of PTO per month, capped at 18 days
per calendar year. PTO accrual begins on the employee's start date, and
unused PTO up to 5 days may be carried over into the next year; anything
beyond that is forfeited on December 31st.

Employees must submit PTO requests through the HR portal at least 5
business days in advance for any leave longer than 2 days. Sick leave is
tracked separately from PTO and does not require advance notice.

New employees are not eligible to take PTO during their first 30 days of
employment, except in the case of documented medical emergencies, which
are handled on a case-by-case basis by HR.

Managers are expected to approve or deny PTO requests within 2 business
days of submission. If a request is not addressed within that window, it
is automatically escalated to the department head.
"""},

    "hr_remote_work_policy.md": {"permission": "hr", "text": """# Acme Corp — Remote Work Policy

Employees may work remotely up to 3 days per week without prior approval.
Fully remote arrangements (5 days/week) require written approval from both
the employee's manager and HR, and are reviewed every 6 months.

Remote employees are expected to be available during core hours, 10 AM to
3 PM in their local timezone, and must attend all scheduled team meetings
with video enabled unless otherwise agreed with their manager.

Acme Corp provides a one-time $500 home office stipend for remote
employees, which can be used for desks, chairs, or monitors. This stipend
is only available once per employee, not on a recurring annual basis.
"""},

    "public_code_of_conduct.md": {"permission": "public", "text": """# Acme Corp — Code of Conduct

All employees are expected to treat colleagues, customers, and partners
with respect and professionalism. Harassment, discrimination, or
retaliation of any kind will not be tolerated and should be reported to
HR immediately, either directly or through the anonymous ethics hotline.

Conflicts of interest — including outside employment, financial interests
in competitors, or hiring family members into your reporting chain — must
be disclosed to HR before they arise, not after.

Confidential company information, including unreleased product plans,
financial data, and customer data, must not be shared outside the
company, including on personal social media accounts.

Violations of this code may result in disciplinary action up to and
including termination, depending on severity.
"""},

    "public_expense_policy.md": {"permission": "public", "text": """# Acme Corp — Expense Reimbursement Policy

Employees may submit expense reports for business-related travel, client
meals, and approved software subscriptions through the Expensify portal.
Reports must be submitted within 30 days of the expense; late submissions
require manager sign-off.

Meals during business travel are reimbursed up to $75/day domestically and
$100/day internationally. Alcohol is only reimbursable when directly
related to client entertainment, and must be itemized separately.

Airfare should be booked in economy class for flights under 6 hours;
business class is permitted for longer international flights with
director-level approval. Personal expenses mixed into a business trip
(e.g., extending a trip for vacation) are not reimbursable and must be
paid out of pocket.
"""},

    "public_onboarding_checklist.md": {"permission": "public", "text": """# Acme Corp — New Hire Onboarding Checklist

Before your start date, IT will ship you a laptop and provision your
company email; you should receive login credentials 2 business days
before you start. Your manager will schedule a 30-minute welcome call on
day one.

Week one: complete mandatory compliance training (data privacy, code of
conduct, security awareness) in the Learning Portal — this must be done
within your first 5 business days. You'll also be added to your team's
Slack channels and calendar.

Week two: your manager will assign a peer buddy for your first 30 days,
and schedule 1:1 introductions with key cross-functional partners.

By day 30: complete your 30-day check-in survey, sent automatically by
HR, and schedule your first formal 1:1 goal-setting session with your
manager.
"""},

    "public_it_setup_guide.md": {"permission": "public", "text": """# Acme Corp — IT Setup Guide

To connect to internal systems, install the Acme VPN client from the IT
portal and log in with your company SSO credentials. VPN access is
required for internal tools like the HR portal and internal wiki, but not
for Slack or Google Workspace.

Password resets are self-service through the SSO portal; if you're locked
out entirely, contact the IT helpdesk via #it-help on Slack or
[email protected], with a 4-hour response SLA during business hours.

New laptops come pre-configured with standard software (Slack, Zoom,
company VPN, 1Password). Requests for additional software licenses go
through the IT portal and require manager approval for anything over
$50/month.

Two-factor authentication is mandatory for all company accounts and must
be set up within 24 hours of receiving your credentials.
"""},

    "engineering_deployment_guide.md": {"permission": "engineering", "text": """# Acme Corp — Deployment Guide (Internal Engineering)

All production deployments must go through the staging environment first.
No engineer may deploy directly to production without a passing staging
smoke test and one code review approval.

Deployments are only permitted Monday through Thursday, between 10 AM and
4 PM. Friday deployments are prohibited except for critical security
patches, which require sign-off from the engineering director.

The deployment pipeline uses GitHub Actions. On merge to main, the CI
pipeline runs unit tests, then integration tests, then a canary deploy to
5% of production traffic for 15 minutes before a full rollout. If error
rates exceed 1% during the canary phase, the deploy is automatically
rolled back.

Rollbacks can also be triggered manually via the `/deploy rollback`
command in the #eng-deploys Slack channel, which reverts to the last
known-good build within roughly 3 minutes.
"""},

    "engineering_incident_response.md": {"permission": "engineering", "text": """# Acme Corp — Incident Response Runbook

Incidents are classified into three severities. SEV1 means full service
outage or data loss risk, and must be acknowledged within 5 minutes with
an incident commander assigned immediately. SEV2 means significant
degraded performance affecting a subset of users, with a 15-minute
acknowledgment target. SEV3 covers minor issues with no user-facing
impact, handled during normal business hours.

For SEV1 and SEV2 incidents, the on-call engineer must post an initial
status update in #incidents within 10 minutes of acknowledgment, and every
30 minutes thereafter until resolution.

A postmortem document is required for all SEV1 incidents and any SEV2
incident lasting longer than 1 hour. Postmortems are blameless and must be
published within 5 business days of resolution.
"""},

    "product_pricing_overview.md": {"permission": "public", "text": """# Acme Corp — Product Pricing Overview

Acme Corp offers three pricing tiers. The Starter plan is $29/month and
includes up to 5 team members and 10GB of storage. The Growth plan is
$99/month, includes up to 25 team members, 100GB of storage, and priority
email support.

The Enterprise plan is custom-priced and includes unlimited team members,
unlimited storage, a dedicated account manager, and a 99.9% uptime SLA
with financial penalties for downtime beyond that threshold.

All plans include a 14-day free trial with no credit card required.
Customers on the Starter or Growth plan can upgrade or downgrade at any
time, with prorated billing applied to the current cycle. Annual billing
is available on all tiers at a 20% discount versus monthly billing.
"""},

    "product_faq.md": {"permission": "public", "text": """# Acme Corp — Frequently Asked Questions

Q: Can I export my data?
A: Yes. All plans allow full data export in CSV or JSON format at any
time from the account settings page, with no additional fee.

Q: Is there an API?
A: Yes, the REST API is available on the Growth and Enterprise plans. The
Starter plan includes read-only API access with a rate limit of 100
requests per hour.

Q: What happens if I cancel my subscription?
A: Your data remains accessible in read-only mode for 30 days after
cancellation, after which it is permanently deleted. You can request an
earlier deletion by contacting support.

Q: Do you offer discounts for nonprofits or students?
A: Yes, nonprofits receive a 30% discount on all plans, and students with
a valid .edu email receive the Growth plan free for 12 months.
"""},

    "public_helpdesk_faq.md": {"permission": "public", "text": """# Acme Corp — Internal Helpdesk FAQ

Q: My laptop won't connect to the office WiFi. What do I do?
A: Forget the network and reconnect using your SSO credentials, not your
old password. If that fails, restart the router by holding the reset
button for 5 seconds — this only affects guest WiFi, not the secured
network.

Q: How do I request access to a tool I don't have permissions for?
A: Submit a request through the IT portal under "Access Requests." Most
approvals take 1 business day; tools involving financial or customer data
require director-level sign-off and can take up to 5 business days.

Q: My badge isn't opening the office door.
A: Badges deactivate automatically after 90 days of inactivity for
security reasons. Visit the front desk to have it reactivated; no
approval needed if you're an active employee.

Q: How do I set up a printer?
A: All office printers are auto-discoverable once connected to the
secured WiFi network; no manual driver installation is required.
"""},

    # ---------- Tier 2: Differentiators ----------
    "manager_compensation_bands.md": {"permission": "manager", "text": """# Acme Corp — Compensation Bands (Confidential — Managers Only)

Engineering compensation bands are structured across 5 levels. L3
(mid-level engineer) base salary ranges from $110,000–$140,000. L4 (senior
engineer) ranges from $140,000–$175,000. L5 (staff engineer) ranges from
$175,000–$215,000, with equity grants scaling proportionally at each
level.

Annual merit increases are budgeted at an average of 4% company-wide, but
individual increases are determined by performance rating and position
within the band — employees below the midpoint of their band are
prioritized for larger increases.

Promotion to the next level requires a compensation band adjustment
within the same review cycle; managers may not defer band adjustments to
a later quarter without HR business partner approval.

This document is confidential and must not be shared with direct reports
or discussed outside of calibration and compensation planning meetings.
"""},

    "manager_performance_review_guidelines.md": {"permission": "manager", "text": """# Acme Corp — Performance Review Guidelines (Managers Only)

Performance reviews occur twice yearly, in June and December. Managers
must submit written evaluations at least 3 business days before the
calibration meeting, using the 5-point rating scale: Exceeds, Strong,
Meets, Partially Meets, Does Not Meet.

Ratings of "Partially Meets" or below automatically trigger a formal
Performance Improvement Plan (PIP) conversation with HR present, within 2
weeks of the rating being finalized.

Calibration meetings are used to normalize ratings across teams — no
individual manager may finalize a rating of "Exceeds" without cross-team
calibration discussion, to prevent grade inflation within a single team.

Compensation decisions are not finalized until 1 week after calibration,
to allow for cross-functional consistency review by HR business partners.
"""},

    "public_data_privacy_policy.md": {"permission": "public", "text": """# Acme Corp — Data Privacy Policy

Acme Corp collects customer data solely for the purpose of providing the
contracted service, and does not sell customer data to third parties
under any circumstances.

Customer data is encrypted at rest using AES-256 and in transit using
TLS 1.3. Access to production customer data is restricted to engineers
with an active, time-boxed access grant, logged and reviewed monthly by
the security team.

Data deletion requests are processed within 30 days of a verified
request, in compliance with GDPR and CCPA. Backups containing deleted
data are purged within 90 days as part of the standard backup rotation
cycle.

Any data breach affecting customer data must be reported to affected
customers within 72 hours of confirmed detection, per our contractual and
regulatory obligations.
"""},

    "public_security_policy.md": {"permission": "public", "text": """# Acme Corp — Security Policy

All employees must enable two-factor authentication on their company
accounts within 24 hours of account creation, and on any third-party tool
that stores customer or company data.

Laptops must have full-disk encryption enabled and are configured to
auto-lock after 5 minutes of inactivity. Lost or stolen devices must be
reported to IT security within 1 hour of discovery so they can be
remotely wiped.

Production database credentials are never shared over Slack or email;
access is granted exclusively through the internal secrets manager with
time-limited tokens that expire after 8 hours.

Security incidents (suspected phishing, unauthorized access, malware)
should be reported immediately to #security-incidents, which is monitored
24/7 by the on-call security engineer.
"""},

    "hr_wiki_team_norms.md": {"permission": "hr", "text": """# Acme Corp — HR Team Norms (Internal Wiki)

The HR team operates with a "no meeting Wednesdays" policy to protect
focus time for casework and policy development. Urgent employee relations
matters are the only exception and should be flagged directly to the HR
lead.

All employee relations cases are tracked in the confidential HR case
management system, never in shared documents or Slack. Case notes must be
finalized within 48 hours of any employee conversation.

The HR on-call rotation covers urgent matters (terminations, harassment
reports, safety concerns) outside business hours; the on-call schedule is
published monthly and rotates among senior HR business partners only.

This page is updated quarterly during the HR team's norms review meeting.
"""},

    "engineering_wiki_architecture_notes.md": {"permission": "engineering", "text": """# Acme Corp — Engineering Wiki: Architecture Notes

The core platform is a service-oriented architecture with 12 backend
services communicating over gRPC, fronted by a GraphQL gateway. Each
service owns its own Postgres database; cross-service joins are handled
at the gateway layer, not via direct database access.

The event bus (Kafka) is used for asynchronous workflows like billing
reconciliation and email notifications — synchronous request paths should
never depend on Kafka delivery guarantees for correctness.

As of the last architecture review, the notifications service is
scheduled for a rewrite from Node.js to Go, targeted for next quarter, due
to memory usage issues under high load.

This page is maintained by the platform team and reviewed at each
quarterly architecture review; it may be out of date between reviews for
fast-moving services.
"""},

    # ---------- Tier 3: Stretch ----------
    "public_support_ticket_examples.md": {"permission": "public", "text": """# Acme Corp — Resolved Support Ticket Examples

Ticket #4471: Customer reported CSV export failing for accounts with over
50,000 rows. Root cause was a timeout in the export worker; resolved by
moving large exports to an async job with an email notification when
ready. Fix shipped in v2.14.

Ticket #4502: Customer's API key stopped working after a plan downgrade.
Root cause was API access being tied to plan tier without a grace period.
Resolved by adding a 7-day grace period after downgrade before API access
is revoked.

Ticket #4519: Customer unable to invite team members past their plan's
seat limit, with a confusing error message. Resolved by updating the error
message to clearly state the seat limit and link directly to the upgrade
page.

Ticket #4530: Customer requested clarification on data retention after
cancellation. Support confirmed the standard 30-day read-only retention
period per the Data Privacy Policy, with no exceptions for extending it
without a signed data processing addendum.
"""},

    "hr_employee_handbook_benefits.md": {"permission": "hr", "text": """# Acme Corp — Employee Handbook: Benefits Enrollment

New employees have 30 days from their start date to enroll in health,
dental, and vision insurance; missing this window means waiting until the
next open enrollment period in November, except for qualifying life
events (marriage, birth, adoption).

Acme Corp matches 401(k) contributions up to 4% of salary, with immediate
vesting — there is no vesting schedule or waiting period for the employer
match.

The company covers 90% of the premium for employee-only health coverage
and 70% for dependents added to the plan. Employees can view exact premium
costs for their selected plan in the benefits portal before finalizing
enrollment.

Parental leave provides 16 weeks of paid leave for the primary caregiver
and 8 weeks for the secondary caregiver, regardless of gender, and can be
taken within 12 months of the birth or adoption date.
"""},

    "public_org_chart.md": {"permission": "public", "text": """# Acme Corp — Organization Structure

Acme Corp is organized into four main departments: Engineering, Product,
HR, and Sales. Each department is led by a VP who reports directly to the
CEO.

Engineering is split into three teams: Platform (owns core infrastructure
and the deployment pipeline), Product Engineering (owns customer-facing
features), and Security (owns the security policy and incident response
process).

HR is split into HR Business Partners (embedded with each department) and
a central People Operations team (owns benefits, payroll, and onboarding
logistics).

Questions about who owns a specific system or policy should be directed
first to your HR Business Partner or, for technical systems, to the
Platform team via #platform-questions on Slack.
"""},
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for filename, doc in DOCS.items():
        path = os.path.join(OUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc["text"].strip() + "\n")
        print(f"Wrote {path} (permission={doc['permission']})")

    print(f"\nDone. {len(DOCS)} sample docs written to {OUT_DIR}/")
    print("Permission tiers used: public, hr, engineering, manager")


if __name__ == "__main__":
    main()