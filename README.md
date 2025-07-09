# LSL Simulator

A comprehensive Python-based toolkit for parsing, simulating, and debugging LSL (Linden Scripting Language) scripts locally. Test and develop LSL code without needing to be in-world.

## Features

### Core Functionality
- **Interactive Simulator**: Run LSL scripts with real-time event simulation
- **Step-by-Step Debugger**: Command-line debugger with breakpoints and variable inspection
- **Comprehensive Parser**: Handles states, events, functions, and all LSL constructs
- **Expression Evaluation**: Complex mathematical and boolean expressions with proper precedence
- **Type System**: Full support for LSL data types (string, integer, float, vector, rotation, list, key)

### LSL Language Support
- **Control Flow**: if/else, while, for loops, jump statements
- **Functions**: User-defined functions with parameters and return values  
- **States**: State machine with entry/exit events
- **Events**: Asynchronous event handling (timer, HTTP, touch, listen)
- **Operators**: All LSL operators including vector/rotation math
- **Literals**: Vector `<x,y,z>`, rotation `<x,y,z,s>`, and list `[a,b,c]` syntax

### API Implementation
- **Communication**: `llSay`, `llShout`, `llWhisper`, `llListen`, `llRegionSay`
- **String Functions**: `llStringLength`, `llGetSubString`, `llStringTrim`, `llSubStringIndex`
- **List Operations**: `llGetListLength`, `llListSort`, `llList2String`, `llDumpList2String`
- **Math Functions**: `llVecMag`, `llVecNorm`, `llRot2Euler`, `llEuler2Rot`
- **HTTP Requests**: `llHTTPRequest` with async response handling
- **Timers**: `llSetTimerEvent` with periodic callbacks
- **File I/O**: `llGetNotecardLine`, `llGetInventoryType` with dataserver events
- **JSON**: `llList2Json`, `llJson2List` for data serialization

### Advanced Features
- **OpenSimulator Compatibility**: OSSL function support for extended capabilities
- **NPC Simulation**: Complete NPC system with AI integration example
- **Async Processing**: Thread-based event simulation for realistic behavior
- **Error Handling**: Comprehensive error reporting and recovery

## Installation

### Prerequisites
- Python 3.12 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Setup
```bash
git clone https://github.com/pakkio/lsl_simulator.git
cd lsl_simulator
poetry install
```

## Usage

### Interactive Simulator
Run LSL scripts with event simulation:
```bash
poetry run python lsl.py script.lsl
```

**Interactive Commands:**
- `touch` - Trigger touch_start event
- `say <channel> <message>` - Send chat message
- `sense` - Trigger sensor event
- `help` - Show available commands  
- `quit` - Exit simulator

### Debugger
Step through scripts line by line:
```bash
poetry run python lsl_debugger.py script.lsl
```

**Debugger Commands:**
- `n` - Next line
- `c` - Continue execution
- `b <line>` - Set breakpoint
- `l` - List source code
- `p [locals|globals]` - Print variables
- `q` - Quit debugger

## Architecture

### Core Components
- **Parser**: Regex-based parser for LSL syntax
- **Simulator**: Execution engine with call stack and variable scoping
- **Expression Evaluator**: Pyparsing-based expression processing
- **API Layer**: Comprehensive LSL function implementations
- **Event System**: Async event queue for timers, HTTP, and user events

### Alternative Implementations
- **Simplified Simulator**: `lsl_simulator_simplified.py` - Lightweight version
- **Core Engine**: `lsl_core_engine.py` - Modular execution engine
- **Production Parser**: `lsl_production_parser.py` - ANTLR4-style parser
- **Simple Evaluator**: `lsl_simple_evaluator.py` - Fast expression evaluation

## Examples

### Basic Script
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

### NPC Integration
The simulator includes a complete NPC system demonstration:

1. **Start the mock AI server**:
```bash
poetry run python mock_nexus_server.py
```

2. **Run the NPC script**:
```bash
poetry run python lsl.py npc.lsl
```

The NPC will register with the AI server, detect nearby avatars, and respond to conversation contextually.

## Testing

### Test Suite
```bash
poetry run python run_tests.py
```

### Coverage Report
```bash
poetry run python run_tests.py --coverage
```

### Performance Tests
```bash
poetry run python run_tests.py --performance
```

## Project Structure

```
lsl_simulator/
├── lsl.py                      # Main simulator entry point
├── lsl_debugger.py            # Interactive debugger
├── lsl_simulator.py           # Core simulation engine
├── lsl_parser.py              # LSL syntax parser
├── expression_parser.py       # Expression evaluation
├── comprehensive_lsl_api.py   # LSL API functions
├── lsl_ossl_compatibility.py  # OpenSimulator functions
├── mock_nexus_server.py       # AI server example
├── tests/                     # Test suite
└── *.lsl                      # Example LSL scripts
```

## Configuration

### Environment Variables
- `LSL_DEBUG=1` - Enable debug output
- `LSL_TIMEOUT=30` - HTTP request timeout
- `LSL_MAX_EVENTS=100` - Event queue size

### Parser Options
Multiple parser implementations available:
- Default: Regex-based parser (fast, simple)
- Production: ANTLR4-style parser (comprehensive)
- Simplified: Minimal parser (lightweight)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is open source. See the LICENSE file for details.

## Acknowledgments

Built for the OpenSimulator and Second Life communities to enable local LSL development and testing.