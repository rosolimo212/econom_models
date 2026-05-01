"""
Backward-compatible entry: delegates to the archived monolith.

New code should use `econom_sim` and YAML configs. The legacy implementation
lives in `old_versions/smith_legacy.py`.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_legacy = Path(__file__).resolve().parent / "old_versions" / "smith_legacy.py"
_spec = importlib.util.spec_from_file_location("smith_legacy", _legacy)
if _spec is None or _spec.loader is None:
    raise ImportError("Cannot load old_versions/smith_legacy.py")
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

globals().update(
    {k: v for k, v in _mod.__dict__.items() if not k.startswith("_")}
)
