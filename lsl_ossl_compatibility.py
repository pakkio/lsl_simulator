#!/usr/bin/env python3
"""
LSL/OSSL Compatibility Layer
Manages differences between LSL (Second Life) and OSSL (OpenSimulator) implementations
"""

import uuid
import time as time_module
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from lsl_api_expanded import LSLAPIExpanded

class SimulatorMode(Enum):
    """Simulator compatibility modes"""
    LSL_STRICT = "lsl"           # Pure Second Life LSL compliance
    OSSL_EXTENDED = "ossl"       # OpenSimulator with OSSL extensions
    HYBRID = "hybrid"            # Best effort compatibility with both

class CompatibilityLevel(Enum):
    """Function compatibility levels"""
    LSL_ONLY = "lsl_only"        # Only available in LSL
    OSSL_ONLY = "ossl_only"      # Only available in OSSL
    BOTH = "both"                # Available in both
    DIFFERS = "differs"          # Available in both but behaves differently

class LSLOSSLCompatibility(LSLAPIExpanded):
    """Extended LSL API with OSSL compatibility and mode switching"""
    
    def __init__(self, mode: SimulatorMode = SimulatorMode.HYBRID):
        super().__init__()
        self.mode = mode
        self.compatibility_info = {}
        self._register_ossl_functions()
        self._register_compatibility_matrix()
    
    def set_mode(self, mode: SimulatorMode):
        """Switch simulator compatibility mode"""
        self.mode = mode
        print(f"Simulator mode changed to: {mode.value}")
    
    def get_mode(self) -> SimulatorMode:
        """Get current simulator mode"""
        return self.mode
    
    def call_function(self, name: str, args: List[Any]) -> Any:
        """Call function with compatibility checking"""
        # Check if function exists
        if name not in self.functions:
            print(f"Warning: Function {name} not implemented")
            return None
        
        # Check compatibility
        compat_info = self.compatibility_info.get(name, {})
        compat_level = compat_info.get('level', CompatibilityLevel.BOTH)
        
        # Enforce mode restrictions
        if self.mode == SimulatorMode.LSL_STRICT:
            if compat_level == CompatibilityLevel.OSSL_ONLY:
                print(f"Error: Function {name} not available in LSL_STRICT mode")
                return None
        elif self.mode == SimulatorMode.OSSL_EXTENDED:
            if compat_level == CompatibilityLevel.LSL_ONLY:
                print(f"Warning: Function {name} is LSL-specific, may not work in OpenSim")
        
        # Handle behavioral differences
        if compat_level == CompatibilityLevel.DIFFERS:
            return self._call_function_with_mode_differences(name, args)
        
        # Call normally
        return super().call_function(name, args)
    
    def _call_function_with_mode_differences(self, name: str, args: List[Any]) -> Any:
        """Handle functions that behave differently between LSL and OSSL"""
        if name == "llGetObjectDetails":
            return self._llGetObjectDetails_compatible(args)
        elif name == "llHTTPRequest":
            return self._llHTTPRequest_compatible(args)
        elif name == "llParseString2List":
            return self._llParseString2List_compatible(args)
        else:
            # Default to base implementation
            return super().call_function(name, args)
    
    def _llGetObjectDetails_compatible(self, args) -> Any:
        """LSL/OSSL compatible version of llGetObjectDetails"""
        if len(args) < 2:
            return []
        
        key, params = args[0], args[1]
        
        if self.mode == SimulatorMode.LSL_STRICT:
            # LSL version: more restrictive, some params not supported
            lsl_supported_params = [1, 2, 3, 4, 5, 6, 7, 8]  # Basic object details
            filtered_params = [p for p in params if p in lsl_supported_params]
            return super().call_function('llGetObjectDetails', [key, filtered_params])
        else:
            # OSSL version: supports additional parameters
            return super().call_function('llGetObjectDetails', args)
    
    def _llHTTPRequest_compatible(self, args) -> Any:
        """LSL/OSSL compatible version of llHTTPRequest"""
        if len(args) < 3:
            return ""
        
        url, headers, body = args[0], args[1], args[2]
        
        if self.mode == SimulatorMode.LSL_STRICT:
            # LSL version: stricter URL validation, header limitations
            if not url.startswith(('http://', 'https://')):
                print("Error: LSL only supports HTTP/HTTPS URLs")
                return ""
            
            # LSL has a 2048 character limit on HTTP body
            if len(str(body)) > 2048:
                print("Warning: HTTP body truncated to 2048 characters (LSL limit)")
                body = str(body)[:2048]
        
        return super().call_function('llHTTPRequest', [url, headers, body])
    
    def _llParseString2List_compatible(self, args) -> Any:
        """LSL/OSSL compatible version of llParseString2List"""
        if len(args) < 3:
            return []
        
        string, separators, spacers = args[0], args[1], args[2]
        
        if self.mode == SimulatorMode.OSSL_EXTENDED:
            # OSSL supports regex separators (enhancement)
            # This is a simulated enhancement for demonstration
            return super().call_function('llParseString2List', args)
        else:
            # LSL standard behavior
            return super().call_function('llParseString2List', args)
    
    def _register_ossl_functions(self):
        """Register OSSL-specific functions"""
        
        # OSSL-only functions
        def osSetSpeed(speed):
            """OSSL: Set avatar movement speed"""
            print(f"OSSL: Set speed to {speed}")
            return speed
        
        def osGetRegionStats():
            """OSSL: Get region performance statistics"""
            return {
                'time_dilation': 0.99,
                'sim_fps': 45.2,
                'physics_fps': 45.1,
                'agent_updates': 22.1,
                'root_agents': 5,
                'child_agents': 0,
                'total_prims': 1523,
                'active_prims': 156,
                'frame_ms': 22.1,
                'net_ms': 0.8,
                'physics_ms': 3.2,
                'image_ms': 0.1,
                'other_ms': 2.1,
                'script_ms': 15.9
            }
        
        def osMessageObject(key, message):
            """OSSL: Send message to object via key"""
            print(f"OSSL: Message to {key}: {message}")
            return 1
        
        def osGetNotecard(name):
            """OSSL: Read entire notecard content"""
            # Simulate notecard content
            return f"This is the content of notecard: {name}"
        
        def osSetDynamicTextureURL(face, contentType, url, extraParams, timer):
            """OSSL: Set dynamic texture from URL"""
            print(f"OSSL: Set dynamic texture on face {face} from {url}")
            return str(uuid.uuid4())
        
        def osConsoleCommand(command):
            """OSSL: Execute console command"""
            print(f"OSSL: Console command: {command}")
            return f"Executed: {command}"
        
        def osGetSimulatorVersion():
            """OSSL: Get OpenSimulator version"""
            return "OpenSimulator 0.9.2.2 (Python Simulator)"
        
        def osGetAvatarList():
            """OSSL: Get list of avatars in region"""
            return [
                {'name': 'John Doe', 'key': str(uuid.uuid4()), 'position': (128.0, 128.0, 22.0)},
                {'name': 'Jane Smith', 'key': str(uuid.uuid4()), 'position': (100.0, 150.0, 22.0)}
            ]
        
        def osSetParcelDetails(position, rules):
            """OSSL: Set parcel details"""
            print(f"OSSL: Set parcel details at {position}: {rules}")
            return True
        
        def osGetDrawStringSize(text, fontName, fontSize):
            """OSSL: Calculate text rendering dimensions"""
            # Simulate text size calculation
            char_width = fontSize * 0.6
            char_height = fontSize
            return (len(text) * char_width, char_height)
        
        # Register OSSL functions
        ossl_funcs = {
            'osSetSpeed': osSetSpeed,
            'osGetRegionStats': osGetRegionStats,
            'osMessageObject': osMessageObject,
            'osGetNotecard': osGetNotecard,
            'osSetDynamicTextureURL': osSetDynamicTextureURL,
            'osConsoleCommand': osConsoleCommand,
            'osGetSimulatorVersion': osGetSimulatorVersion,
            'osGetAvatarList': osGetAvatarList,
            'osSetParcelDetails': osSetParcelDetails,
            'osGetDrawStringSize': osGetDrawStringSize
        }
        self.functions.update(ossl_funcs)
    
    def _register_compatibility_matrix(self):
        """Register function compatibility information"""
        self.compatibility_info = {
            # LSL Standard Functions
            'llSay': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llOwnerSay': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llHTTPRequest': {'level': CompatibilityLevel.DIFFERS, 'notes': 'URL restrictions differ'},
            'llGetObjectDetails': {'level': CompatibilityLevel.DIFFERS, 'notes': 'OSSL supports more parameters'},
            'llParseString2List': {'level': CompatibilityLevel.DIFFERS, 'notes': 'OSSL may support regex'},
            'llSetText': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llSensor': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llListen': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llInstantMessage': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llGetKey': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llGetOwner': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llResetScript': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            
            # Math Functions
            'llAbs': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llSqrt': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llSin': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            'llCos': {'level': CompatibilityLevel.BOTH, 'notes': 'Works identically'},
            
            # OSSL-only Functions
            'osSetSpeed': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osGetRegionStats': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osMessageObject': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osGetNotecard': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osSetDynamicTextureURL': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osConsoleCommand': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osGetSimulatorVersion': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osGetAvatarList': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osSetParcelDetails': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
            'osGetDrawStringSize': {'level': CompatibilityLevel.OSSL_ONLY, 'notes': 'OpenSimulator extension'},
        }
    
    def get_compatibility_info(self, function_name: str) -> Dict[str, Any]:
        """Get compatibility information for a function"""
        return self.compatibility_info.get(function_name, {
            'level': CompatibilityLevel.BOTH,
            'notes': 'No specific compatibility information'
        })
    
    def list_functions_by_compatibility(self, level: CompatibilityLevel) -> List[str]:
        """List functions by compatibility level"""
        return [
            func_name for func_name, info in self.compatibility_info.items()
            if info.get('level') == level
        ]
    
    def validate_script_compatibility(self, function_names: List[str]) -> Dict[str, Any]:
        """Validate a script's compatibility with current mode"""
        issues = []
        warnings = []
        compatible_functions = []
        
        for func_name in function_names:
            if func_name not in self.functions:
                issues.append(f"Function {func_name} not implemented")
                continue
            
            compat_info = self.get_compatibility_info(func_name)
            compat_level = compat_info.get('level', CompatibilityLevel.BOTH)
            
            if self.mode == SimulatorMode.LSL_STRICT:
                if compat_level == CompatibilityLevel.OSSL_ONLY:
                    issues.append(f"Function {func_name} not available in LSL_STRICT mode")
                elif compat_level == CompatibilityLevel.DIFFERS:
                    warnings.append(f"Function {func_name} may behave differently in LSL")
                else:
                    compatible_functions.append(func_name)
            elif self.mode == SimulatorMode.OSSL_EXTENDED:
                if compat_level == CompatibilityLevel.LSL_ONLY:
                    warnings.append(f"Function {func_name} is LSL-specific")
                else:
                    compatible_functions.append(func_name)
            else:  # HYBRID mode
                compatible_functions.append(func_name)
                if compat_level == CompatibilityLevel.DIFFERS:
                    warnings.append(f"Function {func_name} behaves differently between LSL/OSSL")
        
        return {
            'mode': self.mode.value,
            'total_functions': len(function_names),
            'compatible_functions': len(compatible_functions),
            'issues': issues,
            'warnings': warnings,
            'compatibility_score': len(compatible_functions) / len(function_names) * 100 if function_names else 0
        }
    
    def generate_compatibility_report(self) -> str:
        """Generate a comprehensive compatibility report"""
        report = []
        report.append("=" * 60)
        report.append("LSL/OSSL COMPATIBILITY REPORT")
        report.append("=" * 60)
        report.append(f"Current Mode: {self.mode.value}")
        report.append(f"Total Functions: {len(self.functions)}")
        
        # Count by compatibility level
        both_count = len(self.list_functions_by_compatibility(CompatibilityLevel.BOTH))
        lsl_only_count = len(self.list_functions_by_compatibility(CompatibilityLevel.LSL_ONLY))
        ossl_only_count = len(self.list_functions_by_compatibility(CompatibilityLevel.OSSL_ONLY))
        differs_count = len(self.list_functions_by_compatibility(CompatibilityLevel.DIFFERS))
        
        report.append(f"\nCompatibility Breakdown:")
        report.append(f"  Both LSL/OSSL: {both_count}")
        report.append(f"  LSL Only: {lsl_only_count}")
        report.append(f"  OSSL Only: {ossl_only_count}")
        report.append(f"  Differs: {differs_count}")
        
        # Calculate compatibility percentages
        total_with_info = both_count + lsl_only_count + ossl_only_count + differs_count
        if total_with_info > 0:
            lsl_compat = (both_count + lsl_only_count + differs_count) / total_with_info * 100
            ossl_compat = (both_count + ossl_only_count + differs_count) / total_with_info * 100
            
            report.append(f"\nCompatibility Scores:")
            report.append(f"  LSL Compatibility: {lsl_compat:.1f}%")
            report.append(f"  OSSL Compatibility: {ossl_compat:.1f}%")
        
        # List OSSL-only functions
        ossl_funcs = self.list_functions_by_compatibility(CompatibilityLevel.OSSL_ONLY)
        if ossl_funcs:
            report.append(f"\nOSSL-Only Functions ({len(ossl_funcs)}):")
            for func in sorted(ossl_funcs):
                report.append(f"  • {func}")
        
        return "\n".join(report)

def test_compatibility_system():
    """Test the LSL/OSSL compatibility system"""
    print("🔧 Testing LSL/OSSL Compatibility System")
    print("=" * 50)
    
    # Test different modes
    for mode in SimulatorMode:
        print(f"\n🎯 Testing {mode.value} mode:")
        
        api = LSLOSSLCompatibility(mode)
        
        # Test LSL function
        result = api.call_function('llSay', [0, 'Hello World'])
        print(f"  llSay result: {result}")
        
        # Test OSSL function
        result = api.call_function('osGetSimulatorVersion', [])
        print(f"  osGetSimulatorVersion result: {result}")
        
        # Test function with differences
        result = api.call_function('llHTTPRequest', ['https://example.com', [], 'test'])
        print(f"  llHTTPRequest result: {result}")
    
    # Test script compatibility validation
    print(f"\n📊 Script Compatibility Validation:")
    
    api = LSLOSSLCompatibility(SimulatorMode.HYBRID)
    test_script_functions = [
        'llSay', 'llHTTPRequest', 'osGetRegionStats', 'llGetObjectDetails', 'osSetSpeed'
    ]
    
    validation = api.validate_script_compatibility(test_script_functions)
    print(f"  Functions tested: {validation['total_functions']}")
    print(f"  Compatible: {validation['compatible_functions']}")
    print(f"  Compatibility score: {validation['compatibility_score']:.1f}%")
    
    if validation['issues']:
        print(f"  Issues: {validation['issues']}")
    if validation['warnings']:
        print(f"  Warnings: {validation['warnings']}")
    
    # Generate full report
    print(f"\n📋 Full Compatibility Report:")
    print(api.generate_compatibility_report())

if __name__ == "__main__":
    test_compatibility_system()