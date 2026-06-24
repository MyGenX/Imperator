"""Static catalog for Imperator.

Version, ownership-marker constants, and the supported agent/style/profile/
domain/role lists. Imported by every other engine module; depends on nothing
inside the package so it never participates in import cycles.
"""

from __future__ import annotations

VERSION = "0.3.0"

# Ownership markers wrapped around generated content so `clean`/`doctor` can
# recognize Imperator-owned files without touching user-authored ones.
MARKER_BEGIN = "imperator:begin generated"
MARKER_END = "imperator:end generated"

# Global rules load in this fixed order.
GLOBAL_ORDER = ["output", "investigation", "processing", "behavior", "safety"]

DOMAINS_AVAILABLE = [
    "nextjs", "react", "typescript",
    "python", "fastapi", "postgres",
    "docker", "api-rest",
]

ROLES_AVAILABLE = [
    "business-analyst", "backend-developer", "frontend-developer",
    "qa-engineer", "devops",
]

# Domain bundles for common stacks.
PROFILES = {
    "fullstack-js": ["nextjs", "react", "typescript", "postgres"],
    "python-api": ["python", "fastapi", "postgres", "api-rest"],
    "minimal": [],
}

AGENTS = ["claude-code", "cursor", "codex", "gemini"]

# Compression profiles — how verbosely each rule body is rendered:
#   standard = directive + bullets + do/don't examples (full authored richness)
#   compact  = directive + bullets (drop fenced examples)
#   strict   = directive line only
STYLES = ["standard", "compact", "strict"]

# Back-compat alias for older callers (benchmarks, external scripts).
EXTENSIONS_AVAILABLE = DOMAINS_AVAILABLE
