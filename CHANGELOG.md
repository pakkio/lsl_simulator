# Changelog

All notable changes to the LSL Simulator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-07-09

### Added
- **Comprehensive LSL API**: 270+ functions covering core LSL functionality
  - String manipulation: `llStringLength`, `llGetSubString`, `llStringTrim`, `llSubStringIndex`
  - List operations: `llGetListLength`, `llListSort`, `llList2String`, `llDumpList2String`
  - Vector/rotation math: `llVecMag`, `llVecNorm`, `llRot2Euler`, `llEuler2Rot`
  - Communication: `llSay`, `llShout`, `llWhisper`, `llListen`, `llRegionSay`
  - HTTP requests: `llHTTPRequest` with async response handling
  - Timers: `llSetTimerEvent` with periodic callbacks
  - File I/O: `llGetNotecardLine`, `llGetInventoryType` with dataserver events
  - JSON: `llList2Json`, `llJson2List` for data serialization

- **OpenSimulator Compatibility**: OSSL function support
  - `osSetSpeed`, `osGetRegionStats`, `osMessageObject`
  - `osGetNotecard`, `osSetDynamicTextureURL`, `osConsoleCommand`
  - `osGetSimulatorVersion`, `osGetAvatarList`, `osSetParcelDetails`
  - Multi-mode compatibility (LSL_STRICT, OSSL_EXTENDED, HYBRID)

- **NPC Simulation System**: Complete AI-integrated NPC example
  - `npc.lsl` script for in-world NPC behavior
  - `mock_nexus_server.py` AI backend simulation
  - Avatar detection and contextual conversation
  - Dynamic response generation and action commands

- **Enhanced Architecture**: Multiple implementation options
  - `lsl_simulator_simplified.py` - Lightweight version
  - `lsl_core_engine.py` - Modular execution engine
  - `lsl_production_parser.py` - ANTLR4-style parser
  - `lsl_simple_evaluator.py` - Fast expression evaluation

### Changed
- **Unified Documentation**: Single, comprehensive README
- **Modular Design**: Separated concerns with clear component boundaries
- **Expression System**: Pyparsing-based evaluation with object pooling
- **Event Handling**: Thread-based async event simulation
- **Error Handling**: Comprehensive error reporting and recovery

### Fixed
- **Parser Improvements**: Better handling of complex expressions
- **Variable Scoping**: Proper local/global variable management
- **Control Flow**: Correct execution of loops and conditionals
- **Type System**: Improved type casting and validation
- **Event Queue**: Reliable async event processing

### Removed
- **Legacy Code**: Removed 34 unused files
  - 29 debug scripts from development
  - Old simulator variants
  - Outdated documentation
  - Unused analysis scripts

## [1.0.0] - Previous Release

### Features
- Basic LSL script parsing and execution
- Core LSL API implementation
- Simple debugging capabilities
- HTTP request simulation
- Timer and event handling

## Development Notes

### Current Status
- **Architecture**: Stable multi-implementation design
- **API Coverage**: Comprehensive LSL function support
- **Testing**: Professional test suite with coverage reporting
- **Documentation**: Unified and current with actual implementation

### Future Roadmap
- Enhanced OpenSimulator compatibility
- Performance optimizations
- Additional LSL functions
- Visual debugging tools
- Web interface for script testing

---

## Migration Guide

### From v1.0 to v2.0

#### Updated Dependencies
```bash
poetry install
```

#### Usage Changes
- Main entry point remains `lsl.py`
- Debugger usage unchanged
- New NPC simulation available
- Enhanced API coverage

#### New Features
- OpenSimulator OSSL functions
- NPC AI integration example
- Multiple parser implementations
- Improved error handling

---

## Acknowledgments

Built for the OpenSimulator and Second Life communities to enable local LSL development and testing.