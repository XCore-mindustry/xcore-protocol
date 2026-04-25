# Generation Validation

## Goal
Define the reusable validation commands for the phase-1 generator bootstrap.

## Maps Proof Slice Commands

### Regenerate and check outputs
```bash
uv run python scripts/validate-generation.py
```

This command:
- regenerates the maps proof slice outputs
- fails if generated files are stale after generation

### Validate generated Python models
```bash
uv run python scripts/validate-generated-models.py
```

This command runs the generated-model roundtrip tests for the maps slice.

### Full Python validation for the current repository state
```bash
uv run pytest
```

## CI Intent
The initial CI expectation for generator bootstrap is:
1. regenerate maps outputs
2. confirm generated files are current
3. run generated-model tests
4. run the existing Python schema/fixture suite

## Failure Semantics
- stale generated files mean generation output was not committed or generator logic drifted
- generated-model test failures mean the typed canonical surface drifted from fixtures/specs
- schema validation failures remain the authoritative signal that the canonical contract was broken
