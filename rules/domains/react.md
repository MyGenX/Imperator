---
category: domain
domain: react
affects: all-tokens
paths: ["**/*.{jsx,tsx}"]
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Domain — React

**Golden path:** Function components and hooks only. Keep state local and minimal, derive
instead of duplicating, and lift state only as far as it must be shared. Optimize
(`memo`/`useMemo`/`useCallback`) only when a real performance problem is measured. Handle
loading, empty, and error states for every async view.

## IMP-RCT-001 · function-components-only · required
Use function components and hooks; never class components.
- Express lifecycle with `useEffect`/`useLayoutEffect`, not class methods.

## IMP-RCT-002 · rules-of-hooks · required
Call hooks unconditionally at the top level.
- Never call hooks in conditions, loops, or nested functions.
- Hooks run only in components or other hooks.

## IMP-RCT-003 · stable-keys · required
Give list items stable, unique keys.
- Use a domain id as the key, not the array index for dynamic/reorderable lists.
```
do:    items.map(i => <Row key={i.id} ... />)
don't: items.map((i, idx) => <Row key={idx} ... />)
```

## IMP-RCT-004 · no-premature-memo · recommended
Don't memoize without a measured need.
- Skip `useMemo`/`useCallback`/`memo` until profiling shows a real cost.
- Prefer simpler renders and correct keys over reflexive memoization.

## IMP-RCT-005 · lift-state-minimally · recommended
Keep state as local as possible.
- Co-locate state with the component that uses it; lift only to the nearest common parent.
- Reach for context/stores only for genuinely shared/global state.

## IMP-RCT-006 · derive-dont-store · recommended
Derive values during render instead of storing them.
- Compute from props/state in the render body rather than syncing via effects.
- Don't mirror a prop into state unless you intentionally need a snapshot.

## IMP-RCT-007 · effect-cleanup · required
Clean up and scope effects correctly.
- Return a cleanup for subscriptions, timers, and listeners.
- Set a complete, honest dependency array; don't lie to silence the linter.

## IMP-RCT-008 · effects-for-external-only · recommended
Use effects only to sync with systems outside React.
- Don't use `useEffect` to transform props into state or to fetch when the framework
  offers loaders/server components.
- Handle user events in handlers, not in effects.

## IMP-RCT-009 · controlled-inputs · recommended
Prefer controlled form inputs.
- Drive value from state with an `onChange`; keep one source of truth.
- Use uncontrolled refs only for simple/uncontrolled-by-design cases.

## IMP-RCT-010 · error-boundaries · recommended
Guard risky subtrees with error boundaries.
- Wrap data-driven or third-party-heavy regions so one failure doesn't blank the app.
- Pair with `Suspense` fallbacks where you stream or lazy-load.
