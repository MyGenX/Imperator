---
category: extension
affects: all-tokens
extends: core
agents: [claude-code, cursor, codex, gemini]
---
# Imperator Extension — Docker & Compose

## IMP-DOC-001 · pin-base-images · required
Pin base images to a specific tag/digest. Never rely on `latest`.

## IMP-DOC-002 · multi-stage-builds · recommended
Use multi-stage builds to keep final images small and free of build tooling.

## IMP-DOC-003 · non-root-user · required
Run containers as a non-root user.

## IMP-DOC-004 · no-secrets-in-image · required
Never bake secrets into images or `Dockerfile`. Use build args, env, or secret mounts.

## IMP-DOC-005 · layer-cache-order · recommended
Order layers from least to most frequently changing; copy dependency manifests before
source.

## IMP-DOC-006 · dockerignore · recommended
Maintain a `.dockerignore` to exclude `node_modules`, `.git`, and build artifacts.
