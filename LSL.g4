grammar LSL;

// ==== PARSER RULES ====

// Root rule
script: (globalDeclaration | functionDefinition | stateDefinition)*;

// Global declarations
globalDeclaration: lslType IDENTIFIER ('=' expression)? ';';

// Function definitions (ENHANCED)
functionDefinition: returnType? IDENTIFIER '(' parameterList? ')' '{' statement* '}';
returnType: lslType | 'void';
parameterList: parameter (',' parameter)*;
parameter: lslType IDENTIFIER ('=' expression)?;  // Default parameters

// State definitions
stateDefinition: ('default' | 'state' IDENTIFIER) '{' eventHandler* '}';
eventHandler: eventName '(' parameterList? ')' '{' statement* '}';

// Event names
eventName: 'state_entry' | 'state_exit' | 'touch_start' | 'touch' | 'touch_end'
         | 'collision_start' | 'collision' | 'collision_end'
         | 'timer' | 'listen' | 'sensor' | 'no_sensor'
         | 'control' | 'at_target' | 'not_at_target' | 'at_rot_target' | 'not_at_rot_target'
         | 'money' | 'email' | 'run_time_permissions' | 'changed'
         | 'attach' | 'dataserver' | 'moving_start' | 'moving_end'
         | 'object_rez' | 'remote_data' | 'http_response' | 'link_message';

// Statements (ENHANCED)
statement: variableDeclaration
         | assignmentStatement
         | expressionStatement
         | ifStatement
         | whileStatement
         | doWhileStatement
         | forStatement
         | returnStatement
         | stateChangeStatement
         | jumpStatement
         | labelStatement
         | compoundStatement
         | breakStatement
         | continueStatement;

// Additional control flow
breakStatement: 'break' ';';
continueStatement: 'continue' ';';

variableDeclaration: lslType IDENTIFIER ('=' expression)? ';';
assignmentStatement: lvalue assignmentOperator expression ';';
expressionStatement: expression ';';
ifStatement: 'if' '(' expression ')' statement ('else' 'if' '(' expression ')' statement)* ('else' statement)?;
whileStatement: 'while' '(' expression ')' statement;
doWhileStatement: 'do' statement 'while' '(' expression ')' ';';
forStatement: 'for' '(' (variableDeclaration | assignmentStatement | ';') expression? ';' expression? ')' statement;
returnStatement: 'return' expression? ';';
stateChangeStatement: 'state' IDENTIFIER ';';
jumpStatement: 'jump' IDENTIFIER ';';
labelStatement: '@' IDENTIFIER ';';
compoundStatement: '{' statement* '}';

// L-values (ENHANCED)
lvalue: IDENTIFIER
      | IDENTIFIER '.' IDENTIFIER        // vector.x, rotation.s
      | IDENTIFIER '[' expression ']'    // list[index]
      | IDENTIFIER '[' expression ':' expression ']';  // list[start:end] slicing

// Assignment operators
assignmentOperator: '=' | '+=' | '-=' | '*=' | '/=' | '%=';

// Expressions with precedence
expression: assignmentExpression;

assignmentExpression: conditionalExpression (assignmentOperator conditionalExpression)*;
conditionalExpression: logicalOrExpression;
logicalOrExpression: logicalAndExpression ('||' logicalAndExpression)*;
logicalAndExpression: bitwiseOrExpression ('&&' bitwiseOrExpression)*;
bitwiseOrExpression: bitwiseXorExpression ('|' bitwiseXorExpression)*;
bitwiseXorExpression: bitwiseAndExpression ('^' bitwiseAndExpression)*;
bitwiseAndExpression: equalityExpression ('&' equalityExpression)*;
equalityExpression: relationalExpression (('==' | '!=') relationalExpression)*;
relationalExpression: shiftExpression (('<' | '>' | '<=' | '>=') shiftExpression)*;
shiftExpression: additiveExpression (('<<' | '>>') additiveExpression)*;
additiveExpression: multiplicativeExpression (('+' | '-') multiplicativeExpression)*;
multiplicativeExpression: unaryExpression (('*' | '/' | '%') unaryExpression)*;

unaryExpression: ('!' | '~' | '-' | '+')? postfixExpression;
postfixExpression: primaryExpression postfixOperator*;
postfixOperator: '++' | '--' | '.' IDENTIFIER | '[' expression ']' | '(' argumentList? ')';

primaryExpression: IDENTIFIER
                 | literal
                 | '(' expression ')'
                 | '(' lslType ')' expression  // type casting
                 | functionCall
                 | vectorLiteral
                 | rotationLiteral
                 | listLiteral;

functionCall: IDENTIFIER '(' argumentList? ')';
argumentList: expression (',' expression)*;

// Literals
literal: INTEGER
       | FLOAT
       | STRING
       | KEY
       | TRUE
       | FALSE
       | NULL_KEY
       | vectorLiteral
       | rotationLiteral
       | listLiteral;

// Enhanced literals
vectorLiteral: '<' expression ',' expression ',' expression '>';
rotationLiteral: '<' expression ',' expression ',' expression ',' expression '>';
listLiteral: '[' (listElement (',' listElement)*)? ']';
listElement: expression | listLiteral;  // Nested lists

// Types
lslType: 'integer' | 'float' | 'string' | 'key' | 'vector' | 'rotation' | 'list';

// ==== LEXER RULES ====

// Keywords (ENHANCED)
INTEGER_TYPE: 'integer';
FLOAT_TYPE: 'float';
STRING_TYPE: 'string';
KEY_TYPE: 'key';
VECTOR_TYPE: 'vector';
ROTATION_TYPE: 'rotation';
LIST_TYPE: 'list';
VOID_TYPE: 'void';
DEFAULT: 'default';
STATE: 'state';
IF: 'if';
ELSE: 'else';
WHILE: 'while';
DO: 'do';
FOR: 'for';
RETURN: 'return';
JUMP: 'jump';
BREAK: 'break';
CONTINUE: 'continue';
TRUE: 'TRUE';
FALSE: 'FALSE';
NULL_KEY: 'NULL_KEY';

// Operators
ASSIGN: '=';
PLUS_ASSIGN: '+=';
MINUS_ASSIGN: '-=';
MULT_ASSIGN: '*=';
DIV_ASSIGN: '/=';
MOD_ASSIGN: '%=';
LOGICAL_OR: '||';
LOGICAL_AND: '&&';
BITWISE_OR: '|';
BITWISE_XOR: '^';
BITWISE_AND: '&';
EQUALITY: '==' | '!=';
RELATIONAL: '<' | '>' | '<=' | '>=';
SHIFT: '<<' | '>>';
PLUS: '+';
MINUS: '-';
MULTIPLY: '*';
DIVIDE: '/';
MODULO: '%';
LOGICAL_NOT: '!';
BITWISE_NOT: '~';
INCREMENT: '++';
DECREMENT: '--';

// Delimiters
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACKET: '[';
RBRACKET: ']';
SEMICOLON: ';';
COMMA: ',';
DOT: '.';
QUESTION: '?';
COLON: ':';
AT: '@';

// Literals
INTEGER: ('0x' | '0X') [0-9a-fA-F]+        // Hexadecimal
       | [0-9]+;                          // Decimal

FLOAT: [0-9]+ '.' [0-9]*                  // 123.45
     | [0-9]* '.' [0-9]+                  // .45 or 0.45
     | [0-9]+ [eE] [+-]? [0-9]+           // Scientific notation
     | [0-9]+ '.' [0-9]* [eE] [+-]? [0-9]+;

STRING: '"' ( ESC_SEQ | ~["\\\r\n] )* '"';
KEY: STRING;  // Keys are UUID strings

// Identifiers
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;

// Escape sequences
fragment ESC_SEQ: '\\' [btnfr"'\\]
                | '\\' [0-3] [0-7] [0-7]
                | '\\' [0-7] [0-7]
                | '\\' [0-7];

// Comments
COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;

// Whitespace
WS: [ \t\r\n]+ -> skip;