# LSL Simulator

A production-ready Python implementation for parsing and simulating LSL (Linden Scripting Language) scripts. Built with unified ANTLR4 architecture and comprehensive API coverage.

## Features

- **Unified ANTLR4 Parser**: Single parsing system for all LSL syntax
- **Comprehensive API**: 270+ LSL functions with extensive coverage
- **Expression Evaluation**: Simple, fast evaluation without over-engineering
- **Interactive Debugger**: Step-by-step debugging with breakpoints
- **Thread-Safe**: Concurrent operation support
- **Modern Architecture**: Clean, maintainable codebase

## Installation & Setup

This project uses **Poetry** for dependency management.

```bash
git clone https://github.com/pakkio/lsl_simulator.git
cd lsl_simulator
poetry install
```

## Usage

### Run LSL Scripts
```bash
poetry run python lsl.py script.lsl
```

### Debug LSL Scripts  
```bash
poetry run python lsl_debugger.py script.lsl
```

### Run Tests
```bash
poetry run python -m pytest
```

### Example Script
```lsl
default {
    state_entry() {
        llSay(0, "Hello, World!");
        llSetTimerEvent(1.0);
    }
    
    timer() {
        llSay(0, "Timer event fired!");
    }
    
    touch_start(integer total_number) {
        llSay(0, "Touched by " + (string)total_number + " avatars");
    }
}
```

## Architecture

### Core Components
- **Parser** (`lsl_antlr_parser.py`): ANTLR4-based LSL parser
- **Simulator** (`lsl_simulator.py`): Main execution engine  
- **Expression Evaluator** (`simple_expression_evaluator.py`): ANTLR4-based expression evaluation
- **API Libraries**: Comprehensive LSL function implementations
- **Debugger** (`lsl_debugger.py`): Interactive debugging interface

### Design Principles
- **ANTLR4 Unified Parsing**: Single parser for all LSL syntax (no pyparsing, no complex regex)
- **Simple Expression Evaluation**: Direct evaluation without over-engineering
- **Poetry Dependency Management**: No pip, requirements.txt, or manual dependency handling
- **Clean Architecture**: No legacy dependencies or hybrid parsing approaches

## Supported LSL Features

### Core Language
- Variables, functions, states, events
- All LSL data types (integer, float, string, key, vector, rotation, list)
- Control flow (if/else, for, while, do-while)
- Expressions with proper operator precedence

### LSL Functions (270+)
- **Communication**: `llSay`, `llListen`, `llRegionSay`, `llDialog`
- **String Operations**: `llStringLength`, `llGetSubString`, `llStringTrim`
- **Math Functions**: `llVecMag`, `llVecNorm`, `llRot2Euler`, `llAbs`
- **List Operations**: `llGetListLength`, `llListSort`, `llList2String`
- **HTTP Requests**: `llHTTPRequest` with async response handling
- **Timers**: `llSetTimerEvent` with periodic callbacks
- **Sensors**: `llSensor`, `llSensorRepeat` with detection events
- **Object Properties**: Position, rotation, scale, color, texture

## Project Structure

```
lsl_simulator/
├── README.md                      # This file (single source of truth)
├── CLAUDE.md                      # Guidelines for Claude developers
├── pyproject.toml                 # Poetry configuration
├── LSL.g4                         # ANTLR4 grammar definition
├── lsl.py                         # Main entry point
├── lsl_antlr_parser.py           # ANTLR4 parser implementation
├── lsl_simulator.py              # Main simulator engine
├── simple_expression_evaluator.py # Expression evaluation
├── lsl_debugger.py               # Interactive debugger
├── comprehensive_lsl_api*.py     # LSL function implementations
├── tests/                        # Test suite
└── *.lsl                         # Example scripts
```

## Development Guidelines

### Dependencies
- **Use Poetry exclusively**: `poetry add package-name`, `poetry run python script.py`
- **Never use pip directly** in this project

### Parsing
- **ANTLR4 only**: All parsing must use the unified ANTLR4 system
- **No pyparsing**: Removed from project (causes architectural inconsistency)
- **No complex regex parsing**: Use ANTLR4 grammar rules instead
- **No manual string parsing**: Extend LSL.g4 grammar for new syntax

### Adding New Features
1. Check ANTLR4 grammar first (`LSL.g4`)
2. Extend grammar if needed
3. Use `SimpleExpressionEvaluator` for expressions
4. Test with existing test suite
5. Follow Poetry workflow

## Testing

```bash
# Run all tests
poetry run python -m pytest

# Run specific test categories  
poetry run python -m pytest tests/test_expressions.py  # Expression evaluation
poetry run python -m pytest tests/test_lsl_functions.py # LSL function tests
```

## Contributing

1. Ensure Poetry is installed
2. Clone and run `poetry install`
3. Follow the unified ANTLR4 architecture
4. Add tests for new functionality
5. Ensure all tests pass with `poetry run python -m pytest`
6. Submit a pull request

## License

Open source project for the OpenSimulator and Second Life communities.