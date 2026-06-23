---
category: extension
affects: all-tokens
extends: core
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Extension — TypeScript

## IMP-TS-001 · no-any · required
Never use `any`. Use precise types, generics, or `unknown` with narrowing.

## IMP-TS-002 · strict-mode · required
Assume `strict` is on. Handle `null`/`undefined` explicitly.

## IMP-TS-003 · type-over-interface-unions · recommended
Use `type` for unions and mapped types; `interface` for extendable object shapes.

## IMP-TS-004 · no-non-null-assertion · recommended
Avoid the `!` non-null assertion. Narrow types instead.

## IMP-TS-005 · infer-dont-annotate · recommended
Let TypeScript infer obvious local types; annotate function signatures and public APIs.

## IMP-TS-006 · no-ts-ignore · required
Never use `@ts-ignore`. If suppression is unavoidable, use `@ts-expect-error` with a
reason.
