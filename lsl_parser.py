import re
import json

class LSLParser:
    def _remove_comments(self, code):
        """Remove // comments but preserve // inside string literals"""
        result = []
        i = 0
        in_string = False
        string_char = None
        
        while i < len(code):
            char = code[i]
            
            if not in_string:
                if char in ['"', "'"]:
                    in_string = True
                    string_char = char
                elif char == '/' and i + 1 < len(code) and code[i + 1] == '/':
                    # Found comment start outside string - skip to end of line
                    while i < len(code) and code[i] != '\n':
                        i += 1
                    continue  # Don't append the comment characters
            else:
                if char == string_char and (i == 0 or code[i-1] != '\\'):
                    in_string = False
                    string_char = None
            
            result.append(char)
            i += 1
        
        return ''.join(result)
    
    def parse(self, code):
        script = {"globals": [], "states": {}}
        # Remove comments but preserve // inside string literals
        code = self._remove_comments(code)

        # Find globals (everything before the first state)
        first_state_match = re.search(r"\b(default|state)\b", code)
        globals_code = code[:first_state_match.start()] if first_state_match else ""
        
        global_var_pattern = re.compile(r"\b(string|integer|key|float|vector|list|rotation)\s+([\w\d_]+)\s*(?:=\s*(.*?))?;")
        for match in global_var_pattern.finditer(globals_code):
            g_type, g_name, g_val = match.groups()
            if g_val: g_val = g_val.strip().strip('"')
            script["globals"].append({"type": g_type, "name": g_name, "value": g_val})

        # Find user-defined functions (search entire code, not just globals)
        script["functions"] = {}
        
        # Pattern for functions with explicit return types
        func_pattern = re.compile(r"\b(string|integer|key|float|vector|list|rotation|void)\s+([\w\d_]+)\s*\((.*?)\)\s*\{")
        for func_match in func_pattern.finditer(code):  # Search entire code
            return_type, func_name, func_args = func_match.groups()
            # This is a trick to make sure we're not accidentally parsing an event handler
            if func_name in ["state_entry", "touch_start", "listen", "timer", "dataserver", "http_response"]:
                continue
            
            func_body_text = self._extract_braced_block(code, func_match.end())
            script["functions"][func_name] = {
                "return_type": return_type,
                "args": [arg.strip() for arg in func_args.split(',')],
                "body": self._parse_statements(func_body_text)
            }
        
        # Pattern for implicit void functions (no return type)
        void_func_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)\s*\{")
        for func_match in void_func_pattern.finditer(code):  # Search entire code
            func_name, func_args = func_match.groups()
            
            # Skip if already found with explicit return type
            if func_name in script["functions"]:
                continue
                
            # Skip event handlers, keywords, and built-in types
            if func_name in ["state_entry", "touch_start", "listen", "timer", "dataserver", "http_response", 
                           "sensor", "no_sensor", "changed", "collision_start", "collision_end",
                           "string", "integer", "key", "float", "vector", "list", "rotation", "void", "default",
                           "if", "else", "for", "while", "do", "return", "jump", "state"]:
                continue
            
            func_body_text = self._extract_braced_block(code, func_match.end())
            script["functions"][func_name] = {
                "return_type": "void",
                "args": [arg.strip() for arg in func_args.split(',')],
                "body": self._parse_statements(func_body_text)
            }

        # Find states
        state_pattern = re.compile(r"\b(default|state\s+\w+)\s*\{")
        for state_match in state_pattern.finditer(code):
            state_header = state_match.group(1)
            state_name = state_header if state_header == 'default' else state_header.split()[1]
            state_body_text = self._extract_braced_block(code, state_match.end())
            
            # Calculate the line number of the state
            line_num = code.count('\n', 0, state_match.start()) + 1
            
            script["states"][state_name] = self._parse_event_handlers(state_body_text, line_num)
            
        return script

    def _parse_event_handlers(self, state_body, starting_line_num):
        handlers = {}
        event_pattern = re.compile(r"\b(\w+)\s*\((.*?)\)\s*\{")
        pos = 0
        while pos < len(state_body):
            match = event_pattern.search(state_body, pos)
            if not match: break
            
            event_name, event_args = match.groups()
            event_body_text = self._extract_braced_block(state_body, match.end())
            
            # Calculate the line number of the event handler
            line_num = starting_line_num + state_body.count('\n', 0, match.start())
            
            handlers[event_name] = {
                "args": event_args,
                "body": self._parse_statements(event_body_text, line_num)
            }
            pos = match.start() + len(match.group(0)) + len(event_body_text) + 2
        return handlers

    def _parse_statements(self, code_block, starting_line_num=1):
        statements = []
        pos = 0
        
        # The code block passed to this function is stripped of outer braces,
        # but may have leading/trailing whitespace including newlines.
        # We need to account for those newlines to get the correct starting line.
        initial_newlines = len(re.match(r"\s*", code_block).group(0).split('\n')) - 1
        current_line_num = starting_line_num + initial_newlines
        
        code_block = code_block.strip()
        
        while pos < len(code_block):
            # Store the line number at the beginning of the current statement search
            line_at_stmt_start = current_line_num + (code_block.count('\n', 0, pos))

            # Look for if statements
            if_match = re.match(r"\s*if\s*\((.*?)\)\s*\{", code_block[pos:])
            if if_match:
                condition = if_match.group(1)
                body_text = self._extract_braced_block(code_block, pos + if_match.end())
                
                # Check for an else block
                else_text = None
                else_match = re.match(r"\s*else\s*\{", code_block[pos + if_match.end() + len(body_text) + 2:])
                if else_match:
                    else_text = self._extract_braced_block(code_block, pos + if_match.end() + len(body_text) + 2 + else_match.end())
                
                statements.append({
                    "type": "if",
                    "condition": condition,
                    "then_body": self._parse_statements(body_text, line_at_stmt_start),
                    "else_body": self._parse_statements(else_text, line_at_stmt_start) if else_text else [],
                    "line": line_at_stmt_start
                })
                
                pos += if_match.end() + len(body_text) + 2
                if else_text is not None: pos += else_match.end() + len(else_text) + 2
                continue

            # Look for local variable declarations
            decl_match = re.match(r"\s*\b(string|integer|key|float|vector|list|rotation)\s+([\w\d_]+)\s*(?:=\s*(.*?))?;", code_block[pos:])
            if decl_match:
                var_type, var_name, var_val = decl_match.groups()
                statements.append({
                    "type": "declaration",
                    "lsl_type": var_type,
                    "name": var_name,
                    "value": var_val.strip() if var_val else None,
                    "line": line_at_stmt_start
                })
                # Find the semicolon to advance the position
                end_of_stmt = code_block.find(';', pos)
                pos = end_of_stmt + 1 if end_of_stmt != -1 else len(code_block)
                continue

            # Look for return statements
            return_match = re.match(r"\s*return\s*(.*);", code_block[pos:])
            if return_match:
                return_value = return_match.group(1).strip()
                statements.append({
                    "type": "return",
                    "value": return_value if return_value else None,
                    "line": line_at_stmt_start
                })
                # A return statement is always the last thing in a block to be executed
                break

            # Look for for loops
            for_match = re.match(r"\s*for\s*\((.*?);(.*?);(.*?)\)\s*\{", code_block[pos:])
            if for_match:
                init, cond, incr = for_match.groups()
                body_text = self._extract_braced_block(code_block, pos + for_match.end())
                statements.append({
                    "type": "for",
                    "init": init.strip(),
                    "condition": cond.strip(),
                    "increment": incr.strip(),
                    "body": self._parse_statements(body_text, line_at_stmt_start),
                    "line": line_at_stmt_start
                })
                pos += for_match.end() + len(body_text) + 2
                continue

            # Look for while loops
            while_match = re.match(r"\s*while\s*\((.*?)\)\s*\{", code_block[pos:])
            if while_match:
                condition = while_match.group(1)
                body_text = self._extract_braced_block(code_block, pos + while_match.end())
                statements.append({
                    "type": "while",
                    "condition": condition,
                    "body": self._parse_statements(body_text, line_at_stmt_start),
                    "line": line_at_stmt_start
                })
                pos += while_match.end() + len(body_text) + 2
                continue

            # Otherwise, it's a simple statement ending in a semicolon
            end_of_stmt = code_block.find(';', pos)
            if end_of_stmt != -1:
                stmt_str = code_block[pos:end_of_stmt].strip()
                if stmt_str: 
                    statements.append({
                        "type": "simple",
                        "statement": stmt_str,
                        "line": line_at_stmt_start
                    })
                pos = end_of_stmt + 1
            else:
                break # No more statements
                
        return statements

    def _extract_braced_block(self, text, start_pos):
        brace_level = 1
        pos = start_pos
        while pos < len(text):
            if text[pos] == '{': brace_level += 1
            elif text[pos] == '}': brace_level -= 1
            if brace_level == 0:
                return text[start_pos:pos]
            pos += 1
        return text[start_pos:] # Should not happen in well-formed code

if __name__ == "__main__":
    try:
        with open("advanced.lsl", "r") as f: # Using a more complex script for testing
            lsl_code = f.read()
        
        parser = LSLParser()
        parsed_result = parser.parse(lsl_code)
        
        print("--- Pragmatic Parser Test (SUCCESS) ---")
        print(json.dumps(parsed_result, indent=2))

    except FileNotFoundError:
        print("Error: advanced.lsl not found.")