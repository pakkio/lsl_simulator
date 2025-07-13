#!/usr/bin/env python3

"""
Test script to isolate the LSL parser issue with statement parsing
"""

from lsl_antlr_parser import LSLParser

def test_statement_parsing():
    print("=== Testing LSL Statement Parsing Issue ===")
    
    # Simple test case that should work
    simple_code = """
    default {
        state_entry() {
            llSay(0, "Hello World");
        }
    }
    """
    
    parser = LSLParser()
    
    print("Testing simple code:")
    print(simple_code)
    print()
    
    try:
        result = parser.parse(simple_code)
        print("✓ Simple code parsed successfully")
        print(f"States found: {list(result.get('states', {}).keys())}")
        
        # Check the state_entry event
        default_state = result.get('states', {}).get('default', {})
        state_entry = default_state.get('state_entry', {})
        print(f"state_entry body: {state_entry.get('body', [])}")
        
    except Exception as e:
        print(f"✗ Simple code failed: {e}")
        import traceback
        traceback.print_exc()

def test_problematic_lines():
    print("\n=== Testing Individual Problematic Lines ===")
    
    # Test some lines that are causing issues
    problematic_lines = [
        "}",  # Isolated closing brace
        "llSay(0, \"Hello\")",  # Function call without semicolon
        "if (x > 0)",  # If without body
        "else",  # Else without context
    ]
    
    from LSLLexer import LSLLexer
    from LSLParser import LSLParser as GeneratedLSLParser
    from antlr4 import InputStream, CommonTokenStream
    from antlr4.error.ErrorListener import ErrorListener
    
    class CollectingErrorListener(ErrorListener):
        def __init__(self):
            self.errors = []
        
        def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
            self.errors.append(f'line {line}:{column} {msg}')
    
    for line in problematic_lines:
        print(f"\nTesting line: '{line}';")
        try:
            # Try to parse as a statement (like the current implementation does)
            input_stream = InputStream(line + ';')
            lexer = LSLLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = GeneratedLSLParser(token_stream)
            
            error_listener = CollectingErrorListener()
            parser.removeErrorListeners()
            parser.addErrorListener(error_listener)
            
            stmt_tree = parser.statement()
            
            if error_listener.errors:
                print(f"  ✗ Errors: {error_listener.errors}")
            else:
                print(f"  ✓ Parsed successfully")
                
        except Exception as e:
            print(f"  ✗ Exception: {e}")

if __name__ == "__main__":
    test_statement_parsing()
    test_problematic_lines()