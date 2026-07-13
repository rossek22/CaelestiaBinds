#!/usr/bin/env python3
"""CLI for qs — list/save/delete land here."""

from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import (  # noqa: E402
    load_all_binds,
    load_store,
    load_var_values,
    norm_keys,
    pretty_keys,
    remove_bind_from_system_lua,
    save_store,
    write_hypr_user_lua,
)


def binds_payload():
    store = load_store()
    binds = load_all_binds(store)
    out = []
    for b in binds:
        out.append(
            {
                "id": b.id,
                "keys": pretty_keys(b.keys),
                "keysRaw": norm_keys(b.keys),
                "title": b.title,
                "detail": b.detail,
                "category": b.category,
                "source": b.source,
                "kind": b.kind,
                "payload": b.payload,
                "flags": b.flags,
                "enabled": b.enabled,
                "technical": b.technical,
                "technicalResolved": b.technical_resolved or b.technical,
                "hasVarCmd": bool(
                    b.technical_resolved and b.technical_resolved != b.technical
                ),
                "raw": b.raw,
            }
        )
    return {
        "ok": True,
        "binds": out,
        "vars": load_var_values(),
        "counts": {
            "total": len(out),
            "custom": sum(1 for b in out if b["source"] == "custom"),
            "system": sum(1 for b in out if b["source"] == "system"),
            "override": sum(1 for b in out if b["source"] == "override"),
            "disabled": sum(1 for b in out if not b["enabled"]),
        },
    }


def find_bind(binds, bid: str):
    for b in binds:
        if b.id == bid:
            return b
    for b in binds:
        if norm_keys(b.keys).lower() == norm_keys(bid).lower():
            return b
    return None


def entry_from_data(data: dict) -> dict:
    return {
        "id": data.get("id") or str(uuid.uuid4()),
        "keys": data.get("keys") or data.get("keysRaw") or "",
        "kind": data.get("kind") or "exec",
        "payload": data.get("payload") or "",
        "title": data.get("title") or "",
        "detail": data.get("detail") or "",
        "category": data.get("category") or "Custom",
        "flags": data.get("flags") or [],
        "enabled": data.get("enabled", True),
    }


def cmd_list():
    print(json.dumps(binds_payload(), ensure_ascii=False))


def cmd_delete(bid: str):
    store = load_store()
    binds = load_all_binds(store)
    b = find_bind(binds, bid)
    if not b:
        print(json.dumps({"ok": False, "error": "not found"}))
        return
    if b.source == "custom":
        nk = norm_keys(b.keys).lower()
        store["binds"] = [
            x
            for x in store.get("binds", [])
            if x.get("id") != b.id and norm_keys(x.get("keys", "")).lower() != nk
        ]
        store["disabled"] = [
            d for d in store.get("disabled", []) if norm_keys(d).lower() != nk
        ]
    elif b.source == "override":
        ov = store.get("overrides") or {}
        for k, v in list(ov.items()):
            if (
                v.get("id") == b.id
                or norm_keys(k).lower() == norm_keys(b.keys).lower()
                or norm_keys(v.get("keys", "")).lower() == norm_keys(b.keys).lower()
            ):
                ov.pop(k, None)
        store["overrides"] = ov
    else:
        keys = norm_keys(b.keys.replace("[disabled] ", ""))
        nk = keys.lower()
        remove_bind_from_system_lua(b.raw, keys)
        deleted = store.setdefault("deleted", [])
        if keys not in deleted and nk not in {norm_keys(d).lower() for d in deleted}:
            deleted.append(keys)
        store["disabled"] = [
            d for d in store.get("disabled", []) if norm_keys(d).lower() != nk
        ]
        ov = store.get("overrides") or {}
        for k in list(ov.keys()):
            if norm_keys(k).lower() == nk:
                ov.pop(k, None)
        store["overrides"] = ov
    save_store(store)
    print(json.dumps(binds_payload(), ensure_ascii=False))


def cmd_disable(bid: str):
    store = load_store()
    binds = load_all_binds(store)
    b = find_bind(binds, bid)
    if not b:
        print(json.dumps({"ok": False, "error": "not found"}))
        return
    keys = norm_keys(b.keys.replace("[disabled] ", ""))
    nk = keys.lower()
    if b.source == "custom":
        for x in store.get("binds", []):
            if x.get("id") == b.id or norm_keys(x.get("keys", "")).lower() == nk:
                x["enabled"] = False
    disabled = store.setdefault("disabled", [])
    if keys not in disabled and nk not in {norm_keys(d).lower() for d in disabled}:
        disabled.append(keys)
    save_store(store)
    print(json.dumps(binds_payload(), ensure_ascii=False))


def cmd_enable(bid: str):
    store = load_store()
    binds = load_all_binds(store)
    b = find_bind(binds, bid)
    if not b:
        print(json.dumps({"ok": False, "error": "not found"}))
        return
    keys = norm_keys(b.keys.replace("[disabled] ", "")).lower()
    store["disabled"] = [
        d for d in store.get("disabled", []) if norm_keys(d).lower() != keys
    ]
    if b.source == "custom":
        for x in store.get("binds", []):
            if x.get("id") == b.id or norm_keys(x.get("keys", "")).lower() == keys:
                x["enabled"] = True
    save_store(store)
    print(json.dumps(binds_payload(), ensure_ascii=False))


def cmd_save(data: dict | None = None):
    """Create or update a custom bind, or save as override of a system bind."""
    if data is None:
        data = json.loads(sys.stdin.read() or "{}")
    store = load_store()
    entry = entry_from_data(data)
    if not entry["keys"].strip() or not str(entry["payload"]).strip():
        print(json.dumps({"ok": False, "error": "keys and payload required"}))
        return

    mode = data.get("mode") or "custom"
    if mode == "override" or data.get("source") == "system" or data.get("asOverride"):
        base = data.get("baseKeys") or data.get("originalKeys") or entry["keys"]
        base = norm_keys(base)
        store.setdefault("overrides", {})[base] = entry
        save_store(store)
        print(json.dumps(binds_payload(), ensure_ascii=False))
        return

    binds = store.setdefault("binds", [])
    updated = False
    for i, x in enumerate(binds):
        if entry["id"] and x.get("id") == entry["id"]:
            binds[i] = entry
            updated = True
            break
    if not updated:
        prev = data.get("previousKeys")
        if prev:
            pk = norm_keys(prev).lower()
            for i, x in enumerate(binds):
                if norm_keys(x.get("keys", "")).lower() == pk:
                    entry["id"] = x.get("id") or entry["id"]
                    binds[i] = entry
                    updated = True
                    break
    if not updated:
        if not entry["id"]:
            entry["id"] = str(uuid.uuid4())
        binds.append(entry)
    save_store(store)
    print(json.dumps(binds_payload(), ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(
            "usage: cli.py list|delete|disable|enable|save|save-json|add|reload",
            file=sys.stderr,
        )
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "list":
        cmd_list()
    elif cmd == "delete" and len(sys.argv) > 2:
        cmd_delete(sys.argv[2])
    elif cmd == "disable" and len(sys.argv) > 2:
        cmd_disable(sys.argv[2])
    elif cmd == "enable" and len(sys.argv) > 2:
        cmd_enable(sys.argv[2])
    elif cmd in ("save", "add"):
        cmd_save()
    elif cmd == "save-json" and len(sys.argv) > 2:
        cmd_save(json.loads(sys.argv[2]))
    elif cmd == "reload":
        store = load_store()
        write_hypr_user_lua(store)
        print(json.dumps(binds_payload(), ensure_ascii=False))
    else:
        print(json.dumps({"ok": False, "error": "bad command"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
