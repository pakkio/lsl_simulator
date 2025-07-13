
import json
from lsl_parser import LSLParser

class LSLLinter:
    def __init__(self, parsed_script):
        self.parsed_script = parsed_script
        self.warnings = []
        self.symbol_table = {}

    def lint(self):
        """Performs a series of checks on the parsed script."""
        # First, populate the symbol table with global variables
        for var in self.parsed_script.get("globals", []):
            self.symbol_table[var["name"]] = var["type"]

        # Now, check each event handler
        for state_name, state_data in self.parsed_script.get("states", {}).items():
            for event_name, event_data in state_data.items():
                self._lint_block(state_data[event_name]["body"], f"State '{state_name}', Event '{event_name}'")
        
        return self.warnings

    def _lint_block(self, statements, context):
        """Recursively lints a block of statements."""
        local_symbols = {} # Create a new scope for this block

        for stmt in statements:
            if isinstance(stmt, dict):
                if stmt.get("type") == "declaration":
                    # Add to local symbols and check initial assignment
                    local_symbols[stmt["name"]] = stmt["lsl_type"]
                    if stmt["value"] is not None:
                        self._check_assignment(stmt["name"], stmt["value"], local_symbols, context)
                
                # Recursively lint sub-blocks
                if stmt.get("then_body"): self._lint_block(stmt["then_body"], context + " -> if-then")
                if stmt.get("else_body"): self._lint_block(stmt["else_body"], context + " -> if-else")
                if stmt.get("body"): self._lint_block(stmt["body"], context + f" -> {stmt.get('type')}-body")

            elif isinstance(stmt, str) and "=" in stmt:
                # Handle simple assignment
                parts = stmt.split('=', 1)
                var_name = parts[0].strip()
                value_str = parts[1].strip()
                self._check_assignment(var_name, value_str, local_symbols, context)

    def _check_assignment(self, var_name, value_str, local_symbols, context):
        """Checks the type correctness of an assignment."""
        # Find the variable's declared type
        var_type = local_symbols.get(var_name) or self.symbol_table.get(var_name)
        if not var_type:
            self.warnings.append(f"{context}: Assignment to undeclared variable '{var_name}'.")
            return

        # Basic check for value type
        if value_str.startswith('"') and var_type != "string":
            self.warnings.append(f"{context}: Potential type mismatch assigning string literal to '{var_type}' variable '{var_name}'.")
        elif value_str.isdigit() and var_type not in ["integer", "float"]:
             self.warnings.append(f"{context}: Potential type mismatch assigning integer literal to '{var_type}' variable '{var_name}'.")
        # A real linter would use the expression parser here for a much deeper check

if __name__ == "__main__":
    try:
        with open("type_system_test.lsl", "r") as f:
            lsl_code = f.read()
        
        parser = LSLParser()
        parsed = parser.parse(lsl_code)
        
        linter = LSLLinter(parsed)
        warnings = linter.lint()
        
        print("--- Linter Results ---")
        if warnings:
            for warning in warnings:
                print(f"Warning: {warning}")
        else:
            print("No warnings found.")

    except FileNotFoundError:
        print("Error: type_system_test.lsl not found.")
