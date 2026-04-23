# xcore-protocol

Canonical cross-service protocol for the XCore ecosystem.

## Mission
`xcore-protocol` is the canonical source of truth for XCore cross-service communication.

It defines:
- message schemas
- envelope structure
- route and stream metadata
- versioning and compatibility rules
- canonical fixtures
- Java and Python protocol SDKs
- cross-language compatibility tests

## Scope
This repository contains only **cross-process / cross-service wire protocol artifacts**.

### In scope
- event, command, and RPC contracts
- envelope definitions
- route metadata
- shared payload subtypes
- protocol fixtures and validation helpers
- Java and Python protocol SDKs

### Out of scope
- application business logic
- Discord handlers or presentation code
- Mindustry runtime integration
- Mongo persistence
- app-specific reconnect/worker orchestration

## Repository Layout
- `docs/` — ADRs, architecture notes, policies, migration notes
- `spec/` — protocol specs, shared types, envelopes, routes
- `fixtures/` — valid, invalid, and legacy examples
- `java/` — Java protocol support modules
- `python/` — Python protocol package
- `compat/` — cross-language compatibility checks
- `scripts/` — validation/generation/release helper placeholders

## Planned First Slice
The first migration slice is the **moderation** family:
- ban created
- mute created
- vote-kick created
- kick-banned command
- pardon command
- moderation audit appended

## Current Status
This repository is in bootstrap state. Initial design docs and repository structure exist; canonical moderation specs and SDK implementation are the next step.

## See Also
- `docs/adr/ADR-001-protocol-first.md`
- `docs/architecture/protocol-overview.md`
- `docs/policies/versioning.md`
- `docs/policies/compatibility.md`
