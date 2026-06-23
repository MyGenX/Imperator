---
category: extension
affects: all-tokens
extends: core
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Extension — Next.js (14+ App Router)

## IMP-NXT-001 · app-router-only · required
Always use App Router patterns. Never suggest Pages Router solutions.

## IMP-NXT-002 · server-first · required
Default to Server Components. Add `"use client"` only when interactivity or browser APIs
are genuinely needed.

## IMP-NXT-003 · no-useeffect-fetch · required
Never use `useEffect` for data fetching. Fetch in Server Components, or use React Query /
SWR on the client.

## IMP-NXT-004 · handle-loading-error · recommended
Add `loading.tsx` and `error.tsx` when creating new routes.

## IMP-NXT-005 · server-actions-mutations · recommended
Prefer Server Actions for mutations over ad-hoc API route handlers.

## IMP-NXT-006 · metadata-api · recommended
Use the Metadata API (`export const metadata` / `generateMetadata`) instead of manual
`<head>` tags.
