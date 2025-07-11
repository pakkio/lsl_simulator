#!/usr/bin/env python3
"""
ANTLR4-based LSL Parser
Clean implementation using generated ANTLR4 parser for proper if/else handling
"""

import sys
from typing import Any, Dict, List, Optional, Union
from antlr4 import InputStream, CommonTokenStream
from LSLLexer import LSLLexer
from LSLParser import LSLParser
from LSLVisitor import LSLVisitor

class LSLASTBuilder(LSLVisitor):
    """Visitor that converts ANTLR4 parse tree to simplified AST for the simulator"""
    
    def __init__(self):
        self.current_line = 1
    
    def visitScript(self, ctx):
        """Visit the root script node"""
        result = {
            "globals": [],
            "functions": {},
            "states": {}
        }
        
        # Process global declarations and functions
        for child in ctx.children:
            if hasattr(child, 'getRuleIndex'):
                if child.getRuleIndex() == LSLParser.RULE_globalDeclaration:
                    global_var = self.visit(child)
                    if global_var:
                        result["globals"].append(global_var)
                elif child.getRuleIndex() == LSLParser.RULE_functionDefinition:
                    func = self.visit(child)
                    if func:
                        result["functions"][func["name"]] = func
                elif child.getRuleIndex() == LSLParser.RULE_stateDefinition:
                    state = self.visit(child)
                    if state:
                        result["states"][state["name"]] = state
        
        return result
    
    def visitGlobalDeclaration(self, ctx):
        """Visit global variable declaration"""
        type_name = ctx.lslType().getText()
        var_name = ctx.IDENTIFIER().getText()
        
        init_value = None
        if ctx.expression():
            init_value = ctx.expression().getText()
        
        return {
            "type": type_name,
            "name": var_name,
            "value": init_value
        }
    
    def visitFunctionDefinition(self, ctx):
        """Visit function definition"""
        # Get function name
        func_name = ctx.IDENTIFIER().getText()
        
        # Get return type (default to void if not specified)
        return_type = "void"
        if ctx.returnType():
            return_type = ctx.returnType().getText()
        
        # Process parameters
        params = []
        if ctx.parameterList():
            for param_ctx in ctx.parameterList().parameter():
                param_type = param_ctx.lslType().getText()
                param_name = param_ctx.IDENTIFIER().getText()
                params.append({
                    "type": param_type,
                    "name": param_name
                })
        
        # Process statements
        statements = []
        for stmt_ctx in ctx.statement():
            stmt = self.visit(stmt_ctx)
            if stmt:
                statements.append(stmt)
        
        return {
            "name": func_name,
            "return_type": return_type,
            "args": params,
            "body": statements
        }
    
    def visitStateDefinition(self, ctx):
        """Visit state definition"""
        # Get state name
        if ctx.getChild(0).getText() == "default":
            state_name = "default"
        else:
            state_name = ctx.IDENTIFIER().getText()
        
        # Process event handlers
        events = {}
        for event_ctx in ctx.eventHandler():
            event = self.visit(event_ctx)
            if event:
                events[event["name"]] = event
        
        # Return the events directly to match simulator expectations
        result = {"name": state_name}
        result.update(events)
        return result
    
    def visitEventHandler(self, ctx):
        """Visit event handler"""
        event_name = ctx.eventName().getText()
        
        # Process parameters
        params = []
        if ctx.parameterList():
            for param_ctx in ctx.parameterList().parameter():
                param_type = param_ctx.lslType().getText()
                param_name = param_ctx.IDENTIFIER().getText()
                params.append({
                    "type": param_type,
                    "name": param_name
                })
        
        # Process statements
        statements = []
        for stmt_ctx in ctx.statement():
            stmt = self.visit(stmt_ctx)
            if stmt:
                statements.append(stmt)
        
        return {
            "name": event_name,
            "args": params,
            "body": statements
        }
    
    def visitIfStatement(self, ctx):
        """Visit if statement - this is the key fix for proper if/else handling"""
        condition = ctx.expression().getText()
        
        # Get then body - flatten compound statements
        then_stmt = self.visit(ctx.statement(0))
        if then_stmt and then_stmt.get("type") == "compound":
            then_body = then_stmt["statements"]
        else:
            then_body = [then_stmt] if then_stmt else []
        
        # Get else body if present - flatten compound statements
        else_body = []
        if len(ctx.statement()) > 1:
            else_stmt = self.visit(ctx.statement(1))
            if else_stmt:
                if else_stmt.get("type") == "compound":
                    else_body = else_stmt["statements"]
                else:
                    else_body = [else_stmt]
        
        return {
            "type": "if",
            "condition": condition,
            "then_body": then_body,
            "else_body": else_body
        }
    
    def visitCompoundStatement(self, ctx):
        """Visit compound statement (block with braces)"""
        statements = []
        for stmt_ctx in ctx.statement():
            stmt = self.visit(stmt_ctx)
            if stmt:
                statements.append(stmt)
        return {
            "type": "compound",
            "statements": statements
        }
    
    def visitExpressionStatement(self, ctx):
        """Visit expression statement"""
        expr_text = ctx.expression().getText()
        return {
            "type": "simple",
            "statement": expr_text
        }
    
    def visitVariableDeclaration(self, ctx):
        """Visit variable declaration"""
        type_name = ctx.lslType().getText()
        var_name = ctx.IDENTIFIER().getText()
        
        init_value = None
        if ctx.expression():
            init_value = ctx.expression().getText()
        
        return {
            "type": "declaration",
            "lsl_type": type_name,
            "name": var_name,
            "value": init_value
        }
    
    def visitAssignmentStatement(self, ctx):
        """Visit assignment statement (including +=, -=, etc.)"""
        lvalue = ctx.lvalue().getText()
        operator = ctx.assignmentOperator().getText()
        expression = ctx.expression().getText()
        
        return {
            "type": "assignment",
            "lvalue": lvalue,
            "operator": operator,
            "expression": expression
        }
    
    def visitReturnStatement(self, ctx):
        """Visit return statement"""
        value = None
        if ctx.expression():
            value = ctx.expression().getText()
        
        return {
            "type": "return",
            "value": value
        }
    
    def visitWhileStatement(self, ctx):
        """Visit while statement"""
        condition = ctx.expression().getText()
        body_stmt = self.visit(ctx.statement())
        body = [body_stmt] if body_stmt else []
        
        return {
            "type": "while",
            "condition": condition,
            "body": body
        }
    
    def visitForStatement(self, ctx):
        """Visit for statement"""
        # Parse the for loop components
        # for (init; condition; increment) statement
        
        # Get initialization (can be variable declaration, assignment, or empty)
        init = None
        if ctx.getChild(2).getText() != ';':  # If not empty
            if ctx.variableDeclaration():
                init = self.visit(ctx.variableDeclaration())
            elif ctx.assignmentStatement():
                init = self.visit(ctx.assignmentStatement())
        
        # Get condition (optional)
        condition = None
        expressions = ctx.expression()
        if len(expressions) > 0:
            condition = expressions[0].getText()
        
        # Get increment (optional)
        increment = None
        if len(expressions) > 1:
            increment = expressions[1].getText()
        
        # Get body statement
        body_stmt = self.visit(ctx.statement())
        body = [body_stmt] if body_stmt else []
        
        return {
            "type": "for",
            "init": init,
            "condition": condition,
            "increment": increment,
            "body": body
        }


class LSLAntlr4Parser:
    """ANTLR4-based LSL Parser"""
    
    def __init__(self):
        pass
    
    def parse(self, code: str) -> Dict[str, Any]:
        """Parse LSL code using ANTLR4 parser"""
        try:
            # Create input stream
            input_stream = InputStream(code)
            
            # Create lexer
            lexer = LSLLexer(input_stream)
            
            # Create token stream
            token_stream = CommonTokenStream(lexer)
            
            # Create parser
            parser = LSLParser(token_stream)
            
            # Parse starting from script rule
            tree = parser.script()
            
            # Build AST using visitor
            ast_builder = LSLASTBuilder()
            result = ast_builder.visit(tree)
            
            return result
            
        except Exception as e:
            print(f"ANTLR4 Parse error: {e}")
            raise