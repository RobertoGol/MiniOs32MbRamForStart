# -*- coding: utf-8 -*-
"""G1: host-side parser/validator for CtOS SD shell/item manifests.

Format: UTF-8 text, line-based key=value.
- Empty lines ignored.
- Lines starting with '#' (after optional whitespace) are comments.
- Each non-empty, non-comment line must contain '='.
- Keys and values are stripped of surrounding ASCII spaces/tabs.
- Duplicate keys are rejected.
- Unknown keys are rejected (strict; forward-compatible format versions can add keys).
- Paths are relative POSIX-style paths: no empty path, no absolute path, no '\\',
  no NUL, no leading/trailing '/', no '.' or '..' segments.

This is a host-side reference validator for G1. Runtime/native parsing can reuse
the same rules later.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict, Iterable, List, Optional, Tuple


class ManifestError(ValueError):
    pass


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,63}$")
_HASH_RE = re.compile(r"^(sha256:[0-9a-f]{64}|crc32:[0-9A-Fa-f]{8})$")

SHELL_FORMAT = "ctos-shell-1"
ITEM_FORMAT = "ctos-item-1"

SHELL_REQUIRED = ("format", "id", "name", "version", "min_ctos", "payload")
SHELL_OPTIONAL = ("entry", "hash")
SHELL_ALLOWED = set(SHELL_REQUIRED + SHELL_OPTIONAL)

ITEM_REQUIRED = ("format", "id", "type", "name", "content")
ITEM_OPTIONAL = ("version", "size", "installable")
ITEM_ALLOWED = set(ITEM_REQUIRED + ITEM_OPTIONAL)

ITEM_TYPES = {"game", "mod", "video", "photo", "ai", "app", "other"}
BOOL_VALUES = {"0": False, "1": True, "false": False, "true": True, "no": False, "yes": True}


@dataclass
class ShellManifest:
    format: str
    id: str
    name: str
    version: str
    min_ctos: str
    payload: str
    entry: Optional[str] = None
    hash: Optional[str] = None


@dataclass
class ItemManifest:
    format: str
    id: str
    type: str
    name: str
    content: str
    version: Optional[str] = None
    size: Optional[int] = None
    installable: Optional[bool] = None


def parse_manifest_text(text: str, source: str = "<manifest>") -> Dict[str, str]:
    if "\x00" in text:
        raise ManifestError(f"{source}: NUL byte is not allowed")
    data: Dict[str, str] = {}
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.strip(" \t\r\n")
        if not line or line.lstrip().startswith("#"):
            continue
        if "=" not in raw:
            raise ManifestError(f"{source}:{lineno}: expected key=value")
        key, value = raw.split("=", 1)
        key = key.strip(" \t")
        value = value.strip(" \t\r")
        if not key:
            raise ManifestError(f"{source}:{lineno}: empty key")
        if not re.match(r"^[A-Za-z0-9_.-]+$", key):
            raise ManifestError(f"{source}:{lineno}: invalid key '{key}'")
        if key in data:
            raise ManifestError(f"{source}:{lineno}: duplicate key '{key}'")
        data[key] = value
    return data


def _require(data: Dict[str, str], keys: Iterable[str], source: str) -> None:
    for k in keys:
        if k not in data:
            raise ManifestError(f"{source}: missing required key '{k}'")
        if data[k] == "":
            raise ManifestError(f"{source}: empty value for '{k}'")


def _reject_unknown(data: Dict[str, str], allowed: set, source: str) -> None:
    for k in data:
        if k not in allowed:
            raise ManifestError(f"{source}: unknown key '{k}'")


def _validate_id(value: str, source: str, field: str = "id") -> None:
    if not _ID_RE.match(value):
        raise ManifestError(f"{source}: invalid {field} '{value}'")


def _validate_version(value: str, source: str, field: str) -> None:
    if not _VERSION_RE.match(value):
        raise ManifestError(f"{source}: invalid {field} '{value}'")


def _validate_name(value: str, source: str, field: str = "name") -> None:
    if not value or len(value) > 80:
        raise ManifestError(f"{source}: invalid {field} length")
    if any(c in value for c in "\r\n\t\x00"):
        raise ManifestError(f"{source}: invalid control char in {field}")


def _validate_relpath(value: str, source: str, field: str) -> None:
    if not value or len(value) > 160:
        raise ManifestError(f"{source}: invalid {field} length")
    if "\\" in value or value.startswith("/") or value.endswith("/"):
        raise ManifestError(f"{source}: invalid {field} path '{value}'")
    if ":" in value.split("/")[0]:
        raise ManifestError(f"{source}: invalid {field} path '{value}'")
    for seg in value.split("/"):
        if seg in ("", ".", ".."):
            raise ManifestError(f"{source}: invalid {field} path segment in '{value}'")
        if any(ord(c) < 32 or c == "\x7f" for c in seg):
            raise ManifestError(f"{source}: invalid control char in {field}")


def _validate_hash(value: str, source: str) -> None:
    if not _HASH_RE.match(value):
        raise ManifestError(f"{source}: invalid hash '{value}'")


def _validate_size(value: str, source: str) -> int:
    if not re.match(r"^[0-9]{1,20}$", value):
        raise ManifestError(f"{source}: invalid size '{value}'")
    n = int(value, 10)
    if n < 0:
        raise ManifestError(f"{source}: invalid size '{value}'")
    return n


def _validate_bool(value: str, source: str, field: str) -> bool:
    key = value.strip().lower()
    if key not in BOOL_VALUES:
        raise ManifestError(f"{source}: invalid {field} '{value}'")
    return BOOL_VALUES[key]


def validate_shell_manifest(data: Dict[str, str], source: str = "<shell.manifest>") -> ShellManifest:
    _reject_unknown(data, SHELL_ALLOWED, source)
    _require(data, SHELL_REQUIRED, source)
    if data["format"] != SHELL_FORMAT:
        raise ManifestError(f"{source}: unsupported format '{data['format']}'")
    _validate_id(data["id"], source)
    _validate_name(data["name"], source)
    _validate_version(data["version"], source, "version")
    _validate_version(data["min_ctos"], source, "min_ctos")
    _validate_relpath(data["payload"], source, "payload")
    entry = data.get("entry")
    if entry is not None:
        if entry == "":
            raise ManifestError(f"{source}: empty value for 'entry'")
        _validate_name(entry, source, "entry")
    hashv = data.get("hash")
    if hashv is not None:
        if hashv == "":
            raise ManifestError(f"{source}: empty value for 'hash'")
        _validate_hash(hashv, source)
    return ShellManifest(
        format=data["format"],
        id=data["id"],
        name=data["name"],
        version=data["version"],
        min_ctos=data["min_ctos"],
        payload=data["payload"],
        entry=entry,
        hash=hashv,
    )


def validate_item_manifest(data: Dict[str, str], source: str = "<item.manifest>") -> ItemManifest:
    _reject_unknown(data, ITEM_ALLOWED, source)
    _require(data, ITEM_REQUIRED, source)
    if data["format"] != ITEM_FORMAT:
        raise ManifestError(f"{source}: unsupported format '{data['format']}'")
    _validate_id(data["id"], source)
    if data["type"] not in ITEM_TYPES:
        raise ManifestError(f"{source}: invalid type '{data['type']}'")
    _validate_name(data["name"], source)
    _validate_relpath(data["content"], source, "content")
    version = data.get("version")
    if version is not None:
        if version == "":
            raise ManifestError(f"{source}: empty value for 'version'")
        _validate_version(version, source, "version")
    size = None
    if "size" in data:
        size = _validate_size(data["size"], source)
    installable = None
    if "installable" in data:
        installable = _validate_bool(data["installable"], source, "installable")
    return ItemManifest(
        format=data["format"],
        id=data["id"],
        type=data["type"],
        name=data["name"],
        content=data["content"],
        version=version,
        size=size,
        installable=installable,
    )


def load_shell_manifest(path: str) -> ShellManifest:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return validate_shell_manifest(parse_manifest_text(text, path), path)


def load_item_manifest(path: str) -> ItemManifest:
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return validate_item_manifest(parse_manifest_text(text, path), path)
