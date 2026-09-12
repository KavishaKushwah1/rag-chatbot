# Acme Corp — Resolved Support Ticket Examples

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
