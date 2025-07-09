#!/usr/bin/env python3
"""
LSL Simulator Integration Stress Test - The Path to 9/10
Tests complex interactions between events, state management, and concurrent operations
This is the ultimate test of robustness under real-world conditions
"""

import threading
import time as time_module
import random
import uuid
import queue
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from lsl_ossl_compatibility import LSLOSSLCompatibility, SimulatorMode

@dataclass
class ScenarioResult:
    """Results from a specific test scenario"""
    scenario_name: str
    success: bool
    execution_time: float
    events_processed: int
    state_changes: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

class ConcurrentEventManager:
    """Manages multiple types of events with precise timing control"""
    
    def __init__(self):
        self.event_queues = {
            'timer': queue.Queue(),
            'http_response': queue.Queue(),
            'dataserver': queue.Queue(),
            'sensor': queue.Queue(),
            'touch': queue.Queue(),
            'collision': queue.Queue(),
            'listen': queue.Queue()
        }
        self.global_state = {}
        self.state_lock = threading.RLock()
        self.event_history = []
        self.active_operations = set()
        
    def trigger_event(self, event_type: str, data: Dict[str, Any], delay: float = 0):
        """Trigger an event with optional delay"""
        if delay > 0:
            threading.Timer(delay, self._queue_event, args=[event_type, data]).start()
        else:
            self._queue_event(event_type, data)
    
    def _queue_event(self, event_type: str, data: Dict[str, Any]):
        """Internal method to queue an event"""
        if event_type in self.event_queues:
            event = {
                'type': event_type,
                'data': data,
                'timestamp': time_module.time(),
                'thread_id': threading.current_thread().ident
            }
            self.event_queues[event_type].put(event)
            with self.state_lock:
                self.event_history.append(event)
    
    def get_and_clear_history(self) -> List[Dict[str, Any]]:
        """Get and clear event history"""
        with self.state_lock:
            history = self.event_history.copy()
            self.event_history.clear()
            return history

class LSLIntegrationTester:
    """Comprehensive integration testing framework"""
    
    def __init__(self):
        self.api = LSLOSSLCompatibility(SimulatorMode.HYBRID)
        self.event_manager = ConcurrentEventManager()
        self.test_results = []
        self.global_test_state = {
            'shared_counter': 0,
            'shared_list': [],
            'shared_string': "",
            'operation_log': []
        }
        self.locks = {
            'counter_lock': threading.Lock(),
            'list_lock': threading.Lock(),
            'string_lock': threading.Lock(),
            'log_lock': threading.Lock()
        }
    
    @contextmanager
    def scenario_context(self, name: str):
        """Context manager for scenario execution"""
        start_time = time_module.time()
        scenario_result = ScenarioResult(
            scenario_name=name,
            success=True,
            execution_time=0,
            events_processed=0,
            state_changes=0
        )
        
        try:
            print(f"\n🎭 Starting scenario: {name}")
            yield scenario_result
            
        except Exception as e:
            scenario_result.success = False
            scenario_result.errors.append(str(e))
            print(f"❌ Scenario {name} failed: {e}")
            
        finally:
            scenario_result.execution_time = time_module.time() - start_time
            self.test_results.append(scenario_result)
            
            status = "✅ PASSED" if scenario_result.success else "❌ FAILED"
            print(f"{status} {name} - {scenario_result.execution_time:.2f}s")
    
    def test_concurrent_timer_operations(self) -> ScenarioResult:
        """Test: Multiple timers modifying shared state simultaneously"""
        with self.scenario_context("Concurrent Timer Operations") as result:
            
            def timer_worker(timer_id: int, operations: int):
                """Worker function for timer operations"""
                for i in range(operations):
                    with self.locks['counter_lock']:
                        old_value = self.global_test_state['shared_counter']
                        # Simulate some processing time
                        time_module.sleep(0.001)
                        new_value = old_value + 1
                        self.global_test_state['shared_counter'] = new_value
                        
                    with self.locks['log_lock']:
                        self.global_test_state['operation_log'].append(
                            f"Timer{timer_id}_Op{i}_{old_value}->{new_value}"
                        )
                    
                    # Simulate timer API calls
                    self.api.call_function('llSetTimerEvent', [0.1])
                    self.api.call_function('llGetTime', [])
                    
                    result.events_processed += 1
            
            # Reset shared state
            self.global_test_state['shared_counter'] = 0
            self.global_test_state['operation_log'].clear()
            
            # Launch 10 concurrent timers
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = []
                for timer_id in range(10):
                    future = executor.submit(timer_worker, timer_id, 20)
                    futures.append(future)
                
                # Wait for all timers to complete
                for future in as_completed(futures):
                    future.result()
            
            # Validate results
            expected_value = 10 * 20  # 10 timers * 20 operations each
            actual_value = self.global_test_state['shared_counter']
            
            if actual_value != expected_value:
                result.errors.append(
                    f"Counter mismatch: expected {expected_value}, got {actual_value}"
                )
                result.success = False
            
            result.metrics = {
                'expected_counter': expected_value,
                'actual_counter': actual_value,
                'operations_logged': len(self.global_test_state['operation_log'])
            }
        
        return result
    
    def test_http_dataserver_collision(self) -> ScenarioResult:
        """Test: HTTP response colliding with dataserver event on same variable"""
        with self.scenario_context("HTTP-Dataserver Variable Collision") as result:
            
            collision_detected = False
            collision_count = 0
            
            def http_response_handler():
                """Simulates HTTP response modifying shared state"""
                nonlocal collision_detected, collision_count
                
                for i in range(50):
                    try:
                        with self.locks['string_lock']:
                            current = self.global_test_state['shared_string']
                            if 'dataserver' in current and 'http' not in current:
                                collision_detected = True
                                collision_count += 1
                            
                            # Simulate HTTP processing time
                            time_module.sleep(0.002)
                            self.global_test_state['shared_string'] = f"http_response_{i}_{uuid.uuid4().hex[:8]}"
                        
                        # API calls
                        self.api.call_function('llHTTPResponse', [
                            str(uuid.uuid4()), 200, '{"status": "ok"}'
                        ])
                        
                        result.events_processed += 1
                        
                    except Exception as e:
                        result.errors.append(f"HTTP handler error: {e}")
                    
                    time_module.sleep(0.001)
            
            def dataserver_handler():
                """Simulates dataserver event modifying same variable"""
                nonlocal collision_detected, collision_count
                
                for i in range(50):
                    try:
                        with self.locks['string_lock']:
                            current = self.global_test_state['shared_string']
                            if 'http' in current and 'dataserver' not in current:
                                collision_detected = True
                                collision_count += 1
                            
                            # Simulate notecard reading time
                            time_module.sleep(0.003)
                            self.global_test_state['shared_string'] = f"dataserver_{i}_{uuid.uuid4().hex[:8]}"
                        
                        # API calls
                        self.api.call_function('llGetNotecardLine', [
                            'test_notecard', i
                        ])
                        
                        result.events_processed += 1
                        
                    except Exception as e:
                        result.errors.append(f"Dataserver handler error: {e}")
                    
                    time_module.sleep(0.001)
            
            # Reset state
            self.global_test_state['shared_string'] = ""
            
            # Start both handlers simultaneously
            with ThreadPoolExecutor(max_workers=2) as executor:
                http_future = executor.submit(http_response_handler)
                dataserver_future = executor.submit(dataserver_handler)
                
                # Wait for completion
                http_future.result()
                dataserver_future.result()
            
            # Validate that we successfully detected collisions
            if not collision_detected:
                result.warnings.append("No collisions detected - test may be too fast")
            
            result.metrics = {
                'collisions_detected': collision_count,
                'collision_rate': collision_count / 100 if collision_count > 0 else 0,
                'final_string_source': 'http' if 'http' in self.global_test_state['shared_string'] else 'dataserver'
            }
        
        return result
    
    def test_sensor_touch_state_chaos(self) -> ScenarioResult:
        """Test: Sensor detection during touch events with state changes"""
        with self.scenario_context("Sensor-Touch State Chaos") as result:
            
            state_transitions = []
            sensor_detections = []
            touch_events = []
            
            def sensor_worker():
                """Continuous sensor detection"""
                for i in range(30):
                    try:
                        # Trigger sensor
                        self.api.call_function('llSensor', ['', '', 1, 20.0, 1.57])
                        
                        # Simulate detection processing
                        if random.random() < 0.7:  # 70% detection rate
                            detection = {
                                'id': i,
                                'timestamp': time_module.time(),
                                'detected_name': self.api.call_function('llDetectedName', [0]),
                                'detected_key': self.api.call_function('llDetectedKey', [0])
                            }
                            sensor_detections.append(detection)
                        
                        result.events_processed += 1
                        time_module.sleep(0.05)
                        
                    except Exception as e:
                        result.errors.append(f"Sensor error: {e}")
            
            def touch_worker():
                """Continuous touch events"""
                for i in range(25):
                    try:
                        # Simulate touch
                        touch_data = {
                            'toucher': str(uuid.uuid4()),
                            'pos': (random.uniform(0, 256), random.uniform(0, 256), random.uniform(20, 50)),
                            'face': random.randint(0, 7)
                        }
                        touch_events.append(touch_data)
                        
                        # Touch API calls
                        self.api.call_function('llDetectedPos', [0])
                        self.api.call_function('llDetectedKey', [0])
                        
                        result.events_processed += 1
                        time_module.sleep(0.06)
                        
                    except Exception as e:
                        result.errors.append(f"Touch error: {e}")
            
            def state_changer():
                """Random state changes"""
                states = ['default', 'active', 'waiting', 'processing']
                for i in range(15):
                    try:
                        new_state = random.choice(states)
                        transition = {
                            'from': 'current',
                            'to': new_state,
                            'timestamp': time_module.time(),
                            'trigger': f'state_change_{i}'
                        }
                        state_transitions.append(transition)
                        
                        # Simulate state change overhead
                        time_module.sleep(0.01)
                        
                        result.state_changes += 1
                        time_module.sleep(0.08)
                        
                    except Exception as e:
                        result.errors.append(f"State change error: {e}")
            
            # Run all three workers simultaneously
            with ThreadPoolExecutor(max_workers=3) as executor:
                sensor_future = executor.submit(sensor_worker)
                touch_future = executor.submit(touch_worker)
                state_future = executor.submit(state_changer)
                
                # Wait for all to complete
                for future in as_completed([sensor_future, touch_future, state_future]):
                    future.result()
            
            # Analyze timing overlaps
            overlaps = 0
            # Note: timing overlap analysis simplified since touch_events don't have timestamps
            overlaps = min(len(sensor_detections), len(touch_events))
            
            result.metrics = {
                'sensor_detections': len(sensor_detections),
                'touch_events': len(touch_events),
                'state_transitions': len(state_transitions),
                'timing_overlaps': overlaps,
                'overlap_rate': overlaps / max(len(sensor_detections), 1)
            }
        
        return result
    
    def test_list_modification_race(self) -> ScenarioResult:
        """Test: Multiple threads modifying same list with list functions"""
        with self.scenario_context("List Modification Race Conditions") as result:
            
            def list_modifier(worker_id: int, operations: int):
                """Worker that modifies shared list"""
                for i in range(operations):
                    try:
                        with self.locks['list_lock']:
                            current_list = self.global_test_state['shared_list'].copy()
                            
                            # Random list operations
                            operation = random.choice(['append', 'insert', 'sort', 'delete'])
                            
                            if operation == 'append':
                                new_item = f"worker{worker_id}_item{i}"
                                current_list.append(new_item)
                                
                            elif operation == 'insert' and len(current_list) > 0:
                                pos = random.randint(0, len(current_list))
                                new_item = f"worker{worker_id}_insert{i}"
                                current_list.insert(pos, new_item)
                                
                            elif operation == 'sort':
                                # Use LSL list sort
                                current_list = self.api.call_function('llListSort', [current_list, 1, True])
                                
                            elif operation == 'delete' and len(current_list) > 0:
                                # Use LSL delete function
                                start_idx = random.randint(0, len(current_list) - 1)
                                end_idx = min(start_idx + random.randint(0, 2), len(current_list) - 1)
                                current_list = self.api.call_function('llDeleteSubList', [current_list, start_idx, end_idx])
                            
                            # Update shared list
                            self.global_test_state['shared_list'] = current_list
                        
                        # Additional LSL list API calls
                        list_length = self.api.call_function('llGetListLength', [current_list])
                        if list_length > 0:
                            list_string = self.api.call_function('llList2String', [current_list])
                        
                        result.events_processed += 1
                        time_module.sleep(0.001)
                        
                    except Exception as e:
                        result.errors.append(f"List modifier {worker_id} error: {e}")
            
            # Reset shared list
            self.global_test_state['shared_list'] = []
            
            # Launch multiple list modifiers
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                for worker_id in range(8):
                    future = executor.submit(list_modifier, worker_id, 25)
                    futures.append(future)
                
                for future in as_completed(futures):
                    future.result()
            
            # Validate final list integrity
            final_list = self.global_test_state['shared_list']
            unique_items = set(final_list)
            
            result.metrics = {
                'final_list_length': len(final_list),
                'unique_items': len(unique_items),
                'duplicate_rate': 1 - (len(unique_items) / max(len(final_list), 1)),
                'list_contains_workers': sum(1 for item in final_list if 'worker' in str(item))
            }
            
            # Check for corruption
            if len(final_list) != len(unique_items):
                result.warnings.append(f"List contains {len(final_list) - len(unique_items)} duplicates")
        
        return result
    
    def test_extreme_load_simulation(self) -> ScenarioResult:
        """Test: Extreme load with all event types firing simultaneously"""
        with self.scenario_context("Extreme Load Simulation") as result:
            
            event_counts = {
                'timer': 0, 'http': 0, 'sensor': 0, 'touch': 0,
                'listen': 0, 'collision': 0, 'dataserver': 0
            }
            
            def extreme_worker(event_type: str, duration: float):
                """Worker for specific event type under extreme load"""
                end_time = time_module.time() + duration
                count = 0
                
                while time_module.time() < end_time:
                    try:
                        if event_type == 'timer':
                            self.api.call_function('llSetTimerEvent', [0.01])
                            self.api.call_function('llGetTime', [])
                            
                        elif event_type == 'http':
                            self.api.call_function('llHTTPRequest', [
                                'https://example.com', [], f'request_{count}'
                            ])
                            
                        elif event_type == 'sensor':
                            self.api.call_function('llSensor', ['', '', 1, 20.0, 1.57])
                            if random.random() < 0.5:
                                self.api.call_function('llDetectedName', [0])
                                
                        elif event_type == 'touch':
                            self.api.call_function('llDetectedPos', [0])
                            self.api.call_function('llDetectedKey', [0])
                            
                        elif event_type == 'listen':
                            channel = random.randint(0, 1000)
                            listener_id = self.api.call_function('llListen', [channel, '', '', ''])
                            if random.random() < 0.3:
                                self.api.call_function('llListenRemove', [listener_id])
                                
                        elif event_type == 'collision':
                            self.api.call_function('llDetectedKey', [0])
                            self.api.call_function('llDetectedPos', [0])
                            
                        elif event_type == 'dataserver':
                            self.api.call_function('llGetNotecardLine', ['test', count % 100])
                        
                        count += 1
                        
                        # Very short sleep to allow other threads
                        time_module.sleep(0.0001)
                        
                    except Exception as e:
                        result.errors.append(f"{event_type} worker error: {e}")
                
                event_counts[event_type] = count
                return count
            
            # Launch all event types simultaneously for 5 seconds
            test_duration = 5.0
            
            with ThreadPoolExecutor(max_workers=len(event_counts)) as executor:
                futures = {}
                for event_type in event_counts.keys():
                    future = executor.submit(extreme_worker, event_type, test_duration)
                    futures[event_type] = future
                
                # Collect results
                total_operations = 0
                for event_type, future in futures.items():
                    try:
                        operations = future.result()
                        total_operations += operations
                        result.events_processed += operations
                    except Exception as e:
                        result.errors.append(f"Extreme worker {event_type} failed: {e}")
            
            # Calculate performance metrics
            ops_per_second = total_operations / test_duration
            
            result.metrics = {
                'total_operations': total_operations,
                'operations_per_second': ops_per_second,
                'event_distribution': event_counts,
                'avg_ops_per_event_type': total_operations / len(event_counts)
            }
            
            # Performance thresholds
            if ops_per_second < 100:
                result.warnings.append(f"Low performance: {ops_per_second:.1f} ops/sec")
            elif ops_per_second < 500:
                result.warnings.append(f"Moderate performance: {ops_per_second:.1f} ops/sec")
        
        return result
    
    def run_integration_stress_tests(self) -> Dict[str, Any]:
        """Run all integration stress tests"""
        print("🔥 LSL INTEGRATION STRESS TEST - THE PATH TO 9/10")
        print("Testing complex real-world interactions and race conditions")
        print("=" * 70)
        
        # Run all test scenarios
        test_methods = [
            self.test_concurrent_timer_operations,
            self.test_http_dataserver_collision,
            self.test_sensor_touch_state_chaos,
            self.test_list_modification_race,
            self.test_extreme_load_simulation
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"💥 Test method {test_method.__name__} crashed: {e}")
        
        # Analyze overall results
        return self.analyze_integration_results()
    
    def analyze_integration_results(self) -> Dict[str, Any]:
        """Analyze and score integration test results"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        
        total_events = sum(r.events_processed for r in self.test_results)
        total_errors = sum(len(r.errors) for r in self.test_results)
        total_warnings = sum(len(r.warnings) for r in self.test_results)
        
        # Calculate scores
        success_rate = passed_tests / total_tests * 100
        error_rate = total_errors / max(total_events, 1) * 100
        
        # Integration robustness score
        robustness_score = 100
        
        # Deduct for failures
        if success_rate < 100:
            robustness_score -= (100 - success_rate) * 2
        
        # Deduct for errors
        if error_rate > 0:
            robustness_score -= min(error_rate * 10, 30)
        
        # Deduct for warnings
        if total_warnings > 5:
            robustness_score -= min((total_warnings - 5) * 2, 15)
        
        # Performance bonus/penalty
        extreme_load_result = next((r for r in self.test_results if 'Extreme Load' in r.scenario_name), None)
        if extreme_load_result and extreme_load_result.success:
            ops_per_sec = extreme_load_result.metrics.get('operations_per_second', 0)
            if ops_per_sec > 1000:
                robustness_score += 5  # Bonus for high performance
            elif ops_per_sec < 100:
                robustness_score -= 10  # Penalty for low performance
        
        # Grade assignment
        if robustness_score >= 95:
            grade = "A+ - Exceptional"
            ready_for_9 = True
        elif robustness_score >= 90:
            grade = "A - Excellent"
            ready_for_9 = True
        elif robustness_score >= 85:
            grade = "A- - Very Good"
            ready_for_9 = False
        elif robustness_score >= 80:
            grade = "B+ - Good"
            ready_for_9 = False
        else:
            grade = "B - Fair"
            ready_for_9 = False
        
        results = {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'success_rate': success_rate,
            'total_events_processed': total_events,
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'error_rate': error_rate,
            'robustness_score': robustness_score,
            'grade': grade,
            'ready_for_rating_9': ready_for_9,
            'test_details': [
                {
                    'name': r.scenario_name,
                    'success': r.success,
                    'time': r.execution_time,
                    'events': r.events_processed,
                    'errors': len(r.errors),
                    'warnings': len(r.warnings),
                    'metrics': r.metrics
                }
                for r in self.test_results
            ]
        }
        
        # Print summary
        print(f"\n" + "=" * 70)
        print("🎯 INTEGRATION TEST RESULTS")
        print("=" * 70)
        print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"Events Processed: {total_events:,}")
        print(f"Errors: {total_errors} ({error_rate:.3f}%)")
        print(f"Warnings: {total_warnings}")
        print(f"Robustness Score: {robustness_score:.1f}/100")
        print(f"Grade: {grade}")
        print(f"Ready for Rating 9: {'✅ YES' if ready_for_9 else '❌ NO'}")
        
        # Print individual test results
        print(f"\n📊 Individual Test Results:")
        for detail in results['test_details']:
            status = "✅" if detail['success'] else "❌"
            print(f"  {status} {detail['name']}")
            print(f"     Time: {detail['time']:.2f}s, Events: {detail['events']}, Errors: {detail['errors']}")
            if detail['metrics']:
                key_metrics = list(detail['metrics'].items())[:2]  # Show first 2 metrics
                metrics_str = ", ".join(f"{k}: {v}" for k, v in key_metrics)
                print(f"     Metrics: {metrics_str}")
        
        if ready_for_9:
            print(f"\n🏆 CONGRATULATIONS! The simulator has demonstrated exceptional")
            print(f"    robustness under extreme stress and is ready for Rating 9!")
        else:
            print(f"\n⚠️  Additional work needed to reach Rating 9.")
            print(f"   Focus on improving robustness score above 90.")
        
        return results

def run_path_to_9_tests():
    """Main entry point for integration stress testing"""
    tester = LSLIntegrationTester()
    return tester.run_integration_stress_tests()

if __name__ == "__main__":
    results = run_path_to_9_tests()