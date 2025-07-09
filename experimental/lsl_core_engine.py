#!/usr/bin/env python3
"""
LSL Core Execution Engine
Handles the core execution logic separated from API and debug features
"""

import threading
import time
from typing import Any, Dict, List, Optional, Set
from .lsl_antlr_parser import LSLParser, LSLScript, LSLStatement, LSLExpression
from .lsl_simple_evaluator import LSLSimpleEvaluator

class Frame:
    """Call stack frame for local variables"""
    def __init__(self, parent_scope=None):
        self.locals = {}
        self.parent = parent_scope
    
    def get(self, name: str) -> Any:
        return self.locals.get(name)
    
    def set(self, name: str, value: Any):
        self.locals[name] = value

class CallStack:
    """Manages the call stack for function calls"""
    def __init__(self, global_scope: Frame):
        self.frames = []
        self.global_scope = global_scope
    
    def push(self, frame: Frame):
        self.frames.append(frame)
    
    def pop(self) -> Optional[Frame]:
        return self.frames.pop() if self.frames else None
    
    def get_current_scope(self) -> Frame:
        return self.frames[-1] if self.frames else self.global_scope
    
    def find_variable(self, name: str) -> Any:
        current = self.get_current_scope()
        while current:
            val = current.get(name)
            if val is not None:
                return val
            current = getattr(current, 'parent', None)
        return None

class LSLCoreEngine:
    """Core LSL execution engine without debug/API features"""
    
    def __init__(self, script_source: str):
        self.parser = LSLParser()
        self.ast = self.parser.parse(script_source)
        self.evaluator = LSLSimpleEvaluator(self)
        
        # Execution state
        self.global_scope = Frame()
        self.call_stack = CallStack(self.global_scope)
        self.current_state = "default"
        self.event_queue = []
        self._is_running = True
        
        # Initialize globals
        self._initialize_globals()
        
        # API registry
        self.api_functions = {}
        self._register_built_in_functions()
    
    def _initialize_globals(self):
        """Initialize global variables and constants"""
        # LSL constants
        constants = {
            "PI": 3.141592653589793,
            "PI_BY_TWO": 1.5707963267948966,
            "TWO_PI": 6.283185307179586,
            "TRUE": 1,
            "FALSE": 0,
            "NULL_KEY": "00000000-0000-0000-0000-000000000000",
            "ZERO_VECTOR": [0.0, 0.0, 0.0],
            "ZERO_ROTATION": [0.0, 0.0, 0.0, 1.0],
            "AGENT": 1,
            "OBJECT_POS": 1,
            "ALL_SIDES": -1,
            "PUBLIC_CHANNEL": 0,
            "DEBUG_CHANNEL": 2147483647,
            "HTTP_METHOD": "method",
            "HTTP_MIMETYPE": "mimetype",
            "JSON_OBJECT": "object",
            "JSON_ARRAY": "array"
        }
        
        for name, value in constants.items():
            self.global_scope.set(name, value)
        
        # Global variables from script
        for global_decl in self.ast.globals:
            value = self.evaluator.evaluate(global_decl.init_value) if global_decl.init_value else self._get_default_value(global_decl.type_name)
            self.global_scope.set(global_decl.name, value)
    
    def _get_default_value(self, type_name: str) -> Any:
        """Get default value for LSL type"""
        defaults = {
            'integer': 0,
            'float': 0.0,
            'string': "",
            'key': "00000000-0000-0000-0000-000000000000",
            'vector': [0.0, 0.0, 0.0],
            'rotation': [0.0, 0.0, 0.0, 1.0],
            'list': []
        }
        return defaults.get(type_name, 0)
    
    def _register_built_in_functions(self):
        """Register built-in LSL functions"""
        self.api_functions.update({
            'llSay': self._llSay,
            'llOwnerSay': self._llOwnerSay,
            'llShout': self._llShout,
            'llWhisper': self._llWhisper,
            'llSetText': self._llSetText,
            'llGetTime': self._llGetTime,
            'llResetTime': self._llResetTime,
            'llSleep': self._llSleep,
            'llGetObjectName': self._llGetObjectName,
            'llSetObjectName': self._llSetObjectName,
            'llGetKey': self._llGetKey,
            'llGetOwner': self._llGetOwner,
            'llGetObjectDesc': self._llGetObjectDesc,
            'llSetObjectDesc': self._llSetObjectDesc,
            'llList2String': self._llList2String,
            'llList2Integer': self._llList2Integer,
            'llList2Float': self._llList2Float,
            'llGetListLength': self._llGetListLength,
            'llListInsertList': self._llListInsertList,
            'llListReplaceList': self._llListReplaceList,
            'llDeleteSubList': self._llDeleteSubList,
            'llDumpList2String': self._llDumpList2String,
            'llParseString2List': self._llParseString2List,
            'llStringLength': self._llStringLength,
            'llSubStringIndex': self._llSubStringIndex,
            'llGetSubString': self._llGetSubString,
            'llStringReplace': self._llStringReplace,
            'llToLower': self._llToLower,
            'llToUpper': self._llToUpper,
            'llStringTrim': self._llStringTrim,
            'llList2Json': self._llList2Json,
            'llJson2List': self._llJson2List,
            'llJsonGetValue': self._llJsonGetValue,
            'llJsonSetValue': self._llJsonSetValue,
            'llHTTPRequest': self._llHTTPRequest,
            'llSetTimerEvent': self._llSetTimerEvent,
            'llListen': self._llListen,
            'llListenRemove': self._llListenRemove,
            'llSensor': self._llSensor,
            'llSensorRemove': self._llSensorRemove,
            'llSetStatus': self._llSetStatus,
            'llGetStatus': self._llGetStatus,
            'llSetScale': self._llSetScale,
            'llGetScale': self._llGetScale,
            'llSetPos': self._llSetPos,
            'llGetPos': self._llGetPos,
            'llSetRot': self._llSetRot,
            'llGetRot': self._llGetRot,
            'llInstantMessage': self._llInstantMessage,
            'llTeleportAgentHome': self._llTeleportAgentHome,
            'llGiveInventory': self._llGiveInventory,
            'llGiveMoney': self._llGiveMoney,
            'llRezObject': self._llRezObject,
            'llSetVehicleType': self._llSetVehicleType,
            'llSetVehicleFloatParam': self._llSetVehicleFloatParam,
            'llSetVehicleVectorParam': self._llSetVehicleVectorParam,
            'llSetVehicleRotationParam': self._llSetVehicleRotationParam,
            'llRemoveVehicleFlags': self._llRemoveVehicleFlags,
            'llSetVehicleFlags': self._llSetVehicleFlags,
            'llGenerateKey': self._llGenerateKey,
            'llFrand': self._llFrand,
            'llRound': self._llRound,
            'llFloor': self._llFloor,
            'llCeil': self._llCeil,
            'llAbs': self._llAbs,
            'llPow': self._llPow,
            'llSqrt': self._llSqrt,
            'llSin': self._llSin,
            'llCos': self._llCos,
            'llTan': self._llTan,
            'llAsin': self._llAsin,
            'llAcos': self._llAcos,
            'llAtan2': self._llAtan2,
            'llLog': self._llLog,
            'llLog10': self._llLog10
        })
    
    def call_function(self, name: str, args: List[Any]) -> Any:
        """Call a function (built-in or user-defined)"""
        if name in self.api_functions:
            return self.api_functions[name](args)
        else:
            # User-defined function
            for func_def in self.ast.functions:
                if func_def.name == name:
                    return self._call_user_function(func_def, args)
            return None
    
    def _call_user_function(self, func_def, args: List[Any]) -> Any:
        """Execute user-defined function"""
        # Create new frame
        frame = Frame(self.global_scope)
        
        # Bind parameters
        for i, param in enumerate(func_def.parameters):
            value = args[i] if i < len(args) else self._get_default_value(param.type_name)
            frame.set(param.name, value)
        
        # Execute function body
        self.call_stack.push(frame)
        try:
            result = self._execute_statements(func_def.body)
            return result
        finally:
            self.call_stack.pop()
    
    def _execute_statements(self, statements: List[LSLStatement]) -> Any:
        """Execute a list of statements"""
        for stmt in statements:
            result = self._execute_statement(stmt)
            if result is not None:  # Return value
                return result
        return None
    
    def _execute_statement(self, stmt: LSLStatement) -> Any:
        """Execute a single statement"""
        # This would be implemented with proper visitor pattern
        # For now, simplified implementation
        return None
    
    def trigger_event(self, event_name: str, *args):
        """Trigger an event in the current state"""
        if self.current_state in [state.name for state in self.ast.states]:
            state = next(s for s in self.ast.states if s.name == self.current_state)
            for event in state.events:
                if event.event_name == event_name:
                    self._execute_event(event, args)
                    break
    
    def _execute_event(self, event_handler, args):
        """Execute an event handler"""
        # Create new frame for event
        frame = Frame(self.global_scope)
        
        # Bind event parameters
        for i, param in enumerate(event_handler.parameters):
            value = args[i] if i < len(args) else self._get_default_value(param.type_name)
            frame.set(param.name, value)
        
        # Execute event body
        self.call_stack.push(frame)
        try:
            self._execute_statements(event_handler.body)
        finally:
            self.call_stack.pop()
    
    def is_running(self) -> bool:
        """Check if engine is running"""
        return self._is_running
    
    def stop(self):
        """Stop the engine"""
        self._is_running = False
    
    # Built-in LSL function implementations (simplified)
    
    def _llSay(self, args: List[Any]) -> None:
        channel = int(args[0]) if args else 0
        message = str(args[1]) if len(args) > 1 else ""
        print(f"[{channel}] {message}")
    
    def _llOwnerSay(self, args: List[Any]) -> None:
        message = str(args[0]) if args else ""
        print(f"[OWNER] {message}")
    
    def _llShout(self, args: List[Any]) -> None:
        channel = int(args[0]) if args else 0
        message = str(args[1]) if len(args) > 1 else ""
        print(f"[SHOUT {channel}] {message}")
    
    def _llWhisper(self, args: List[Any]) -> None:
        channel = int(args[0]) if args else 0
        message = str(args[1]) if len(args) > 1 else ""
        print(f"[WHISPER {channel}] {message}")
    
    def _llSetText(self, args: List[Any]) -> None:
        text = str(args[0]) if args else ""
        color = args[1] if len(args) > 1 else [1.0, 1.0, 1.0]
        alpha = float(args[2]) if len(args) > 2 else 1.0
        print(f"[TEXT] {text} (color={color}, alpha={alpha})")
    
    def _llGetTime(self, args: List[Any]) -> float:
        return time.time()
    
    def _llResetTime(self, args: List[Any]) -> None:
        pass  # Reset internal timer
    
    def _llSleep(self, args: List[Any]) -> None:
        seconds = float(args[0]) if args else 0.0
        time.sleep(seconds)
    
    def _llGetObjectName(self, args: List[Any]) -> str:
        return "Object"
    
    def _llSetObjectName(self, args: List[Any]) -> None:
        pass
    
    def _llGetKey(self, args: List[Any]) -> str:
        return "00000000-0000-0000-0000-000000000000"
    
    def _llGetOwner(self, args: List[Any]) -> str:
        return "00000000-0000-0000-0000-000000000000"
    
    def _llGetObjectDesc(self, args: List[Any]) -> str:
        return ""
    
    def _llSetObjectDesc(self, args: List[Any]) -> None:
        pass
    
    def _llList2String(self, args: List[Any]) -> str:
        lst = args[0] if args and isinstance(args[0], list) else []
        index = int(args[1]) if len(args) > 1 else 0
        return str(lst[index]) if 0 <= index < len(lst) else ""
    
    def _llList2Integer(self, args: List[Any]) -> int:
        lst = args[0] if args and isinstance(args[0], list) else []
        index = int(args[1]) if len(args) > 1 else 0
        if 0 <= index < len(lst):
            try:
                return int(lst[index])
            except (ValueError, TypeError):
                return 0
        return 0
    
    def _llList2Float(self, args: List[Any]) -> float:
        lst = args[0] if args and isinstance(args[0], list) else []
        index = int(args[1]) if len(args) > 1 else 0
        if 0 <= index < len(lst):
            try:
                return float(lst[index])
            except (ValueError, TypeError):
                return 0.0
        return 0.0
    
    def _llGetListLength(self, args: List[Any]) -> int:
        lst = args[0] if args and isinstance(args[0], list) else []
        return len(lst)
    
    def _llListInsertList(self, args: List[Any]) -> list:
        dest = args[0] if args and isinstance(args[0], list) else []
        src = args[1] if len(args) > 1 and isinstance(args[1], list) else []
        index = int(args[2]) if len(args) > 2 else 0
        return dest[:index] + src + dest[index:]
    
    def _llListReplaceList(self, args: List[Any]) -> list:
        dest = args[0] if args and isinstance(args[0], list) else []
        src = args[1] if len(args) > 1 and isinstance(args[1], list) else []
        start = int(args[2]) if len(args) > 2 else 0
        end = int(args[3]) if len(args) > 3 else 0
        return dest[:start] + src + dest[end+1:]
    
    def _llDeleteSubList(self, args: List[Any]) -> list:
        lst = args[0] if args and isinstance(args[0], list) else []
        start = int(args[1]) if len(args) > 1 else 0
        end = int(args[2]) if len(args) > 2 else 0
        return lst[:start] + lst[end+1:]
    
    def _llDumpList2String(self, args: List[Any]) -> str:
        lst = args[0] if args and isinstance(args[0], list) else []
        separator = str(args[1]) if len(args) > 1 else ","
        return separator.join(str(item) for item in lst)
    
    def _llParseString2List(self, args: List[Any]) -> list:
        string = str(args[0]) if args else ""
        separators = args[1] if len(args) > 1 and isinstance(args[1], list) else [" "]
        spacers = args[2] if len(args) > 2 and isinstance(args[2], list) else []
        
        # Simplified implementation
        result = [string]
        for sep in separators:
            new_result = []
            for item in result:
                if isinstance(item, str):
                    new_result.extend(item.split(str(sep)))
                else:
                    new_result.append(item)
            result = new_result
        
        return result
    
    def _llStringLength(self, args: List[Any]) -> int:
        string = str(args[0]) if args else ""
        return len(string)
    
    def _llSubStringIndex(self, args: List[Any]) -> int:
        string = str(args[0]) if args else ""
        pattern = str(args[1]) if len(args) > 1 else ""
        return string.find(pattern)
    
    def _llGetSubString(self, args: List[Any]) -> str:
        string = str(args[0]) if args else ""
        start = int(args[1]) if len(args) > 1 else 0
        end = int(args[2]) if len(args) > 2 else -1
        if end == -1:
            return string[start:]
        return string[start:end+1]
    
    def _llStringReplace(self, args: List[Any]) -> str:
        string = str(args[0]) if args else ""
        pattern = str(args[1]) if len(args) > 1 else ""
        replacement = str(args[2]) if len(args) > 2 else ""
        return string.replace(pattern, replacement)
    
    def _llToLower(self, args: List[Any]) -> str:
        string = str(args[0]) if args else ""
        return string.lower()
    
    def _llToUpper(self, args: List[Any]) -> str:
        string = str(args[0]) if args else ""
        return string.upper()
    
    def _llStringTrim(self, args: List[Any]) -> str:
        string = str(args[0]) if args else ""
        trim_type = int(args[1]) if len(args) > 1 else 0
        # Simplified: just strip whitespace
        return string.strip()
    
    def _llList2Json(self, args: List[Any]) -> str:
        json_type = str(args[0]) if args else "array"
        lst = args[1] if len(args) > 1 and isinstance(args[1], list) else []
        
        if json_type == "object":
            # Convert list to JSON object
            result = "{"
            for i in range(0, len(lst), 2):
                if i > 0:
                    result += ","
                key = str(lst[i]) if i < len(lst) else ""
                value = str(lst[i+1]) if i+1 < len(lst) else ""
                result += f'"{key}":"{value}"'
            result += "}"
            return result
        else:
            # Convert list to JSON array
            result = "["
            for i, item in enumerate(lst):
                if i > 0:
                    result += ","
                result += f'"{item}"'
            result += "]"
            return result
    
    def _llJson2List(self, args: List[Any]) -> list:
        json_str = str(args[0]) if args else ""
        # Simplified JSON parsing
        if json_str.startswith('[') and json_str.endswith(']'):
            # Array
            content = json_str[1:-1]
            if not content:
                return []
            # Simple split by comma (not robust)
            items = content.split(',')
            return [item.strip().strip('"') for item in items]
        elif json_str.startswith('{') and json_str.endswith('}'):
            # Object
            content = json_str[1:-1]
            if not content:
                return []
            # Simple key-value parsing
            result = []
            pairs = content.split(',')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    result.append(key.strip().strip('"'))
                    result.append(value.strip().strip('"'))
            return result
        return []
    
    def _llJsonGetValue(self, args: List[Any]) -> str:
        json_str = str(args[0]) if args else ""
        specifiers = args[1] if len(args) > 1 and isinstance(args[1], list) else []
        # Simplified implementation
        return ""
    
    def _llJsonSetValue(self, args: List[Any]) -> str:
        json_str = str(args[0]) if args else ""
        specifiers = args[1] if len(args) > 1 and isinstance(args[1], list) else []
        value = str(args[2]) if len(args) > 2 else ""
        # Simplified implementation
        return json_str
    
    def _llHTTPRequest(self, args: List[Any]) -> str:
        url = str(args[0]) if args else ""
        options = args[1] if len(args) > 1 and isinstance(args[1], list) else []
        body = str(args[2]) if len(args) > 2 else ""
        # Return a dummy key for http_response event
        return "00000000-0000-0000-0000-000000000000"
    
    def _llSetTimerEvent(self, args: List[Any]) -> None:
        sec = float(args[0]) if args else 0.0
        # Would set up timer event
        pass
    
    def _llListen(self, args: List[Any]) -> int:
        channel = int(args[0]) if args else 0
        name = str(args[1]) if len(args) > 1 else ""
        id = str(args[2]) if len(args) > 2 else ""
        msg = str(args[3]) if len(args) > 3 else ""
        return 1  # Return dummy handle
    
    def _llListenRemove(self, args: List[Any]) -> None:
        handle = int(args[0]) if args else 0
        pass
    
    def _llSensor(self, args: List[Any]) -> None:
        name = str(args[0]) if args else ""
        id = str(args[1]) if len(args) > 1 else ""
        type = int(args[2]) if len(args) > 2 else 0
        range = float(args[3]) if len(args) > 3 else 0.0
        arc = float(args[4]) if len(args) > 4 else 0.0
        pass
    
    def _llSensorRemove(self, args: List[Any]) -> None:
        pass
    
    def _llSetStatus(self, args: List[Any]) -> None:
        status = int(args[0]) if args else 0
        value = bool(args[1]) if len(args) > 1 else False
        pass
    
    def _llGetStatus(self, args: List[Any]) -> int:
        status = int(args[0]) if args else 0
        return 0
    
    def _llSetScale(self, args: List[Any]) -> None:
        scale = args[0] if args and isinstance(args[0], list) else [1.0, 1.0, 1.0]
        pass
    
    def _llGetScale(self, args: List[Any]) -> list:
        return [1.0, 1.0, 1.0]
    
    def _llSetPos(self, args: List[Any]) -> None:
        pos = args[0] if args and isinstance(args[0], list) else [0.0, 0.0, 0.0]
        pass
    
    def _llGetPos(self, args: List[Any]) -> list:
        return [0.0, 0.0, 0.0]
    
    def _llSetRot(self, args: List[Any]) -> None:
        rot = args[0] if args and isinstance(args[0], list) else [0.0, 0.0, 0.0, 1.0]
        pass
    
    def _llGetRot(self, args: List[Any]) -> list:
        return [0.0, 0.0, 0.0, 1.0]
    
    def _llInstantMessage(self, args: List[Any]) -> None:
        user = str(args[0]) if args else ""
        message = str(args[1]) if len(args) > 1 else ""
        print(f"[IM to {user}] {message}")
    
    def _llTeleportAgentHome(self, args: List[Any]) -> None:
        agent = str(args[0]) if args else ""
        print(f"[TELEPORT HOME] {agent}")
    
    def _llGiveInventory(self, args: List[Any]) -> None:
        destination = str(args[0]) if args else ""
        inventory = str(args[1]) if len(args) > 1 else ""
        print(f"[GIVE INVENTORY] {inventory} to {destination}")
    
    def _llGiveMoney(self, args: List[Any]) -> None:
        destination = str(args[0]) if args else ""
        amount = int(args[1]) if len(args) > 1 else 0
        print(f"[GIVE MONEY] ${amount} to {destination}")
    
    def _llRezObject(self, args: List[Any]) -> None:
        inventory = str(args[0]) if args else ""
        pos = args[1] if len(args) > 1 and isinstance(args[1], list) else [0.0, 0.0, 0.0]
        vel = args[2] if len(args) > 2 and isinstance(args[2], list) else [0.0, 0.0, 0.0]
        rot = args[3] if len(args) > 3 and isinstance(args[3], list) else [0.0, 0.0, 0.0, 1.0]
        param = int(args[4]) if len(args) > 4 else 0
        print(f"[REZ OBJECT] {inventory} at {pos}")
    
    def _llSetVehicleType(self, args: List[Any]) -> None:
        type = int(args[0]) if args else 0
        pass
    
    def _llSetVehicleFloatParam(self, args: List[Any]) -> None:
        param = int(args[0]) if args else 0
        value = float(args[1]) if len(args) > 1 else 0.0
        pass
    
    def _llSetVehicleVectorParam(self, args: List[Any]) -> None:
        param = int(args[0]) if args else 0
        vec = args[1] if len(args) > 1 and isinstance(args[1], list) else [0.0, 0.0, 0.0]
        pass
    
    def _llSetVehicleRotationParam(self, args: List[Any]) -> None:
        param = int(args[0]) if args else 0
        rot = args[1] if len(args) > 1 and isinstance(args[1], list) else [0.0, 0.0, 0.0, 1.0]
        pass
    
    def _llRemoveVehicleFlags(self, args: List[Any]) -> None:
        flags = int(args[0]) if args else 0
        pass
    
    def _llSetVehicleFlags(self, args: List[Any]) -> None:
        flags = int(args[0]) if args else 0
        pass
    
    def _llGenerateKey(self, args: List[Any]) -> str:
        import uuid
        return str(uuid.uuid4())
    
    def _llFrand(self, args: List[Any]) -> float:
        import random
        mag = float(args[0]) if args else 1.0
        return random.random() * mag
    
    def _llRound(self, args: List[Any]) -> int:
        val = float(args[0]) if args else 0.0
        return round(val)
    
    def _llFloor(self, args: List[Any]) -> int:
        import math
        val = float(args[0]) if args else 0.0
        return math.floor(val)
    
    def _llCeil(self, args: List[Any]) -> int:
        import math
        val = float(args[0]) if args else 0.0
        return math.ceil(val)
    
    def _llAbs(self, args: List[Any]) -> float:
        val = float(args[0]) if args else 0.0
        return abs(val)
    
    def _llPow(self, args: List[Any]) -> float:
        base = float(args[0]) if args else 0.0
        exp = float(args[1]) if len(args) > 1 else 0.0
        return base ** exp
    
    def _llSqrt(self, args: List[Any]) -> float:
        import math
        val = float(args[0]) if args else 0.0
        return math.sqrt(val)
    
    def _llSin(self, args: List[Any]) -> float:
        import math
        val = float(args[0]) if args else 0.0
        return math.sin(val)
    
    def _llCos(self, args: List[Any]) -> float:
        import math
        val = float(args[0]) if args else 0.0
        return math.cos(val)
    
    def _llTan(self, args: List[Any]) -> float:
        import math
        val = float(args[0]) if args else 0.0
        return math.tan(val)
    
    def _llAsin(self, args: List[Any]) -> float:
        import math
        val = float(args[0]) if args else 0.0
        return math.asin(val)
    
    def _llAcos(self, args: List[Any]) -> float:
        import math
        val = float(args[0]) if args else 0.0
        return math.acos(val)
    
    def _llAtan2(self, args: List[Any]) -> float:
        import math
        y = float(args[0]) if args else 0.0
        x = float(args[1]) if len(args) > 1 else 0.0
        return math.atan2(y, x)
    
    def _llLog(self, args: List[Any]) -> float:
        import math
        val = float(args[0]) if args else 1.0
        return math.log(val)
    
    def _llLog10(self, args: List[Any]) -> float:
        import math
        val = float(args[0]) if args else 1.0
        return math.log10(val)