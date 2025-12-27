"""
Deprecated module.

This file belonged to the early Flask implementation and is no longer used.
FastAPI authentication and authorization are implemented in `core/deps.py`.

Any import of this module will raise an error to prevent accidental usage.
"""

raise RuntimeError(
    "core/auth.py is deprecated. Use FastAPI deps in core/deps.py (e.g., get_current_admin)."
)