---
category: extension
affects: all-tokens
extends: core
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Extension — React

## IMP-RCT-001 · function-components-only · required
Use function components and hooks. Never write class components.

## IMP-RCT-002 · rules-of-hooks · required
Call hooks only at the top level of components or custom hooks — never conditionally or
in loops.

## IMP-RCT-003 · stable-keys · required
Use stable, unique keys for list items. Never use array index as key for dynamic lists.

## IMP-RCT-004 · no-premature-memo · recommended
Do not add `useMemo`/`useCallback`/`memo` unless there is a measured performance need.

## IMP-RCT-005 · lift-state-minimally · recommended
Keep state as local as possible; lift it only as far as it must be shared.

## IMP-RCT-006 · derive-dont-store · recommended
Derive values during render instead of duplicating them in state.
