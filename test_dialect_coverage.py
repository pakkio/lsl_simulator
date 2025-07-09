#!/usr/bin/env python3
"""
Test script to validate LSL dialect coverage
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lsl_dialect import LSLDialect, set_dialect, get_function_count, get_dialect_info
from lsl_expanded_api import LSLExpandedAPI

def test_dialect_coverage():
    """Test function coverage for both dialects"""
    print("=== LSL DIALECT COVERAGE TEST ===")
    print()
    
    # Test OpenSimulator dialect
    set_dialect(LSLDialect.OPENSIMULATOR)
    os_info = get_dialect_info()
    os_count = get_function_count()
    
    print(f"OpenSimulator (OS) Dialect:")
    print(f"  Functions available: {os_count}")
    print(f"  Target: 256 functions (realistic OS total)")
    print(f"  Progress: {os_count}/256 ({os_count/256*100:.1f}%)")
    print(f"  Status: {'✅ TARGET REACHED' if os_count >= 256 else '⚠️ MORE NEEDED'}")
    print()
    
    # Test Second Life dialect  
    set_dialect(LSLDialect.SECONDLIFE)
    sl_info = get_dialect_info()
    sl_count = get_function_count()
    
    print(f"Second Life (SL) Dialect:")
    print(f"  Functions available: {sl_count}")
    print(f"  Target: 476 functions (90% of 529)")
    print(f"  Progress: {sl_count}/476 ({sl_count/476*100:.1f}%)")
    print(f"  Status: {'✅ TARGET REACHED' if sl_count >= 476 else '⚠️ MORE NEEDED'}")
    print()
    
    # Show detailed breakdown
    print("=== DETAILED BREAKDOWN ===")
    print(f"OpenSimulator:")
    print(f"  Core functions: {os_info['core_functions']}")
    print(f"  OS-specific: {os_info['specific_functions']}")
    print(f"  Total: {os_info['total_functions']}")
    print()
    
    print(f"Second Life:")
    print(f"  Core functions: {sl_info['core_functions']}")
    print(f"  SL-specific: {sl_info['specific_functions']}")
    print(f"  Total: {sl_info['total_functions']}")
    print()
    
    # Overall summary
    print("=== SUMMARY ===")
    print(f"✅ OpenSimulator: {os_count >= 256}")
    print(f"✅ Second Life: {sl_count >= 476}")
    print(f"✅ Dialect system: Working")
    print()
    
    if os_count >= 256 and sl_count >= 476:
        print("🎉 ALL TARGETS ACHIEVED!")
        print("   - Realistic OpenSimulator coverage")
        print("   - 90% Second Life coverage")
        print("   - Dialect switching functional")
        return True
    else:
        print("⚠️ TARGETS NOT YET REACHED")
        print(f"   - OpenSimulator needs: {max(0, 256 - os_count)} more functions")
        print(f"   - Second Life needs: {max(0, 476 - sl_count)} more functions")
        return False

def test_api_integration():
    """Test that the expanded API integrates properly"""
    print("\n=== API INTEGRATION TEST ===")
    
    try:
        # Test with mock simulator
        class MockSimulator:
            def __init__(self):
                self.global_scope = type('obj', (object,), {})()
                self.global_scope.locals = {}
        
        mock_sim = MockSimulator()
        
        # Test OpenSimulator API
        set_dialect(LSLDialect.OPENSIMULATOR)
        os_api = LSLExpandedAPI(mock_sim)
        print("✅ OpenSimulator API initialized successfully")
        
        # Test Second Life API
        set_dialect(LSLDialect.SECONDLIFE)
        sl_api = LSLExpandedAPI(mock_sim)
        print("✅ Second Life API initialized successfully")
        
        print("✅ API integration working correctly")
        return True
        
    except Exception as e:
        print(f"❌ API integration failed: {e}")
        return False

if __name__ == "__main__":
    success = test_dialect_coverage()
    api_success = test_api_integration()
    
    if success and api_success:
        print("\n🎯 ALL TESTS PASSED - DIALECT SYSTEM READY!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED - NEEDS MORE WORK")
        sys.exit(1)