import argparse
import threading
import time
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

def list_function_or_event(simulator, target):
    """List a specific function or event handler"""
    lines = simulator.source_lines
    target_lower = target.lower()
    
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
                line_content.lower().startswith(target_lower + "(")):
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
    
    # Start the simulator in a background thread
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()

    # The simulator will pause on its own at the first statement.
    # We just need to wait for it.
    simulator.debugger_ready.wait()

    print("Debugger started. Type 'h' for help.")
    
    last_command = ""  # Track the last command for repeat functionality
    
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
            
        cmd_parts = command.split()
        cmd = cmd_parts[0] if cmd_parts else ''

        if cmd == 'q':
            simulator.stop()
            break
        elif cmd == 'h':
            print("Commands: (n)ext, (i)nto, (c)ontinue, (p)rint [var], (g)lobals, (l)ist [function/event], (b)reak <line>, (cb) clear break, (ca) clear all, (lb) list breaks, (q)uit")
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
            if len(cmd_parts) > 1 and cmd_parts[1].isdigit():
                line_num = int(cmd_parts[1])
                simulator.breakpoints.add(line_num)
                print(f"Breakpoint set at line {line_num}")
            else:
                print("Usage: b <line_number>")
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
                # Handle 'l <function>' or 'l <event>'
                target = cmd_parts[1]
                list_function_or_event(simulator, target)
            else:
                # List source code around current line
                info = simulator.next_statement_info
                
                if isinstance(info, str):
                    current_line = 1
                else:
                    current_line = find_source_line(simulator, info)
                
                start = max(1, current_line - 5)
                end = min(len(simulator.source_lines), current_line + 5)
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
