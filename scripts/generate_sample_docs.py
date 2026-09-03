"""
Generates a small fictional company knowledge base so the pipeline has
something realistic to ingest, retrieve, and (later) apply ACL to.
Run once: python scripts/generate_sample_docs.py
"""
import os

OUT_DIR = "data/sample_docs"

DOCS = {
    "hr_pto_policy.md": {
        "permission": "hr",
        "text": """# Acme Corp — Paid Time Off (PTO) Policy

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
""",
    },
    "hr_remote_work_policy.md": {
        "permission": "hr",
        "text": """# Acme Corp — Remote Work Policy

Employees may work remotely up to 3 days per week without prior approval.
Fully remote arrangements (5 days/week) require written approval from both
the employee's manager and HR, and are reviewed every 6 months.

Remote employees are expected to be available during core hours, 10 AM to
3 PM in their local timezone, and must attend all scheduled team meetings
with video enabled unless otherwise agreed with their manager.

Acme Corp provides a one-time $500 home office stipend for remote
employees, which can be used for desks, chairs, or monitors. This stipend
is only available once per employee, not on a recurring annual basis.
""",
    },
    "engineering_deployment_guide.md": {
        "permission": "engineering",
        "text": """# Acme Corp — Deployment Guide (Internal Engineering)

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
""",
    },
    "engineering_incident_response.md": {
        "permission": "engineering",
        "text": """# Acme Corp — Incident Response Runbook

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
""",
    },
    "product_pricing_overview.md": {
        "permission": "public",
        "text": """# Acme Corp — Product Pricing Overview

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
""",
    },
    "product_faq.md": {
        "permission": "public",
        "text": """# Acme Corp — Frequently Asked Questions

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
""",
    },
}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for filename, doc in DOCS.items():
        path = os.path.join(OUT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(doc["text"].strip() + "\n")
        print(f"Wrote {path} (permission={doc['permission']})")

    print(f"\nDone. {len(DOCS)} sample docs written to {OUT_DIR}/")
    print("Permission tiers used: public, hr, engineering")


if __name__ == "__main__":
    main()