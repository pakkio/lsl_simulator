#!/usr/bin/env python3
"""
Modern LSL Simulator
Refactored with separated concerns and simplified architecture
"""

import threading
import time
from typing import Any, Dict, List, Optional, Set
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lsl_debug_layer import LSLDebugLayer
from .lsl_core_engine import LSLCoreEngine

class LSLSimulator:
    """Modern LSL Simulator with separated concerns"""
    
    def __init__(self, script_source: str, debug_mode: bool = False, breakpoints: Optional[Set[int]] = None):
        # Choose engine based on debug mode
        if debug_mode:
            self.engine = LSLDebugLayer(script_source, debug_mode, breakpoints)
        else:
            self.engine = LSLCoreEngine(script_source)
        
        # Compatibility properties for existing code
        self.debug_mode = debug_mode
        self.source_lines = script_source.split('\n')
        self.breakpoints = breakpoints or set()
        
        # Event handling
        self.active_listeners = []
        self.listener_handle_counter = 1
        self.avatar_counter = 0
        
        # Threading for timers and events
        self.timer_thread = None
        self.timer_interval = 0.0
        self.timer_active = False
        
        # Initialize and start
        self._setup_simulator()
    
    def _setup_simulator(self):
        """Initialize the simulator"""
        # Trigger state_entry event
        self.trigger_event('state_entry')
    
    # Core execution methods
    
    def trigger_event(self, event_name: str, *args):
        """Trigger an event"""
        self.engine.trigger_event(event_name, *args)
    
    def call_function(self, name: str, args: List[Any]) -> Any:
        """Call a function"""
        return self.engine.call_function(name, args)
    
    def is_running(self) -> bool:
        """Check if simulator is running"""
        return self.engine.is_running()
    
    def stop(self):
        """Stop the simulator"""
        self.engine.stop()
        self._stop_timer()
    
    # Timer management
    
    def _start_timer(self, interval: float):
        """Start the timer"""
        self._stop_timer()
        if interval > 0:
            self.timer_interval = interval
            self.timer_active = True
            self.timer_thread = threading.Thread(target=self._timer_loop)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def _stop_timer(self):
        """Stop the timer"""
        self.timer_active = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1.0)
            self.timer_thread = None
    
    def _timer_loop(self):
        """Timer loop"""
        while self.timer_active and self.is_running():
            time.sleep(self.timer_interval)
            if self.timer_active and self.is_running():
                self.trigger_event('timer')
    
    # Debug interface (if debug layer is used)
    
    def set_breakpoint(self, line_number: int):
        """Set a breakpoint"""
        if hasattr(self.engine, 'set_breakpoint'):
            self.engine.set_breakpoint(line_number)
    
    def remove_breakpoint(self, line_number: int):
        """Remove a breakpoint"""
        if hasattr(self.engine, 'remove_breakpoint'):
            self.engine.remove_breakpoint(line_number)
    
    def step_into(self):
        """Step into next statement"""
        if hasattr(self.engine, 'step_into'):
            self.engine.step_into()
    
    def step_over(self):
        """Step over next statement"""
        if hasattr(self.engine, 'step_over'):
            self.engine.step_over()
    
    def continue_execution(self):
        """Continue execution"""
        if hasattr(self.engine, 'continue_execution'):
            self.engine.continue_execution()
    
    def pause_execution(self):
        """Pause execution"""
        if hasattr(self.engine, 'pause_execution'):
            self.engine.pause_execution()
    
    def get_call_stack(self) -> List[Dict[str, Any]]:
        """Get call stack"""
        if hasattr(self.engine, 'get_call_stack'):
            return self.engine.get_call_stack()
        return []
    
    def get_variables(self) -> Dict[str, Any]:
        """Get variables"""
        if hasattr(self.engine, 'get_variables'):
            return self.engine.get_variables()
        return {}
    
    def evaluate_expression(self, expression: str) -> Any:
        """Evaluate expression"""
        if hasattr(self.engine, 'evaluate_expression'):
            return self.engine.evaluate_expression(expression)
        return None
    
    def get_execution_info(self) -> Dict[str, Any]:
        """Get execution info"""
        if hasattr(self.engine, 'get_execution_info'):
            return self.engine.get_execution_info()
        return {}
    
    # Compatibility methods for existing code
    
    @property
    def global_scope(self):
        """Get global scope for compatibility"""
        if hasattr(self.engine, 'global_scope'):
            return self.engine.global_scope
        elif hasattr(self.engine, 'get_global_scope'):
            return self.engine.get_global_scope()
        return None
    
    @property
    def call_stack(self):
        """Get call stack for compatibility"""
        if hasattr(self.engine, 'call_stack'):
            return self.engine.call_stack
        elif hasattr(self.engine, 'get_call_stack_obj'):
            return self.engine.get_call_stack_obj()
        return None
    
    @property
    def current_state(self):
        """Get current state for compatibility"""
        if hasattr(self.engine, 'current_state'):
            return self.engine.current_state
        elif hasattr(self.engine, 'get_current_state'):
            return self.engine.get_current_state()
        return "default"
    
    @current_state.setter
    def current_state(self, state: str):
        """Set current state for compatibility"""
        if hasattr(self.engine, 'current_state'):
            self.engine.current_state = state
        elif hasattr(self.engine, 'set_current_state'):
            self.engine.set_current_state(state)
    
    def _evaluate_expression(self, expr):
        """Evaluate expression for compatibility"""
        if expr is None:
            return None
        
        if hasattr(self.engine, 'evaluator'):
            return self.engine.evaluator.evaluate(expr)
        
        # Fallback for simple values
        return expr
    
    # Enhanced LSL API functions that need timer support
    
    def _llSetTimerEvent(self, args: List[Any]) -> None:
        """Set timer event"""
        sec = float(args[0]) if args else 0.0
        if sec > 0:
            self._start_timer(sec)
        else:
            self._stop_timer()
    
    def _llHTTPRequest(self, args: List[Any]) -> str:
        """HTTP request with callback"""
        url = str(args[0]) if args else ""
        options = args[1] if len(args) > 1 and isinstance(args[1], list) else []
        body = str(args[2]) if len(args) > 2 else ""
        
        # Generate request key
        import uuid
        request_key = str(uuid.uuid4())
        
        # Schedule HTTP response event (simplified)
        def http_callback():
            time.sleep(0.1)  # Simulate network delay
            self.trigger_event('http_response', request_key, 200, [], body)
        
        thread = threading.Thread(target=http_callback)
        thread.daemon = True
        thread.start()
        
        return request_key
    
    def _llListen(self, args: List[Any]) -> int:
        """Listen for chat messages"""
        channel = int(args[0]) if args else 0
        name = str(args[1]) if len(args) > 1 else ""
        id = str(args[2]) if len(args) > 2 else ""
        msg = str(args[3]) if len(args) > 3 else ""
        
        handle = self.listener_handle_counter
        self.listener_handle_counter += 1
        
        listener = {
            'handle': handle,
            'channel': channel,
            'name': name,
            'id': id,
            'msg': msg
        }
        self.active_listeners.append(listener)
        
        return handle
    
    def _llListenRemove(self, args: List[Any]) -> None:
        """Remove listener"""
        handle = int(args[0]) if args else 0
        self.active_listeners = [l for l in self.active_listeners if l['handle'] != handle]
    
    def simulate_chat(self, channel: int, name: str, id: str, message: str):
        """Simulate incoming chat message"""
        for listener in self.active_listeners:
            if (listener['channel'] == channel and
                (not listener['name'] or listener['name'] == name) and
                (not listener['id'] or listener['id'] == id) and
                (not listener['msg'] or listener['msg'] in message)):
                
                self.trigger_event('listen', channel, name, id, message)
                break
    
    def simulate_touch(self, avatar_key: str = None):
        """Simulate touch event"""
        if avatar_key is None:
            avatar_key = f"avatar-{self.avatar_counter:08d}"
            self.avatar_counter += 1
        
        self.trigger_event('touch_start', 1)  # num_detected
        self.trigger_event('touch_end', 1)
    
    def simulate_collision(self, avatar_key: str = None):
        """Simulate collision event"""
        if avatar_key is None:
            avatar_key = f"avatar-{self.avatar_counter:08d}"
            self.avatar_counter += 1
        
        self.trigger_event('collision_start', 1)  # num_detected
    
    def simulate_sensor(self, name: str, id: str, type: int = 1):
        """Simulate sensor detection"""
        self.trigger_event('sensor', 1)  # num_detected
    
    def simulate_no_sensor(self):
        """Simulate no sensor detection"""
        self.trigger_event('no_sensor')


# Compatibility function for existing code
def parse_script(script_source: str) -> Dict[str, Any]:
    """Parse script and return structure compatible with old simulator"""
    from lsl_antlr_parser import LSLParser
    
    parser = LSLParser()
    ast = parser.parse(script_source)
    
    # Convert AST to old format
    parsed_script = {
        'globals': [],
        'functions': {},
        'states': {}
    }
    
    # Convert globals
    for global_decl in ast.globals:
        parsed_script['globals'].append({
            'name': global_decl.name,
            'type': global_decl.type_name,
            'value': global_decl.init_value
        })
    
    # Convert functions
    for func_def in ast.functions:
        parsed_script['functions'][func_def.name] = func_def
    
    # Convert states
    for state in ast.states:
        parsed_script['states'][state.name] = state
    
    return parsed_script


def run_script(script_source: str, debug_mode: bool = False, breakpoints: Optional[Set[int]] = None) -> LSLSimulator:
    """Run an LSL script with the new simulator"""
    return LSLSimulator(script_source, debug_mode, breakpoints)