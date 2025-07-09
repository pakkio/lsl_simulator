# Experimental LSL Components

This directory contains experimental and legacy LSL simulator components that are not part of the main production codebase.

## Files

- **lsl_antlr_parser.py** - ANTLR4-based parser implementation (experimental)
- **lsl_core_engine.py** - Core execution engine with separated concerns
- **lsl_simple_evaluator.py** - Simplified expression evaluator using visitor pattern
- **lsl_simulator_new.py** - Modern simulator with separated concerns

## Purpose

These files represent experimental approaches to implementing LSL parsing and simulation:

1. **ANTLR4 Parser**: A more formal parser implementation using ANTLR4 principles
2. **Separated Architecture**: Modular design with separated concerns for parsing, evaluation, and simulation
3. **Visitor Pattern**: Clean expression evaluation using visitor pattern

## Status

These components are used in test files (`test_lsl_components.py`) for validation and experimentation, but are not part of the production codebase.

## Production Files

The main production codebase uses:
- `lsl_parser.py` + `lsl_simulator.py` for main functionality
- `lsl_production_parser.py` + `lsl_simulator_simplified.py` for test infrastructure