import argparse
import threading
import time
import readline
from lsl_antlr_parser import LSLParser
from lsl_simulator import LSLSimulator

def print_source_line_with_context(simulator):
    """Print current line and surrounding context (5 lines before and after)"""
    info = simulator.next_statement_info
    
    # Handle case where info is a string instead of dict
    if isinstance(info, str):
        print(f"\033[91m-> ???: {info}\033[0m")
        return
    
    # Use the same line finding logic as print_source_line
    current_line = find_source_line(simulator, info)
    
    # Print context: 5 lines before and 5 after current line
    start = max(1, current_line - 5)
    end = min(len(simulator.source_lines), current_line + 5)
    
    for i in range(start, end + 1):
        if i <= len(simulator.source_lines):
            line_content = simulator.source_lines[i-1].rstrip()
            if i == current_line:
                print(f"\033[93m-> {i:3d}: {line_content}\033[0m")
            else:
                print(f"   {i:3d}: {line_content}")

def find_all_functions(simulator):
    """Find all user-defined functions in the source code"""
    functions = []
    lines = simulator.source_lines
    
    # Common LSL event names to exclude
    event_names = [
        'state_entry', 'dataserver', 'http_response', 'sensor', 'no_sensor',
        'listen', 'timer', 'touch_start', 'touch', 'touch_end', 'changed',
        'collision_start', 'collision', 'collision_end', 'land_collision_start',
        'land_collision', 'land_collision_end', 'at_target', 'not_at_target',
        'at_rot_target', 'not_at_rot_target', 'money', 'email', 'run_time_permissions',
        'attach', 'on_rez', 'object_rez', 'link_message', 'moving_start', 'moving_end'
    ]
    
    for i, line in enumerate(lines):
        line_content = line.strip()
        
        # Skip comments and empty lines
        if not line_content or line_content.startswith('//'):
            continue
            
        # Look for function definitions
        # Pattern 1: function_name() { (same line)
        # Pattern 2: function_name() followed by { on next line
        if '(' in line_content and ')' in line_content:
            # Check if it's a function definition (has opening brace somewhere)
            has_brace_same_line = '{' in line_content
            has_brace_next_line = (i + 1 < len(lines) and 
                                 lines[i + 1].strip() == '{')
            
            if has_brace_same_line or has_brace_next_line:
                # Extract potential function name
                before_paren = line_content.split('(')[0].strip()
                
                # Skip if it's an event handler
                is_event = any(event in before_paren.lower() for event in event_names)
                
                # Skip control structures and other non-functions
                is_control = any(keyword in before_paren.lower() for keyword in 
                               ['if', 'while', 'for', 'else', 'return', 'switch'])
                
                # Skip API calls (starting with ll or os)
                is_api_call = any(before_paren.strip().startswith(prefix) for prefix in 
                                ['ll', 'os'])
                
                if not is_event and not is_control and not is_api_call:
                    # Extract function name (last word before parentheses)
                    words = before_paren.split()
                    if words:
                        func_name = words[-1]
                        # Additional validation: should be a valid identifier
                        if (func_name.replace('_', '').replace('-', '').isalnum() and 
                            not func_name.isdigit()):
                            functions.append({'name': func_name, 'line': i + 1})
    
    return functions

def find_all_events(simulator):
    """Find all event handlers in the current state"""
    events = []
    lines = simulator.source_lines
    
    # Common LSL event names
    event_names = [
        'state_entry', 'dataserver', 'http_response', 'sensor', 'no_sensor',
        'listen', 'timer', 'touch_start', 'touch', 'touch_end', 'changed',
        'collision_start', 'collision', 'collision_end', 'land_collision_start',
        'land_collision', 'land_collision_end', 'at_target', 'not_at_target',
        'at_rot_target', 'not_at_rot_target', 'money', 'email', 'run_time_permissions',
        'attach', 'on_rez', 'object_rez', 'link_message', 'moving_start', 'moving_end'
    ]
    
    for i, line in enumerate(lines):
        line_content = line.strip()
        for event_name in event_names:
            if (line_content and not line_content.startswith('//') and
                f'{event_name}(' in line_content.lower()):
                events.append({'name': event_name, 'line': i + 1})
                break
    
    return events

def list_function_or_event(simulator, target):
    """List a specific function, event handler, or all functions/events"""
    target_lower = target.lower()
    
    # Handle special commands
    if target_lower == 'functions':
        functions = find_all_functions(simulator)
        if functions:
            print("User-defined functions:")
            for func in functions:
                print(f"   {func['name']:20} (line {func['line']})")
        else:
            print("No user-defined functions found.")
        return
    
    if target_lower == 'events':
        events = find_all_events(simulator)
        if events:
            print("Event handlers:")
            for event in events:
                print(f"   {event['name']:20} (line {event['line']})")
        else:
            print("No event handlers found.")
        return
    
    # Original function/event listing code
    lines = simulator.source_lines
    
    # Look for function definition
    found_start = None
    found_end = None
    in_block = False
    brace_count = 0
    
    for i, line in enumerate(lines):
        line_content = line.strip()
        
        # Check if this line contains the target function/event
        if not found_start and target_lower in line_content.lower():
            # More specific matching for events and functions
            if (f"{target_lower}(" in line_content.lower() or 
                f" {target_lower}(" in line_content.lower() or
                line_content.lower().startswith(target_lower + "(") or
                line_content.lower().strip().endswith(f"{target_lower}()")):
                found_start = i
                in_block = True
                print(f"Found {target} starting at line {i+1}:")
        
        if in_block:
            # Count braces to find the end of the function/event
            brace_count += line_content.count('{')
            brace_count -= line_content.count('}')
            
            # Print the line
            line_num = i + 1
            print(f"   {line_num:3d}: {line.rstrip()}")
            
            # If we've closed all braces, we're done
            if brace_count == 0 and found_start is not None:
                found_end = i
                break
    
    if found_start is None:
        print(f"Function or event '{target}' not found.")
    elif found_end is None:
        print(f"Warning: End of {target} not found (possible syntax error)")

def find_source_line(simulator, info):
    """Find the actual source line number for a statement"""
    stmt_type = info.get('type')
    
    if stmt_type == 'declaration':
        var_name = info.get('name', '')
        var_type = info.get('lsl_type', '')
        for i, line in enumerate(simulator.source_lines):
            if var_name in line and var_type in line and '=' in line and line.strip():
                return i + 1
                
    elif stmt_type == 'simple':
        statement_text = info.get('statement', '')
        if statement_text:
            # Extract function name
            if '(' in statement_text:
                func_name = statement_text.split('(')[0].strip()
                
                # For function calls, find the line containing the function
                for i, line in enumerate(simulator.source_lines):
                    if func_name in line and line.strip() and not line.strip().startswith('//'):
                        # For llSay, also try to match message content
                        if func_name == 'llSay':
                            import re
                            quotes = re.findall(r'"([^"]*)"', statement_text)
                            if quotes and any(quote in line for quote in quotes if len(quote) > 5):
                                return i + 1
                        else:
                            return i + 1
    
    # Fallback: try to get line from parser info
    line_num = info.get('line', -1)
    if line_num != -1 and line_num <= len(simulator.source_lines):
        return line_num
    
    return 1  # Default fallback

def print_source_line(simulator):
    """Print just the current executing line (for compatibility)"""
    info = simulator.next_statement_info
    
    # Handle case where info is a string instead of dict
    if isinstance(info, str):
        print(f"\033[91m-> ???: {info}\033[0m")
        return
    
    # Use the helper function to find the line
    line_num = find_source_line(simulator, info)
    
    if line_num <= len(simulator.source_lines):
        source_line = simulator.source_lines[line_num - 1]
        print(f"\033[93m-> {line_num:3d}: {source_line.strip()}\033[0m")
    else:
        print(f"\033[91m-> ???: {info}\033[0m")

def find_function_or_event_line(simulator, name):
    """Find the line number of the first executable statement in a function or event by name"""
    functions = find_all_functions(simulator)
    events = find_all_events(simulator)
    
    # Check functions first
    for func in functions:
        if func['name'] == name:
            return find_first_executable_line(simulator, func['line'])
    
    # Check events
    for event in events:
        if event['name'] == name:
            return find_first_executable_line(simulator, event['line'])
    
    return None

def find_first_executable_line(simulator, start_line):
    """Find the first executable statement after the function/event declaration"""
    lines = simulator.source_lines
    
    # Start looking from the line after the function/event declaration
    for i in range(start_line, len(lines)):
        line = lines[i].strip()
        
        # Skip empty lines, comments, and opening braces
        if not line or line.startswith('//') or line == '{':
            continue
            
        # Found the first executable statement
        return i + 1  # Convert to 1-based line numbering
    
    # Fallback to original line if no executable statement found
    return start_line

def setup_autocompletion(simulator):
    """Setup tab autocompletion for function and event names"""
    functions = find_all_functions(simulator)
    events = find_all_events(simulator)
    
    # Create completion lists
    function_names = [f['name'] for f in functions]
    event_names = [e['name'] for e in events]
    
    # Add special commands
    special_commands = ['functions', 'events']
    
    all_completions = function_names + event_names + special_commands
    
    def completer(text, state):
        # Get the current line being edited
        line = readline.get_line_buffer()
        
        # Complete after 'l ' or 'b ' commands
        if ((line.startswith('l ') or line.startswith('b ')) and len(line.split()) <= 2):
            matches = [item for item in all_completions if item.startswith(text)]
            if state < len(matches):
                return matches[state]
        return None
    
    readline.set_completer(completer)
    readline.parse_and_bind("tab: complete")
    
    return function_names, event_names

def main():
    parser = argparse.ArgumentParser(description="Debug an LSL script step-by-step.")
    parser.add_argument("filename", help="The LSL script file to debug.")
    args = parser.parse_args()

    try:
        with open(args.filename, "r") as f:
            lsl_code = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{args.filename}'")
        return

    print("--- LSL Debugger ---")
    lsl_parser = LSLParser()
    parsed_script = lsl_parser.parse(lsl_code)
    
    simulator = LSLSimulator(parsed_script, debug_mode=True, source_code=lsl_code)
    
    # Set single_step to true so the simulator will pause at the first statement
    # Use "into" mode for the initial step to ensure we pause regardless of call depth
    simulator.single_step = True
    simulator.step_mode = "into"
    
    # Setup autocompletion
    function_names, event_names = setup_autocompletion(simulator)
    
    # Start the simulator in a background thread
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()

    # The simulator will pause on its own at the first statement.
    # We just need to wait for it.
    simulator.debugger_ready.wait()

    print("Debugger started. Type 'h' for help.")
    print(f"Available functions: {', '.join(function_names) if function_names else 'None'}")
    print(f"Available events: {', '.join(event_names) if event_names else 'None'}")
    
    last_command = ""  # Track the last command for repeat functionality
    last_list_line = 1  # Track the last line shown by 'l' command for continuation
    
    while True:
        if not sim_thread.is_alive():
            print("--- Program has finished ---")
            break

        print_source_line_with_context(simulator)
        command = input("(lsldb) ").strip()
        
        # If empty input, repeat last command
        if not command and last_command:
            command = last_command
            print(f"Repeating: {command}")
        elif command:  # Only update last_command if user entered something
            last_command = command
            # Reset list continuation for non-list commands
            if not command.startswith('l'):
                last_list_line = 1
            
        cmd_parts = command.split()
        cmd = cmd_parts[0] if cmd_parts else ''

        if cmd == 'q':
            simulator.stop()
            break
        elif cmd == 'h':
            print("Commands: (n)ext, (i)nto, (c)ontinue, (p)rint [var], (g)lobals, (l)ist [function/event/functions/events/line], (b)reak <line|function|event>, (cb) clear break, (ca) clear all, (lb) list breaks, (q)uit")
            print("Use TAB for autocompletion of function/event names after 'l ' or 'b '.")
        elif cmd == 'n':
            simulator.step()
            simulator.debugger_ready.wait() # Wait for the next pause
        elif cmd == 'i':
            simulator.step_into()
            simulator.debugger_ready.wait() # Wait for the next pause
        elif cmd == 'c':
            simulator.continue_execution()
            # If there are more breakpoints, wait for the next one
            if simulator.breakpoints:
                 simulator.debugger_ready.wait()
        elif cmd == 'b':
            if len(cmd_parts) > 1:
                target = cmd_parts[1]
                if target.isdigit():
                    # Line number
                    line_num = int(target)
                    simulator.breakpoints.add(line_num)
                    print(f"Breakpoint set at line {line_num}")
                else:
                    # Function or event name
                    line_num = find_function_or_event_line(simulator, target)
                    if line_num:
                        simulator.breakpoints.add(line_num)
                        print(f"Breakpoint set at {target} (line {line_num})")
                    else:
                        print(f"Function or event '{target}' not found.")
            else:
                print("Usage: b <line_number|function_name|event_name>")
        elif cmd == 'cb':
            if len(cmd_parts) > 1 and cmd_parts[1].isdigit():
                line_num = int(cmd_parts[1])
                if line_num in simulator.breakpoints:
                    simulator.breakpoints.remove(line_num)
                    print(f"Breakpoint cleared at line {line_num}")
                else:
                    print(f"No breakpoint at line {line_num}")
            else:
                print("Usage: cb <line_number>")
        elif cmd == 'ca':
            if simulator.breakpoints:
                count = len(simulator.breakpoints)
                simulator.breakpoints.clear()
                print(f"Cleared {count} breakpoint(s)")
            else:
                print("No breakpoints to clear")
        elif cmd == 'lb':
            if simulator.breakpoints:
                print("Breakpoints:")
                for line_num in sorted(simulator.breakpoints):
                    print(f"  Line {line_num}")
            else:
                print("No breakpoints set")
        elif cmd == 'p':
            if len(cmd_parts) > 1:
                var_name = cmd_parts[1]
                # Check locals first
                local_vars = simulator.get_variables("locals")
                global_vars = simulator.get_variables("globals")
                
                found_in_local = local_vars and var_name in local_vars
                found_in_global = global_vars and var_name in global_vars
                
                if found_in_local and found_in_global and local_vars != global_vars:
                    # Variable exists in both scopes, show both
                    print(f"  {var_name} = {local_vars[var_name]} (local)")
                    print(f"  {var_name} = {global_vars[var_name]} (global)")
                elif found_in_local:
                    scope_name = "local" if local_vars != global_vars else "global"
                    print(f"  {var_name} = {local_vars[var_name]} ({scope_name})")
                elif found_in_global:
                    print(f"  {var_name} = {global_vars[var_name]} (global)")
                else:
                    print(f"Variable '{var_name}' not found.")
            else:
                # Show all variables with scope indication
                local_vars = simulator.get_variables("locals")
                global_vars = simulator.get_variables("globals")
                
                if local_vars and local_vars != global_vars:
                    print("Local variables:")
                    for name, value in local_vars.items():
                        print(f"  {name} = {value}")
                
                if global_vars:
                    scope_label = "Global variables:" if (local_vars and local_vars != global_vars) else "Variables:"
                    print(scope_label)
                    for name, value in global_vars.items():
                        # Only show globals that aren't already shown as locals
                        if not local_vars or local_vars == global_vars or name not in local_vars:
                            print(f"  {name} = {value}")
                
                if not local_vars and not global_vars:
                    print("No variables in current scope.")
        elif cmd == 'g':
            variables = simulator.get_variables("globals")
            if variables:
                for name, value in variables.items():
                    print(f"  {name} = {value}")
            else:
                print("No global variables.")
        elif cmd == 'l':
            if len(cmd_parts) > 1:
                target = cmd_parts[1]
                # Check if target is a number (line number)
                if target.isdigit():
                    # List from specific line number
                    start_line = int(target)
                    end_line = min(len(simulator.source_lines), start_line + 10)
                    last_list_line = end_line  # Update for continuation
                    
                    info = simulator.next_statement_info
                    current_line = find_source_line(simulator, info) if not isinstance(info, str) else 1
                    
                    for i in range(start_line, end_line + 1):
                        if i <= len(simulator.source_lines):
                            line_content = simulator.source_lines[i-1].rstrip()
                            if i == current_line:
                                print(f"\033[93m-> {i:3d}: {line_content}\033[0m")
                            else:
                                print(f"   {i:3d}: {line_content}")
                else:
                    # Handle 'l <function>' or 'l <event>'
                    list_function_or_event(simulator, target)
            else:
                # Handle list continuation or initial list
                if last_command == 'l' and last_list_line > 0:
                    # Continue listing from where we left off
                    start_line = last_list_line + 1
                    end_line = min(len(simulator.source_lines), start_line + 10)
                    last_list_line = end_line
                    
                    info = simulator.next_statement_info
                    current_line = find_source_line(simulator, info) if not isinstance(info, str) else 1
                    
                    for i in range(start_line, end_line + 1):
                        if i <= len(simulator.source_lines):
                            line_content = simulator.source_lines[i-1].rstrip()
                            if i == current_line:
                                print(f"\033[93m-> {i:3d}: {line_content}\033[0m")
                            else:
                                print(f"   {i:3d}: {line_content}")
                else:
                    # List source code around current line (first time)
                    info = simulator.next_statement_info
                    
                    if isinstance(info, str):
                        current_line = 1
                    else:
                        current_line = find_source_line(simulator, info)
                    
                    start = max(1, current_line - 5)
                    end = min(len(simulator.source_lines), current_line + 5)
                    last_list_line = end  # Set for next continuation
                    
                    for i in range(start, end + 1):
                        if i <= len(simulator.source_lines):
                            line_content = simulator.source_lines[i-1].rstrip()
                            if i == current_line:
                                print(f"\033[93m-> {i:3d}: {line_content}\033[0m")
                            else:
                                print(f"   {i:3d}: {line_content}")
        else:
            print("Unknown command. Type 'h' for help.")
    
    # Final cleanup
    simulator.stop()
    sim_thread.join(timeout=0.5)

if __name__ == "__main__":
    main()
