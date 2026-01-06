#!/usr/bin/env python3
"""Quality verification script for WhatsApp Song Scanner."""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and report results."""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=".",
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)

        return result.returncode == 0
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Run all quality checks."""
    print("\n🚀 WhatsApp Song Scanner - Quality Verification")
    print("=" * 60)
    
    checks = [
        (
            "python -m flake8 src config --config=setup.cfg --count",
            "Flake8 Linting Check (should be 0 errors)"
        ),
        (
            "python -m pytest tests/ -q --tb=no",
            "Test Suite (should be 32 passed)"
        ),
        (
            "python -c \"import datetime; print(f'Python {__import__(\\\"sys\\\").version_info.major}.{__import__(\\\"sys\\\").version_info.minor} - timezone support: {hasattr(datetime, \\\"timezone\\\")}')\"",
            "Python Version & Timezone Support"
        ),
    ]
    
    results = []
    for cmd, desc in checks:
        success = run_command(cmd, desc)
        results.append((desc, success))
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    for desc, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {desc}")
    
    all_passed = all(success for _, success in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - CODEBASE IS PRODUCTION READY!")
    else:
        print("⚠️ SOME CHECKS FAILED - REVIEW ABOVE")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
