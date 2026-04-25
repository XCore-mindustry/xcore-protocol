# Python Tests

This directory contains the Python-side validation surface for the current canonical protocol repository state.

Current coverage includes:
- fixture validation tests for canonical valid/invalid examples
- generated-model roundtrip and strictness tests for the generated maps, chat/heartbeat, and discord surface
- generator/bootstrap tests that keep committed outputs and registry-driven behavior aligned

Consumer-side compatibility adapters and legacy acceptance behavior are out of scope here; those belong in application repositories.
