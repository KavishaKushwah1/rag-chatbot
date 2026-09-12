# Acme Corp — Engineering Wiki: Architecture Notes

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
