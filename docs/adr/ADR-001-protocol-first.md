# ADR-001: Protocol-first ownership for XCore cross-service communication

## Status
Proposed

## Decision
Use `xcore-protocol` as the canonical source of truth for XCore wire-level communication artifacts.

## Rationale
Cross-repository contracts must not be defined independently by application implementations. A shared protocol boundary enables:

- explicit schema ownership
- cross-language consistency
- controlled compatibility
- easier onboarding for new services and agents

## Scope
This repository owns:
- message schemas
- envelope definitions
- route metadata
- fixtures/examples
- protocol SDKs for Java and Python
- compatibility tests

This repository does not own application runtime or business logic.

## Initial Migration Priority
Moderation contracts first.
