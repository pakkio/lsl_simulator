# Generated from LSL.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .LSLParser import LSLParser
else:
    from LSLParser import LSLParser

# This class defines a complete generic visitor for a parse tree produced by LSLParser.

class LSLVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by LSLParser#script.
    def visitScript(self, ctx:LSLParser.ScriptContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#globalDeclaration.
    def visitGlobalDeclaration(self, ctx:LSLParser.GlobalDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#functionDefinition.
    def visitFunctionDefinition(self, ctx:LSLParser.FunctionDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#returnType.
    def visitReturnType(self, ctx:LSLParser.ReturnTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#parameterList.
    def visitParameterList(self, ctx:LSLParser.ParameterListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#parameter.
    def visitParameter(self, ctx:LSLParser.ParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#stateDefinition.
    def visitStateDefinition(self, ctx:LSLParser.StateDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#eventHandler.
    def visitEventHandler(self, ctx:LSLParser.EventHandlerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#eventName.
    def visitEventName(self, ctx:LSLParser.EventNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#statement.
    def visitStatement(self, ctx:LSLParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#breakStatement.
    def visitBreakStatement(self, ctx:LSLParser.BreakStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#continueStatement.
    def visitContinueStatement(self, ctx:LSLParser.ContinueStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#variableDeclaration.
    def visitVariableDeclaration(self, ctx:LSLParser.VariableDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#assignmentStatement.
    def visitAssignmentStatement(self, ctx:LSLParser.AssignmentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#expressionStatement.
    def visitExpressionStatement(self, ctx:LSLParser.ExpressionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#ifStatement.
    def visitIfStatement(self, ctx:LSLParser.IfStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#whileStatement.
    def visitWhileStatement(self, ctx:LSLParser.WhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#doWhileStatement.
    def visitDoWhileStatement(self, ctx:LSLParser.DoWhileStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#forStatement.
    def visitForStatement(self, ctx:LSLParser.ForStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#returnStatement.
    def visitReturnStatement(self, ctx:LSLParser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#stateChangeStatement.
    def visitStateChangeStatement(self, ctx:LSLParser.StateChangeStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#jumpStatement.
    def visitJumpStatement(self, ctx:LSLParser.JumpStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#labelStatement.
    def visitLabelStatement(self, ctx:LSLParser.LabelStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#compoundStatement.
    def visitCompoundStatement(self, ctx:LSLParser.CompoundStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#lvalue.
    def visitLvalue(self, ctx:LSLParser.LvalueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#assignmentOperator.
    def visitAssignmentOperator(self, ctx:LSLParser.AssignmentOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#expression.
    def visitExpression(self, ctx:LSLParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#assignmentExpression.
    def visitAssignmentExpression(self, ctx:LSLParser.AssignmentExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#conditionalExpression.
    def visitConditionalExpression(self, ctx:LSLParser.ConditionalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#logicalOrExpression.
    def visitLogicalOrExpression(self, ctx:LSLParser.LogicalOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#logicalAndExpression.
    def visitLogicalAndExpression(self, ctx:LSLParser.LogicalAndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#bitwiseOrExpression.
    def visitBitwiseOrExpression(self, ctx:LSLParser.BitwiseOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#bitwiseXorExpression.
    def visitBitwiseXorExpression(self, ctx:LSLParser.BitwiseXorExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#bitwiseAndExpression.
    def visitBitwiseAndExpression(self, ctx:LSLParser.BitwiseAndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#equalityExpression.
    def visitEqualityExpression(self, ctx:LSLParser.EqualityExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#relationalExpression.
    def visitRelationalExpression(self, ctx:LSLParser.RelationalExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#shiftExpression.
    def visitShiftExpression(self, ctx:LSLParser.ShiftExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#additiveExpression.
    def visitAdditiveExpression(self, ctx:LSLParser.AdditiveExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:LSLParser.MultiplicativeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#unaryExpression.
    def visitUnaryExpression(self, ctx:LSLParser.UnaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#postfixExpression.
    def visitPostfixExpression(self, ctx:LSLParser.PostfixExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#postfixOperator.
    def visitPostfixOperator(self, ctx:LSLParser.PostfixOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#primaryExpression.
    def visitPrimaryExpression(self, ctx:LSLParser.PrimaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#functionCall.
    def visitFunctionCall(self, ctx:LSLParser.FunctionCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#argumentList.
    def visitArgumentList(self, ctx:LSLParser.ArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#literal.
    def visitLiteral(self, ctx:LSLParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#vectorLiteral.
    def visitVectorLiteral(self, ctx:LSLParser.VectorLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#rotationLiteral.
    def visitRotationLiteral(self, ctx:LSLParser.RotationLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#listLiteral.
    def visitListLiteral(self, ctx:LSLParser.ListLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#listElement.
    def visitListElement(self, ctx:LSLParser.ListElementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by LSLParser#lslType.
    def visitLslType(self, ctx:LSLParser.LslTypeContext):
        return self.visitChildren(ctx)



del LSLParser