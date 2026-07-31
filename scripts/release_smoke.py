#!/usr/bin/env python3
"""Read-only production smoke checks for Panacea web and API releases."""
from __future__ import annotations

import argparse
import json
import ssl
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin


@dataclass(frozen=True)
class Response:
    status: int
    content_type: str
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def _url(base: str, path: str) -> str:
    return urljoin(f"{base.rstrip('/')}/", path.lstrip("/"))


def fetch(url: str, timeout: float) -> Response:
    """Fetch a public URL with normal browser-grade TLS verification."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "PanaceaReleaseSmoke/1.0"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return Response(
                status=response.status,
                content_type=response.headers.get("Content-Type", ""),
                body=response.read(),
            )
    except urllib.error.HTTPError as exc:
        try:
            return Response(
                status=exc.code,
                content_type=exc.headers.get("Content-Type", ""),
                body=exc.read(),
            )
        finally:
            exc.close()


def _matches_sha(actual: str, expected: str) -> bool:
    return actual == expected or actual.startswith(expected) or expected.startswith(actual)


def _get(
    name: str,
    base: str,
    path: str,
    timeout: float,
    expected_status: int,
    expected_type: str,
) -> tuple[Check, Response | None]:
    url = _url(base, path)
    try:
        response = fetch(url, timeout)
    except (OSError, ssl.SSLError, urllib.error.URLError) as exc:
        return Check(name, False, f"{url}: {type(exc).__name__}: {exc}"), None

    if response.status != expected_status:
        return (
            Check(name, False, f"{url}: expected HTTP {expected_status}, got {response.status}"),
            response,
        )
    if expected_type not in response.content_type.lower():
        return (
            Check(
                name,
                False,
                f"{url}: expected {expected_type} content, got "
                f"{response.content_type or 'no Content-Type'}",
            ),
            response,
        )
    return Check(name, True, f"{url}: HTTP {response.status}"), response


def _json_check(
    name: str,
    base: str,
    path: str,
    timeout: float,
    expected_status: int = 200,
) -> tuple[Check, dict[str, Any] | None]:
    check, response = _get(
        name,
        base,
        path,
        timeout,
        expected_status=expected_status,
        expected_type="application/json",
    )
    if not check.ok or response is None:
        return check, None
    try:
        payload = response.json()
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return Check(name, False, f"{_url(base, path)}: invalid JSON: {exc}"), None
    if not isinstance(payload, dict):
        return Check(name, False, f"{_url(base, path)}: expected a JSON object"), None
    return check, payload


def run_checks(
    frontend_url: str,
    api_url: str,
    timeout: float = 10.0,
    expected_sha: str | None = None,
    require_payments: bool = False,
) -> list[Check]:
    """Run public, read-only checks without creating users or payment sessions."""
    checks: list[Check] = []

    frontend_check, frontend = _get(
        "frontend",
        frontend_url,
        "/",
        timeout,
        expected_status=200,
        expected_type="text/html",
    )
    if frontend_check.ok and frontend is not None and b"Panacea" not in frontend.body:
        frontend_check = Check(
            "frontend",
            False,
            f"{_url(frontend_url, '/')}: HTML does not identify Panacea",
        )
    checks.append(frontend_check)

    web_build_check, web_build = _json_check(
        "frontend-build-metadata",
        frontend_url,
        "/build.json",
        timeout,
    )
    checks.append(web_build_check)

    health_check, health = _json_check("api-health", api_url, "/health", timeout)
    if health_check.ok and health is not None and health.get("status") != "ok":
        health_check = Check("api-health", False, "API health payload does not report status=ok")
    checks.append(health_check)

    api_build_check, api_build = _json_check(
        "api-build-metadata",
        api_url,
        "/api/version",
        timeout,
    )
    checks.append(api_build_check)

    for name, path in (
        ("auth-protection", "/auth/me"),
        ("document-protection", "/api/documents"),
        ("usage-protection", "/api/user/usage"),
    ):
        check, _ = _json_check(name, api_url, path, timeout, expected_status=401)
        checks.append(check)

    plans_check, plans = _json_check(
        "billing-plans",
        api_url,
        "/api/payments/plans",
        timeout,
    )
    if plans_check.ok and plans is not None:
        plan_rows = plans.get("plans")
        if not isinstance(plan_rows, list):
            plans_check = Check("billing-plans", False, "Billing payload has no plans list")
        elif require_payments and not any(
            isinstance(plan, dict) and plan.get("available") for plan in plan_rows
        ):
            plans_check = Check(
                "billing-plans",
                False,
                "No paid plan is configured; expected at least one available Stripe price",
            )
    checks.append(plans_check)

    if expected_sha:
        for name, payload in (
            ("frontend-expected-commit", web_build),
            ("api-expected-commit", api_build),
        ):
            actual = payload.get("commit") if payload else None
            ok = isinstance(actual, str) and _matches_sha(actual, expected_sha)
            checks.append(
                Check(
                    name,
                    ok,
                    f"expected {expected_sha}, got {actual or 'unavailable'}",
                )
            )

    return checks


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frontend-url", required=True)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--expected-sha")
    parser.add_argument("--require-payments", action="store_true")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json", action="store_true", dest="json_output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    checks = run_checks(
        frontend_url=args.frontend_url,
        api_url=args.api_url,
        timeout=args.timeout,
        expected_sha=args.expected_sha,
        require_payments=args.require_payments,
    )
    if args.json_output:
        print(json.dumps([asdict(check) for check in checks], indent=2))
    else:
        for check in checks:
            marker = "PASS" if check.ok else "FAIL"
            print(f"[{marker}] {check.name}: {check.detail}")
        passed = sum(check.ok for check in checks)
        print(f"\n{passed}/{len(checks)} checks passed")
    return 0 if all(check.ok for check in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
