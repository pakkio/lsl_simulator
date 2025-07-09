#!/usr/bin/env python3
"""
State Management Stress Test
Tests the robustness of state management, event queuing, and concurrent operations
This is the "cuore pulsante" test - the heart of the simulator
"""

import threading
import time
import random
import uuid
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from lsl_ossl_compatibility import LSLOSSLCompatibility, SimulatorMode

@dataclass
class Event:
    """Represents an LSL event"""
    event_type: str
    parameters: Dict[str, Any]
    timestamp: float
    priority: int = 1  # 1=normal, 2=high, 3=critical
    source_object: Optional[str] = None

@dataclass
class StateTransition:
    """Represents a state change"""
    from_state: str
    to_state: str
    timestamp: float
    trigger: str

class EventQueue:
    """Thread-safe event queue with priority support"""
    
    def __init__(self, max_size: int = 1000):
        self.queues = {
            1: Queue(max_size),  # Normal priority
            2: Queue(max_size),  # High priority  
            3: Queue(max_size)   # Critical priority
        }
        self.total_events = 0
        self.processed_events = 0
        self.dropped_events = 0
        self._lock = threading.Lock()
    
    def enqueue(self, event: Event) -> bool:
        """Add event to queue, returns True if successful"""
        with self._lock:
            queue = self.queues.get(event.priority, self.queues[1])
            try:
                queue.put_nowait(event)
                self.total_events += 1
                return True
            except:
                self.dropped_events += 1
                return False
    
    def dequeue(self, timeout: float = 0.1) -> Optional[Event]:
        """Get next event (highest priority first)"""
        # Check critical first, then high, then normal
        for priority in [3, 2, 1]:
            queue = self.queues[priority]
            try:
                event = queue.get_nowait()
                with self._lock:
                    self.processed_events += 1
                return event
            except Empty:
                continue
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics"""
        with self._lock:
            return {
                'total_events': self.total_events,
                'processed_events': self.processed_events,
                'dropped_events': self.dropped_events,
                'pending_events': sum(q.qsize() for q in self.queues.values()),
                'queue_sizes': {p: q.qsize() for p, q in self.queues.items()}
            }

class LSLStateMachine:
    """Advanced state machine for LSL scripts"""
    
    def __init__(self, script_name: str):
        self.script_name = script_name
        self.current_state = "default"
        self.states = {"default": {}}
        self.global_vars = {}
        self.local_scopes = []  # Stack of local scopes
        self.event_handlers = {}
        self.timers = {}
        self.listeners = {}
        self.state_history = []
        self._lock = threading.RLock()  # Reentrant lock for nested calls
        
    def add_state(self, state_name: str, handlers: Dict[str, Any]):
        """Add a new state with event handlers"""
        with self._lock:
            self.states[state_name] = handlers
            self.event_handlers[state_name] = handlers
    
    def change_state(self, new_state: str, trigger: str = "manual") -> bool:
        """Change to a new state"""
        with self._lock:
            if new_state not in self.states:
                return False
            
            old_state = self.current_state
            transition = StateTransition(old_state, new_state, time.time(), trigger)
            self.state_history.append(transition)
            
            # Call state_exit for old state
            if old_state in self.event_handlers:
                exit_handler = self.event_handlers[old_state].get('state_exit')
                if exit_handler:
                    try:
                        exit_handler()
                    except Exception as e:
                        print(f"Error in state_exit for {old_state}: {e}")
            
            # Change state
            self.current_state = new_state
            
            # Call state_entry for new state
            if new_state in self.event_handlers:
                entry_handler = self.event_handlers[new_state].get('state_entry')
                if entry_handler:
                    try:
                        entry_handler()
                    except Exception as e:
                        print(f"Error in state_entry for {new_state}: {e}")
            
            return True
    
    def push_scope(self, scope_vars: Dict[str, Any]):
        """Push a new local scope (for function calls)"""
        with self._lock:
            self.local_scopes.append(scope_vars.copy())
    
    def pop_scope(self) -> Optional[Dict[str, Any]]:
        """Pop the current local scope"""
        with self._lock:
            if self.local_scopes:
                return self.local_scopes.pop()
            return None
    
    def get_variable(self, name: str) -> Any:
        """Get variable value (local scope first, then global)"""
        with self._lock:
            # Check local scopes (most recent first)
            for scope in reversed(self.local_scopes):
                if name in scope:
                    return scope[name]
            
            # Check global variables
            return self.global_vars.get(name)
    
    def set_variable(self, name: str, value: Any, local: bool = False):
        """Set variable value"""
        with self._lock:
            if local and self.local_scopes:
                self.local_scopes[-1][name] = value
            else:
                self.global_vars[name] = value
    
    def handle_event(self, event: Event) -> bool:
        """Handle an incoming event"""
        with self._lock:
            current_handlers = self.event_handlers.get(self.current_state, {})
            handler = current_handlers.get(event.event_type)
            
            if handler:
                try:
                    # Push event scope
                    event_scope = {'event_data': event.parameters}
                    self.push_scope(event_scope)
                    
                    # Call handler
                    result = handler(event.parameters)
                    
                    # Pop event scope
                    self.pop_scope()
                    
                    return True
                except Exception as e:
                    print(f"Error handling event {event.event_type}: {e}")
                    # Ensure scope is popped even on error
                    if self.local_scopes:
                        self.pop_scope()
                    return False
            
            return False
    
    def get_state_stats(self) -> Dict[str, Any]:
        """Get state machine statistics"""
        with self._lock:
            return {
                'current_state': self.current_state,
                'total_states': len(self.states),
                'global_vars_count': len(self.global_vars),
                'scope_depth': len(self.local_scopes),
                'state_transitions': len(self.state_history),
                'recent_transitions': [
                    f"{t.from_state}->{t.to_state}" 
                    for t in self.state_history[-5:]
                ]
            }

class StressTestRunner:
    """Runs comprehensive stress tests on the state management system"""
    
    def __init__(self):
        self.api = LSLOSSLCompatibility(SimulatorMode.HYBRID)
        self.event_queue = EventQueue()
        self.state_machines = {}
        self.running = False
        self.test_results = {}
        
    def create_test_scripts(self, count: int):
        """Create multiple test script state machines"""
        for i in range(count):
            script_name = f"TestScript_{i}"
            state_machine = LSLStateMachine(script_name)
            
            # Add states with event handlers
            def make_handler(script_id, event_type):
                def handler(params):
                    # Simulate some work
                    time.sleep(random.uniform(0.001, 0.01))
                    # Randomly change state
                    if random.random() < 0.1:  # 10% chance
                        new_state = random.choice(['default', 'active', 'waiting'])
                        state_machine.change_state(new_state, f"event_{event_type}")
                    return f"Script {script_id} handled {event_type}"
                return handler
            
            # Add states
            for state in ['default', 'active', 'waiting']:
                handlers = {}
                for event_type in ['state_entry', 'state_exit', 'timer', 'touch_start', 'http_response']:
                    handlers[event_type] = make_handler(i, event_type)
                state_machine.add_state(state, handlers)
            
            self.state_machines[script_name] = state_machine
    
    def event_generator_thread(self, events_per_second: int, duration: int):
        """Generate events at specified rate"""
        event_types = ['timer', 'touch_start', 'http_response', 'collision_start', 'listen']
        end_time = time.time() + duration
        
        while time.time() < end_time and self.running:
            # Generate event
            event = Event(
                event_type=random.choice(event_types),
                parameters={'data': f"event_{uuid.uuid4().hex[:8]}"},
                timestamp=time.time(),
                priority=random.choices([1, 2, 3], weights=[70, 25, 5])[0],
                source_object=random.choice(list(self.state_machines.keys()))
            )
            
            self.event_queue.enqueue(event)
            
            # Sleep to maintain rate
            time.sleep(1.0 / events_per_second)
    
    def event_processor_thread(self):
        """Process events from the queue"""
        while self.running:
            event = self.event_queue.dequeue(timeout=0.1)
            if event:
                # Find target state machine
                if event.source_object and event.source_object in self.state_machines:
                    state_machine = self.state_machines[event.source_object]
                    state_machine.handle_event(event)
    
    def api_stress_thread(self, calls_per_second: int, duration: int):
        """Stress test API functions"""
        functions_to_test = [
            ('llSay', [0, 'Test message']),
            ('llGetPos', []),
            ('llSetPos', [(random.uniform(0, 256), random.uniform(0, 256), random.uniform(20, 50))]),
            ('llSensor', ['', '', 1, 20.0, 1.57]),
            ('llStringLength', [f'test_string_{random.randint(1, 1000)}']),
            ('llVecMag', [(random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10))]),
            ('llListSort', [[random.randint(1, 100) for _ in range(10)], 1, True])
        ]
        
        end_time = time.time() + duration
        call_count = 0
        error_count = 0
        
        while time.time() < end_time and self.running:
            func_name, args = random.choice(functions_to_test)
            try:
                result = self.api.call_function(func_name, args)
                call_count += 1
            except Exception as e:
                error_count += 1
                print(f"API error in {func_name}: {e}")
            
            time.sleep(1.0 / calls_per_second)
        
        return {'calls': call_count, 'errors': error_count}
    
    def memory_pressure_thread(self, duration: int):
        """Create memory pressure with large data structures"""
        large_lists = []
        end_time = time.time() + duration
        
        while time.time() < end_time and self.running:
            # Create large list
            large_list = [random.random() for _ in range(1000)]
            large_lists.append(large_list)
            
            # Randomly clear some lists to simulate garbage collection
            if len(large_lists) > 50:
                large_lists = large_lists[-25:]
            
            time.sleep(0.1)
    
    def run_stress_test(self, 
                       script_count: int = 10,
                       events_per_second: int = 100,
                       api_calls_per_second: int = 50,
                       duration: int = 30) -> Dict[str, Any]:
        """Run comprehensive stress test"""
        
        print(f"🔥 Starting State Management Stress Test")
        print(f"   Scripts: {script_count}")
        print(f"   Events/sec: {events_per_second}")
        print(f"   API calls/sec: {api_calls_per_second}")
        print(f"   Duration: {duration}s")
        print("=" * 50)
        
        # Setup
        self.create_test_scripts(script_count)
        self.running = True
        
        start_time = time.time()
        
        # Start threads
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            # Event generation
            futures.append(executor.submit(
                self.event_generator_thread, events_per_second, duration
            ))
            
            # Event processing (multiple processors)
            for _ in range(3):
                futures.append(executor.submit(self.event_processor_thread))
            
            # API stress testing
            futures.append(executor.submit(
                self.api_stress_thread, api_calls_per_second, duration
            ))
            
            # Memory pressure
            futures.append(executor.submit(self.memory_pressure_thread, duration))
            
            # Wait for duration
            time.sleep(duration)
            self.running = False
            
            # Collect results
            api_results = None
            for future in as_completed(futures):
                try:
                    result = future.result(timeout=1)
                    if isinstance(result, dict) and 'calls' in result:
                        api_results = result
                except:
                    pass
        
        end_time = time.time()
        actual_duration = end_time - start_time
        
        # Collect statistics
        event_stats = self.event_queue.get_stats()
        
        state_stats = {}
        for name, sm in self.state_machines.items():
            state_stats[name] = sm.get_state_stats()
        
        # Calculate performance metrics
        events_processed_per_second = event_stats['processed_events'] / actual_duration
        event_success_rate = (event_stats['processed_events'] / event_stats['total_events'] * 100) if event_stats['total_events'] > 0 else 0
        
        results = {
            'duration': actual_duration,
            'script_count': script_count,
            'event_stats': event_stats,
            'events_per_second_actual': events_processed_per_second,
            'event_success_rate': event_success_rate,
            'api_results': api_results,
            'state_stats_sample': dict(list(state_stats.items())[:3]),  # Sample of state stats
            'total_state_transitions': sum(
                len(sm.state_history) for sm in self.state_machines.values()
            ),
            'memory_usage_estimate': sum(
                len(sm.global_vars) + len(sm.local_scopes) 
                for sm in self.state_machines.values()
            )
        }
        
        return results
    
    def evaluate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate test results and provide scoring"""
        score = 100
        issues = []
        warnings = []
        
        # Event processing performance
        events_per_sec = results['events_per_second_actual']
        if events_per_sec < 50:
            score -= 20
            issues.append(f"Low event processing rate: {events_per_sec:.1f}/sec")
        elif events_per_sec < 80:
            score -= 10
            warnings.append(f"Moderate event processing rate: {events_per_sec:.1f}/sec")
        
        # Event success rate
        success_rate = results['event_success_rate']
        if success_rate < 95:
            score -= 15
            issues.append(f"Low event success rate: {success_rate:.1f}%")
        elif success_rate < 98:
            score -= 5
            warnings.append(f"Moderate event success rate: {success_rate:.1f}%")
        
        # Dropped events
        dropped = results['event_stats']['dropped_events']
        if dropped > 0:
            score -= 10
            warnings.append(f"Dropped {dropped} events")
        
        # API performance
        if results['api_results']:
            api_calls = results['api_results']['calls']
            api_errors = results['api_results']['errors']
            api_error_rate = (api_errors / api_calls * 100) if api_calls > 0 else 0
            
            if api_error_rate > 5:
                score -= 15
                issues.append(f"High API error rate: {api_error_rate:.1f}%")
            elif api_error_rate > 1:
                score -= 5
                warnings.append(f"Moderate API error rate: {api_error_rate:.1f}%")
        
        # Performance grade
        if score >= 90:
            grade = "A - Excellent"
        elif score >= 80:
            grade = "B - Good"
        elif score >= 70:
            grade = "C - Fair"
        elif score >= 60:
            grade = "D - Poor"
        else:
            grade = "F - Failed"
        
        return {
            'score': score,
            'grade': grade,
            'issues': issues,
            'warnings': warnings,
            'ready_for_production': score >= 80 and len(issues) == 0
        }

def run_comprehensive_stress_test():
    """Run the complete stress test suite"""
    print("💓 LSL State Management Heart Beat Test")
    print("Testing the robustness of the simulator's core...")
    print("=" * 60)
    
    runner = StressTestRunner()
    
    # Test different scenarios
    scenarios = [
        {"name": "Light Load", "scripts": 5, "events": 25, "api_calls": 25, "duration": 10},
        {"name": "Medium Load", "scripts": 10, "events": 50, "api_calls": 50, "duration": 20},
        {"name": "Heavy Load", "scripts": 20, "events": 100, "api_calls": 100, "duration": 30},
    ]
    
    all_results = {}
    
    for scenario in scenarios:
        print(f"\n🎯 Running {scenario['name']} Test...")
        
        runner = StressTestRunner()  # Fresh instance for each test
        results = runner.run_stress_test(
            script_count=scenario['scripts'],
            events_per_second=scenario['events'],
            api_calls_per_second=scenario['api_calls'],
            duration=scenario['duration']
        )
        
        evaluation = runner.evaluate_results(results)
        all_results[scenario['name']] = {**results, **evaluation}
        
        # Print results
        print(f"✅ {scenario['name']} Results:")
        print(f"   Score: {evaluation['score']}/100 ({evaluation['grade']})")
        print(f"   Events processed: {results['event_stats']['processed_events']}")
        print(f"   Processing rate: {results['events_per_second_actual']:.1f} events/sec")
        print(f"   Success rate: {results['event_success_rate']:.1f}%")
        print(f"   State transitions: {results['total_state_transitions']}")
        
        if evaluation['issues']:
            print(f"   Issues: {evaluation['issues']}")
        if evaluation['warnings']:
            print(f"   Warnings: {evaluation['warnings']}")
    
    # Overall assessment
    print(f"\n" + "=" * 60)
    print("💓 HEART BEAT TEST SUMMARY")
    print("=" * 60)
    
    overall_score = sum(r['score'] for r in all_results.values()) / len(all_results)
    all_production_ready = all(r['ready_for_production'] for r in all_results.values())
    
    print(f"Overall Score: {overall_score:.1f}/100")
    print(f"Production Ready: {'✅ YES' if all_production_ready else '❌ NO'}")
    
    if overall_score >= 85:
        print("🏆 EXCELLENT: State management is rock solid!")
    elif overall_score >= 75:
        print("✅ GOOD: State management is reliable with minor issues")
    elif overall_score >= 65:
        print("⚠️  FAIR: State management needs improvement")
    else:
        print("❌ POOR: State management has significant issues")
    
    return all_results

if __name__ == "__main__":
    results = run_comprehensive_stress_test()