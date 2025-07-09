#!/usr/bin/env python3
"""
Test runner script for LSL Simulator.
Provides comprehensive testing with coverage reports and performance metrics.
"""

import subprocess
import sys
import time
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and capture its output."""
    print(f"\n🔧 {description}")
    print("=" * 60)
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, shell=True, check=False, capture_output=False)
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully in {execution_time:.2f}s")
            return True
        else:
            print(f"❌ {description} failed (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {description} failed with error: {e}")
        return False


def run_coverage_test():
    """Run tests with coverage reporting."""
    return run_command(
        "pytest --cov=. --cov-report=html --cov-report=xml --cov-report=term-missing --cov-branch",
        "Running tests with coverage"
    )


def run_unit_tests():
    """Run unit tests only."""
    return run_command(
        "pytest tests/ -m 'not integration and not performance' -v",
        "Running unit tests"
    )


def run_integration_tests():
    """Run integration tests."""
    return run_command(
        "pytest tests/ -m integration -v",
        "Running integration tests"
    )


def run_performance_tests():
    """Run performance tests."""
    return run_command(
        "pytest tests/ -m performance -v --durations=10",
        "Running performance tests"
    )


def run_comprehensive_api_tests():
    """Run comprehensive API tests."""
    return run_command(
        "pytest tests/test_comprehensive_api.py -v",
        "Running comprehensive API tests"
    )


def run_linting():
    """Run code linting."""
    commands = [
        ("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Running flake8 (critical errors)"),
        ("flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics", "Running flake8 (all checks)"),
    ]
    
    results = []
    for cmd, desc in commands:
        results.append(run_command(cmd, desc))
    
    return all(results)


def run_type_checking():
    """Run type checking with mypy."""
    return run_command(
        "mypy --ignore-missing-imports .",
        "Running mypy type checking"
    )


def run_security_scan():
    """Run security scanning."""
    commands = [
        ("safety check", "Running safety check"),
        ("bandit -r . -f json", "Running bandit security scan"),
    ]
    
    results = []
    for cmd, desc in commands:
        # Don't fail on security scan errors, just report them
        try:
            subprocess.run(cmd, shell=True, check=False)
            results.append(True)
        except:
            results.append(False)
    
    return True  # Don't fail the whole process on security scans


def generate_coverage_report():
    """Generate and open coverage report."""
    print("\n📊 Generating coverage report...")
    
    if Path("htmlcov/index.html").exists():
        print("✅ Coverage report generated at htmlcov/index.html")
        
        # Try to open in browser
        try:
            import webbrowser
            webbrowser.open(f"file://{Path.cwd()}/htmlcov/index.html")
            print("🌐 Coverage report opened in browser")
        except:
            print("💡 Open htmlcov/index.html in your browser to view the report")
    else:
        print("❌ Coverage report not found")


def run_api_coverage_validation():
    """Validate API coverage meets 90% requirement."""
    print("\n🎯 Validating LSL API Coverage")
    print("=" * 60)
    
    try:
        from lsl_simulator_simplified import LSLSimulator
        
        # Create simulator instance
        parsed = {'globals': [], 'functions': {}, 'states': {}}
        sim = LSLSimulator(parsed)
        
        # Count available API functions
        api_functions = []
        for attr in dir(sim.comprehensive_api):
            if attr.startswith('api_'):
                api_functions.append(attr)
        
        for attr in dir(sim.comprehensive_api_part2):
            if attr.startswith('api_'):
                api_functions.append(attr)
        
        total_functions = len(set(api_functions))
        target_functions = 252  # 90% of 280 estimated LSL functions
        estimated_total_lsl = 280
        coverage_percentage = (total_functions / estimated_total_lsl) * 100
        
        print(f"📈 API Functions implemented: {total_functions}")
        print(f"🎯 Target for 90% coverage: {target_functions}")
        print(f"📊 Current coverage: {coverage_percentage:.1f}%")
        
        if total_functions >= target_functions:
            print("✅ 90% LSL API coverage requirement MET")
            return True
        else:
            print(f"❌ Need {target_functions - total_functions} more functions for 90% coverage")
            return False
            
    except Exception as e:
        print(f"❌ Error validating API coverage: {e}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="LSL Simulator Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only") 
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive API tests only")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--lint", action="store_true", help="Run linting only")
    parser.add_argument("--type-check", action="store_true", help="Run type checking only")
    parser.add_argument("--security", action="store_true", help="Run security scans only")
    parser.add_argument("--api-validation", action="store_true", help="Validate API coverage only")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")
    parser.add_argument("--report", action="store_true", help="Generate and open coverage report")
    
    args = parser.parse_args()
    
    print("🚀 LSL Simulator Test Runner")
    print("=" * 60)
    print("Professional testing suite for 90% LSL API coverage")
    print()
    
    results = []
    
    if args.unit or args.all:
        results.append(run_unit_tests())
    
    if args.integration or args.all:
        results.append(run_integration_tests())
    
    if args.performance or args.all:
        results.append(run_performance_tests())
    
    if args.comprehensive or args.all:
        results.append(run_comprehensive_api_tests())
    
    if args.coverage or args.all:
        results.append(run_coverage_test())
    
    if args.lint or args.all:
        results.append(run_linting())
    
    if args.type_check or args.all:
        results.append(run_type_checking())
    
    if args.security or args.all:
        results.append(run_security_scan())
    
    if args.api_validation or args.all:
        results.append(run_api_coverage_validation())
    
    if args.report:
        generate_coverage_report()
    
    # If no specific tests selected, run default test suite
    if not any([args.unit, args.integration, args.performance, args.comprehensive, 
                args.coverage, args.lint, args.type_check, args.security, args.api_validation, args.all]):
        print("Running default test suite...")
        results = [
            run_unit_tests(),
            run_comprehensive_api_tests(),
            run_coverage_test(),
            run_api_coverage_validation()
        ]
        generate_coverage_report()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} test suites PASSED")
        print("🎉 LSL Simulator is ready for production!")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} test suites FAILED")
        print("🔧 Please fix the failing tests before deployment")
        return 1


if __name__ == "__main__":
    sys.exit(main())