
import pyparsing as pp
from pyparsing import (
    opAssoc,
    pyparsing_common,
    infixNotation,
    Word,
    alphas,
    alphanums,
    QuotedString,
    oneOf,
    Forward
)

class ExpressionParser:
    def __init__(self):
        # Define the basic elements (operands)
        identifier = Word(alphas + "_", alphanums + "_")
        number = pyparsing_common.number
        string_literal = QuotedString('"')

        operand = Forward()
        
        # Add a rule for LSL-style type casting, e.g., (string)i
        LSL_TYPE = oneOf("integer string key vector rotation list float")
        type_cast = pp.Group(pp.Suppress("(") + LSL_TYPE("type") + pp.Suppress(")") + operand("value"))

        # Define list literals, e.g., [1, "a", "b"]
        list_literal = pp.Group(pp.Suppress("[") + pp.Optional(pp.delimitedList(operand)) + pp.Suppress("]"))

        vector_literal = pp.Group(pp.Suppress("<") + pp.delimitedList(pp.pyparsing_common.number, delim=",", min=3, max=3) + pp.Suppress(">"))
        rotation_literal = pp.Group(pp.Suppress("<") + pp.delimitedList(pp.pyparsing_common.number, delim=",", min=4, max=4) + pp.Suppress(">"))

        # Define function calls, e.g., llSay(0, "hello")
        function_call = pp.Group(identifier("function_name") + pp.Suppress("(") + pp.Optional(pp.delimitedList(operand))("args") + pp.Suppress(")"))

        # An operand can be a number, a variable, a string, a function call, or a type-casted value
        operand <<= type_cast | function_call | number | string_literal | vector_literal | rotation_literal | list_literal | identifier

        # Define the operators and their precedence
        # Precedence is defined from highest to lowest
        self.grammar = infixNotation(
            operand,
            [
                (oneOf("!"), 1, opAssoc.RIGHT),
                (oneOf("* /"), 2, opAssoc.LEFT),
                (oneOf("+ -"), 2, opAssoc.LEFT),
                (oneOf("< > <= >="), 2, opAssoc.LEFT),
                (oneOf("== !="), 2, opAssoc.LEFT),
                (oneOf("&&"), 2, opAssoc.LEFT),
                (oneOf("||"), 2, opAssoc.LEFT),
            ],
        )

    def parse(self, expression_string):
        """
        Parses a mathematical or string expression.
        Returns a pyparsing ParseResults object that represents the expression tree.
        """
        return self.grammar.parseString(expression_string, parseAll=True)[0]

if __name__ == "__main__":
    # --- Test the expression parser ---
    parser = ExpressionParser()
    tests = [
        "5 + 3 * 2",
        "(5 + 3) * 2",
        '"hello" + " " + "world"',
        "i + 1",
        "some_variable",
        '[ "a", 1, "b" ] + [ "c", 3 ]',
        "i > 5 && j < 10",
        "!flag || (x == y)"
    ]
    for test in tests:
        print(f"Parsing: '{test}'")
        result = parser.parse(test)
        print(f"Result: {result}")
        print("-" * 20)
