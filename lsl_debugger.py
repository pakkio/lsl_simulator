import argparse
import threading
import time
from lsl_parser import LSLParser
from lsl_simulator import LSLSimulator

def print_source_line(simulator):
    info = simulator.next_statement_info
    stmt_type = info.get('type')
    
    # Always search for the actual source line since parser line numbers are unreliable
    if stmt_type == 'declaration':
        var_name = info.get('name', '')
        var_type = info.get('lsl_type', '')
        # Find the actual declaration line in the source
        for i, line in enumerate(simulator.source_lines):
            if var_name in line and var_type in line and '=' in line and line.strip():
                actual_line_num = i + 1
                print(f"-> {actual_line_num:3d}: {line.strip()}")
                return
        print(f"-> ???: declaring {var_type} {var_name}")
        
    elif stmt_type == 'simple':
        statement_text = info.get('statement', '')
        if statement_text:
            # Look for function name and key parts of the statement
            search_terms = []
            if '(' in statement_text:
                func_name = statement_text.split('(')[0].strip()
                search_terms.append(func_name)
            
            # Also try to match quoted strings in the statement
            import re
            quotes = re.findall(r'"([^"]*)"', statement_text)
            if quotes:
                search_terms.extend(quotes[:2])  # Use first 2 quotes for better matching
            
            # Search for the actual line - be more specific for llSay statements
            if statement_text.startswith('llSay'):
                # For llSay, try to match the message content more specifically
                for term in search_terms:
                    if term and len(term) > 8:  # Use longer strings for better matching
                        best_match = None
                        best_score = 0
                        for i, line in enumerate(simulator.source_lines):
                            if term in line and line.strip() and not line.strip().startswith('//'):
                                # Count how many terms match for better selection
                                score = sum(1 for t in search_terms if t in line)
                                if score > best_score:
                                    best_score = score
                                    best_match = i + 1
                        if best_match:
                            print(f"-> {best_match:3d}: {simulator.source_lines[best_match-1].strip()}")
                            return
            else:
                # For non-llSay statements, use the original logic
                for term in search_terms:
                    if term and len(term) > 3:
                        for i, line in enumerate(simulator.source_lines):
                            if term in line and line.strip() and not line.strip().startswith('//'):
                                actual_line_num = i + 1
                                print(f"-> {actual_line_num:3d}: {line.strip()}")
                                return
            
            # Fallback if no match found
            print(f"-> ???: {statement_text}")
        else:
            print(f"-> ???: Unknown statement")
    else:
        line_num = info.get('line', -1)
        if line_num != -1 and line_num <= len(simulator.source_lines):
            source_line = simulator.source_lines[line_num - 1]
            print(f"-> {line_num:3d}: {source_line.strip()}")
        else:
            print(f"-> ???: {info}")

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
    simulator.single_step = True
    
    # Start the simulator in a background thread
    sim_thread = threading.Thread(target=simulator.run)
    sim_thread.daemon = True
    sim_thread.start()

    # The simulator will pause on its own at the first statement.
    # We just need to wait for it.
    simulator.debugger_ready.wait()

    print("Debugger started. Type 'h' for help.")
    
    while True:
        if not sim_thread.is_alive():
            print("--- Program has finished ---")
            break

        print_source_line(simulator)
        command = input("(lsldb) ").strip()
        cmd_parts = command.split()
        cmd = cmd_parts[0] if cmd_parts else ''

        if cmd == 'q':
            simulator.stop()
            break
        elif cmd == 'h':
            print("Commands: (n)ext, (c)ontinue, (p)rint [var], (g)lobals, (l)ist, (b)reak <line>, (q)uit")
        elif cmd == 'n':
            simulator.step()
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
        elif cmd == 'p':
            if len(cmd_parts) > 1:
                var_name = cmd_parts[1]
                variables = simulator.get_variables("locals")
                if variables and var_name in variables:
                    print(f"  {var_name} = {variables[var_name]}")
                else:
                    variables = simulator.get_variables("globals")
                    if variables and var_name in variables:
                        print(f"  {var_name} = {variables[var_name]}")
                    else:
                        print(f"Variable '{var_name}' not found.")
            else:
                variables = simulator.get_variables("locals")
                if variables:
                    for name, value in variables.items():
                        print(f"  {name} = {value}")
                else:
                    print("No local variables in the current scope.")
        elif cmd == 'g':
            variables = simulator.get_variables("globals")
            if variables:
                for name, value in variables.items():
                    print(f"  {name} = {value}")
            else:
                print("No global variables.")
        elif cmd == 'l':
            # List source code around current line
            info = simulator.next_statement_info
            stmt_type = info.get('type')
            
            # Find the actual current line using same logic as print_source_line
            current_line = 1
            if stmt_type == 'declaration':
                var_name = info.get('name', '')
                var_type = info.get('lsl_type', '')
                for i, line in enumerate(simulator.source_lines):
                    if var_name in line and var_type in line and '=' in line and line.strip():
                        current_line = i + 1
                        break
            elif stmt_type == 'simple':
                statement_text = info.get('statement', '')
                if statement_text:
                    search_terms = []
                    if '(' in statement_text:
                        func_name = statement_text.split('(')[0].strip()
                        search_terms.append(func_name)
                    
                    import re
                    quotes = re.findall(r'"([^"]*)"', statement_text)
                    if quotes:
                        search_terms.extend(quotes[:2])
                    
                    # Use same improved matching logic as print_source_line
                    if statement_text.startswith('llSay'):
                        for term in search_terms:
                            if term and len(term) > 8:
                                best_match = None
                                best_score = 0
                                for i, line in enumerate(simulator.source_lines):
                                    if term in line and line.strip() and not line.strip().startswith('//'):
                                        score = sum(1 for t in search_terms if t in line)
                                        if score > best_score:
                                            best_score = score
                                            best_match = i + 1
                                if best_match:
                                    current_line = best_match
                                    break
                    else:
                        for term in search_terms:
                            if term and len(term) > 3:
                                for i, line in enumerate(simulator.source_lines):
                                    if term in line and line.strip() and not line.strip().startswith('//'):
                                        current_line = i + 1
                                        break
                                if current_line > 1:
                                    break
            
            start = max(1, current_line - 5)
            end = min(len(simulator.source_lines), current_line + 5)
            for i in range(start, end + 1):
                prefix = "->" if i == current_line else "  "
                if i <= len(simulator.source_lines):
                    print(f"{prefix} {i:3d}: {simulator.source_lines[i-1]}")
        else:
            print("Unknown command. Type 'h' for help.")
    
    # Final cleanup
    simulator.stop()
    sim_thread.join(timeout=0.5)

if __name__ == "__main__":
    main()
