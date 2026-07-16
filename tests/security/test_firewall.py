from __future__ import annotations

import importlib.util
from pathlib import Path


def load_firewall_module():
    module_path = Path(".claude/hooks/security_firewall_v2.py")
    spec = importlib.util.spec_from_file_location("security_firewall_v2", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def test_blocks_dangerous_command() -> None:
    firewall_module = load_firewall_module()
    firewall = firewall_module.SecurityFirewall()

    result = firewall.process('{"tool_name":"Bash","params":{"command":"rm -rf /"}}')

    assert result["block"] is True


def test_allows_safe_write() -> None:
    firewall_module = load_firewall_module()
    firewall = firewall_module.SecurityFirewall()

    result = firewall.process(
        '{"tool_name":"Write","params":{"path":"frontend/src/App.tsx","content":"export default 1;"}}'
    )

    assert result["block"] is False
