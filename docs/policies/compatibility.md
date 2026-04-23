# Compatibility Policy

## Canonical Rule
Canonical schemas define the only official outbound form.

## Repository Boundary Rule
`xcore-protocol` describes only the canonical protocol surface. Temporary compatibility adapters, legacy aliases, and old payload translations belong in consumer/application repositories during migration.

## Change Rule
No contract change is complete without updating:
- schema/spec
- fixtures
- validation/tests
- migration notes when relevant
