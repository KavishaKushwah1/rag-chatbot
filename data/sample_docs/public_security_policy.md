# Acme Corp — Security Policy

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
