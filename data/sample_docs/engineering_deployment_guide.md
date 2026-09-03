# Acme Corp — Deployment Guide (Internal Engineering)

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
