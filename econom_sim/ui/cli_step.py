"""Developer REPL: step periods, skip, patch config, quit."""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def _parse_value(s: str) -> Any:
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return s


def _dot_set(d: dict[str, Any], path: str, value: Any) -> None:
    keys = path.split(".")
    cur: dict[str, Any] = d
    for k in keys[:-1]:
        nxt = cur.get(k)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[k] = nxt
        cur = nxt
    cur[keys[-1]] = value


def main() -> None:
    from econom_sim.config import Config, load_config
    from econom_sim.engine import init_state, run_period
    from econom_sim.io.snapshot import snapshot_to_dict

    ap = argparse.ArgumentParser(description="Step-by-step econom sim CLI")
    ap.add_argument("--config", default=str(_ROOT / "configs" / "base.yaml"))
    args = ap.parse_args()

    raw = load_config(args.config).model_dump(mode="python")
    state = init_state(Config.model_validate(raw))

    print("Commands: n = next period | c K = skip K periods | set path value | raw = dump yaml dict | q = quit")
    while True:
        try:
            line = input("sim> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        parts = line.split(maxsplit=2)
        cmd = parts[0].lower()
        if cmd == "q":
            break
        if cmd == "n":
            snap = run_period(state)
            print(snapshot_to_dict(snap)["metrics"])
            continue
        if cmd == "c" and len(parts) >= 2:
            k = int(parts[1])
            for _ in range(k):
                snap = run_period(state)
            print("after", k, ":", snapshot_to_dict(snap)["metrics"])
            continue
        if cmd == "set" and len(parts) >= 3:
            path, val_s = parts[1], parts[2]
            _dot_set(raw, path, _parse_value(val_s))
            state = init_state(Config.model_validate(raw))
            cur: Any = raw
            for k in path.split("."):
                cur = cur[k]
            print("config updated; state reset.", path, "=", cur)
            continue
        if cmd == "raw":
            print(raw)
            continue
        print("unknown command")


if __name__ == "__main__":
    main()
