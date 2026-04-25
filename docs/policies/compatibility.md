# Compatibility Policy

## Canonical Rule
Canonical schemas define the only official outbound form.

## Repository Boundary Rule
`xcore-protocol` describes only the canonical protocol surface. Temporary compatibility adapters, legacy aliases, and old payload translations belong in consumer/application repositories during migration.

Generated Java/Python protocol artifacts are part of the supported canonical consumption surface. Compatibility glue must wrap those artifacts in consumer repos rather than altering canonical specs or generated outputs.

## Change Rule
No contract change is complete without updating:
- schema/spec
- fixtures
- validation/tests
- migration notes when relevant
