---
category: domain
domain: nextjs
affects: all-tokens
paths: ["app/**", "pages/**", "**/*.{tsx,ts,jsx,js}", "next.config.*"]
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Domain — Next.js (App Router)

**Golden path:** App Router; Server Components by default; Server Actions for mutations;
data fetched on the server. Add `loading.tsx`/`error.tsx` per route, set metadata via the
Metadata API, and reach for the client only for interactivity or browser APIs. Be explicit
about caching and revalidation.

## IMP-NXT-001 · app-router-only · required
Use App Router patterns; don't introduce Pages Router.
- Build features under `app/` with route segments, layouts, and route groups.
- Don't mix in `pages/`-era data methods (`getServerSideProps`/`getStaticProps`).

## IMP-NXT-002 · server-first · required
Default to Server Components; opt into the client deliberately.
- Add `"use client"` only for interactivity, state, effects, or browser APIs.
- Keep client components small and at the leaves; pass server data down as props.
```
do:    server component fetches data, renders a small client island for the form
don't: mark the whole page tree "use client" to use one onClick
```

## IMP-NXT-003 · no-useeffect-fetch · required
Don't fetch data in `useEffect`.
- Fetch in Server Components (or route loaders) on the server.
- If client fetching is required, use React Query/SWR, not raw effects.

## IMP-NXT-004 · handle-loading-error · recommended
Give every route its loading and error UI.
- Add `loading.tsx` (Suspense fallback) and `error.tsx` (reset boundary) per segment.
- Add `not-found.tsx` where a resource may be missing.

## IMP-NXT-005 · server-actions-mutations · recommended
Prefer Server Actions for mutations.
- Use Server Actions over hand-rolled API routes for form/data mutations.
- Revalidate affected data (`revalidatePath`/`revalidateTag`) after a mutation.

## IMP-NXT-006 · metadata-api · recommended
Set metadata via the Metadata API.
- Export `metadata` or `generateMetadata`; don't hand-write `<head>` tags.

## IMP-NXT-007 · explicit-caching · required
Be deliberate about caching and revalidation.
- Choose fetch caching intentionally (`cache`, `next: { revalidate }`); don't rely on defaults by accident.
- Mark dynamic routes (`dynamic`/`revalidate`) when data must be fresh per request.

## IMP-NXT-008 · route-handlers-for-apis · recommended
Use Route Handlers for real HTTP endpoints, Server Actions for mutations from your UI.
- Put webhooks and public/third-party APIs in `route.ts` handlers.
- Don't duplicate a Server Action as an API route without a reason.

## IMP-NXT-009 · env-server-only · required
Keep server secrets off the client.
- Only `NEXT_PUBLIC_*` env vars reach the browser; never expose other secrets.
- Keep secret-using code in Server Components/Actions/Route Handlers.

## IMP-NXT-010 · next-image-font · recommended
Use built-in optimization primitives.
- Use `next/image` for images and `next/font` for fonts instead of raw tags.
