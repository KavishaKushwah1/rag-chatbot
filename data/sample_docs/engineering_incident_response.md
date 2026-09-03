# Acme Corp — Incident Response Runbook

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
