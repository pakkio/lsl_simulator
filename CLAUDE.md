# LSL Simulator - Development Guidelines

## Project Management

### Dependency Management
- **Use Poetry exclusively** for dependency management
- Run all Python commands through Poetry: `poetry run python script.py`
- Install new dependencies with: `poetry add package-name`
- Never use pip directly in this project

### Development Commands
```bash
# Run tests
poetry run python -m pytest

# Run debugger
poetry run python lsl_debugger.py script.lsl

# Run simulator
poetry run python lsl_simulator.py
```

## Parsing Architecture

### ⚠️ CRITICAL: Unified ANTLR4 Parsing Only

**DO NOT use any of the following for parsing:**
- ❌ **pyparsing** - Removed from project, causes architectural inconsistency
- ❌ **Complex regex parsing** - Leads to brittle, unmaintainable code
- ❌ **String manipulation parsing** - Error-prone and limited
- ❌ **Manual tokenization** - Reinventing the wheel poorly

**ALWAYS use ANTLR4 for ALL parsing needs:**
- ✅ **ANTLR4 grammar** (`LSL.g4`) handles ALL LSL syntax
- ✅ **LSLParser** class for script parsing
- ✅ **SimpleExpressionEvaluator** for expression evaluation
- ✅ **Unified parsing paradigm** - one parser, one source of truth

### Parsing Guidelines

1. **Expression Parsing**: Use `SimpleExpressionEvaluator` which leverages ANTLR4's existing expression rules
2. **Statement Parsing**: Use ANTLR4's statement parsing rules directly
3. **New Syntax**: Add to `LSL.g4` grammar file, never implement custom parsers
4. **Debugging**: All parsing errors should come from ANTLR4, making them consistent and predictable

### Architecture Principles

- **Simplicity over complexity** - LSL syntax is limited, parser should be simple
- **Single source of truth** - ANTLR4 grammar defines all syntax
- **No hybrid approaches** - Don't mix parsing technologies
- **Maintainability** - One parser system to debug and maintain

## Historical Context

This project was unified from a hybrid pyparsing/ANTLR4 system to pure ANTLR4. The old approach caused:
- Parsing inconsistencies between systems  
- Duplicate functionality
- Maintenance overhead
- Architectural complexity

The unified approach provides:
- Consistent parsing behavior
- Single grammar definition
- Simplified debugging
- Reduced dependencies

## When Adding New Features

1. **Check ANTLR4 grammar first** - Most LSL constructs are already defined
2. **Extend grammar if needed** - Add new rules to `LSL.g4`
3. **Use SimpleExpressionEvaluator** - For expression evaluation needs
4. **Test with existing test suite** - Ensure no regressions

Remember: **ANTLR4 unified parsing is a core architectural decision** - maintain it!