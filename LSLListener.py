# Generated from LSL.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .LSLParser import LSLParser
else:
    from LSLParser import LSLParser

# This class defines a complete listener for a parse tree produced by LSLParser.
class LSLListener(ParseTreeListener):

    # Enter a parse tree produced by LSLParser#script.
    def enterScript(self, ctx:LSLParser.ScriptContext):
        pass

    # Exit a parse tree produced by LSLParser#script.
    def exitScript(self, ctx:LSLParser.ScriptContext):
        pass


    # Enter a parse tree produced by LSLParser#globalDeclaration.
    def enterGlobalDeclaration(self, ctx:LSLParser.GlobalDeclarationContext):
        pass

    # Exit a parse tree produced by LSLParser#globalDeclaration.
    def exitGlobalDeclaration(self, ctx:LSLParser.GlobalDeclarationContext):
        pass


    # Enter a parse tree produced by LSLParser#functionDefinition.
    def enterFunctionDefinition(self, ctx:LSLParser.FunctionDefinitionContext):
        pass

    # Exit a parse tree produced by LSLParser#functionDefinition.
    def exitFunctionDefinition(self, ctx:LSLParser.FunctionDefinitionContext):
        pass


    # Enter a parse tree produced by LSLParser#returnType.
    def enterReturnType(self, ctx:LSLParser.ReturnTypeContext):
        pass

    # Exit a parse tree produced by LSLParser#returnType.
    def exitReturnType(self, ctx:LSLParser.ReturnTypeContext):
        pass


    # Enter a parse tree produced by LSLParser#parameterList.
    def enterParameterList(self, ctx:LSLParser.ParameterListContext):
        pass

    # Exit a parse tree produced by LSLParser#parameterList.
    def exitParameterList(self, ctx:LSLParser.ParameterListContext):
        pass


    # Enter a parse tree produced by LSLParser#parameter.
    def enterParameter(self, ctx:LSLParser.ParameterContext):
        pass

    # Exit a parse tree produced by LSLParser#parameter.
    def exitParameter(self, ctx:LSLParser.ParameterContext):
        pass


    # Enter a parse tree produced by LSLParser#stateDefinition.
    def enterStateDefinition(self, ctx:LSLParser.StateDefinitionContext):
        pass

    # Exit a parse tree produced by LSLParser#stateDefinition.
    def exitStateDefinition(self, ctx:LSLParser.StateDefinitionContext):
        pass


    # Enter a parse tree produced by LSLParser#eventHandler.
    def enterEventHandler(self, ctx:LSLParser.EventHandlerContext):
        pass

    # Exit a parse tree produced by LSLParser#eventHandler.
    def exitEventHandler(self, ctx:LSLParser.EventHandlerContext):
        pass


    # Enter a parse tree produced by LSLParser#eventName.
    def enterEventName(self, ctx:LSLParser.EventNameContext):
        pass

    # Exit a parse tree produced by LSLParser#eventName.
    def exitEventName(self, ctx:LSLParser.EventNameContext):
        pass


    # Enter a parse tree produced by LSLParser#statement.
    def enterStatement(self, ctx:LSLParser.StatementContext):
        pass

    # Exit a parse tree produced by LSLParser#statement.
    def exitStatement(self, ctx:LSLParser.StatementContext):
        pass


    # Enter a parse tree produced by LSLParser#breakStatement.
    def enterBreakStatement(self, ctx:LSLParser.BreakStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#breakStatement.
    def exitBreakStatement(self, ctx:LSLParser.BreakStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#continueStatement.
    def enterContinueStatement(self, ctx:LSLParser.ContinueStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#continueStatement.
    def exitContinueStatement(self, ctx:LSLParser.ContinueStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#variableDeclaration.
    def enterVariableDeclaration(self, ctx:LSLParser.VariableDeclarationContext):
        pass

    # Exit a parse tree produced by LSLParser#variableDeclaration.
    def exitVariableDeclaration(self, ctx:LSLParser.VariableDeclarationContext):
        pass


    # Enter a parse tree produced by LSLParser#assignmentStatement.
    def enterAssignmentStatement(self, ctx:LSLParser.AssignmentStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#assignmentStatement.
    def exitAssignmentStatement(self, ctx:LSLParser.AssignmentStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#expressionStatement.
    def enterExpressionStatement(self, ctx:LSLParser.ExpressionStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#expressionStatement.
    def exitExpressionStatement(self, ctx:LSLParser.ExpressionStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#ifStatement.
    def enterIfStatement(self, ctx:LSLParser.IfStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#ifStatement.
    def exitIfStatement(self, ctx:LSLParser.IfStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#whileStatement.
    def enterWhileStatement(self, ctx:LSLParser.WhileStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#whileStatement.
    def exitWhileStatement(self, ctx:LSLParser.WhileStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#doWhileStatement.
    def enterDoWhileStatement(self, ctx:LSLParser.DoWhileStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#doWhileStatement.
    def exitDoWhileStatement(self, ctx:LSLParser.DoWhileStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#forStatement.
    def enterForStatement(self, ctx:LSLParser.ForStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#forStatement.
    def exitForStatement(self, ctx:LSLParser.ForStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#returnStatement.
    def enterReturnStatement(self, ctx:LSLParser.ReturnStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#returnStatement.
    def exitReturnStatement(self, ctx:LSLParser.ReturnStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#stateChangeStatement.
    def enterStateChangeStatement(self, ctx:LSLParser.StateChangeStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#stateChangeStatement.
    def exitStateChangeStatement(self, ctx:LSLParser.StateChangeStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#jumpStatement.
    def enterJumpStatement(self, ctx:LSLParser.JumpStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#jumpStatement.
    def exitJumpStatement(self, ctx:LSLParser.JumpStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#labelStatement.
    def enterLabelStatement(self, ctx:LSLParser.LabelStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#labelStatement.
    def exitLabelStatement(self, ctx:LSLParser.LabelStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#compoundStatement.
    def enterCompoundStatement(self, ctx:LSLParser.CompoundStatementContext):
        pass

    # Exit a parse tree produced by LSLParser#compoundStatement.
    def exitCompoundStatement(self, ctx:LSLParser.CompoundStatementContext):
        pass


    # Enter a parse tree produced by LSLParser#lvalue.
    def enterLvalue(self, ctx:LSLParser.LvalueContext):
        pass

    # Exit a parse tree produced by LSLParser#lvalue.
    def exitLvalue(self, ctx:LSLParser.LvalueContext):
        pass


    # Enter a parse tree produced by LSLParser#assignmentOperator.
    def enterAssignmentOperator(self, ctx:LSLParser.AssignmentOperatorContext):
        pass

    # Exit a parse tree produced by LSLParser#assignmentOperator.
    def exitAssignmentOperator(self, ctx:LSLParser.AssignmentOperatorContext):
        pass


    # Enter a parse tree produced by LSLParser#expression.
    def enterExpression(self, ctx:LSLParser.ExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#expression.
    def exitExpression(self, ctx:LSLParser.ExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#assignmentExpression.
    def enterAssignmentExpression(self, ctx:LSLParser.AssignmentExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#assignmentExpression.
    def exitAssignmentExpression(self, ctx:LSLParser.AssignmentExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#conditionalExpression.
    def enterConditionalExpression(self, ctx:LSLParser.ConditionalExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#conditionalExpression.
    def exitConditionalExpression(self, ctx:LSLParser.ConditionalExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#logicalOrExpression.
    def enterLogicalOrExpression(self, ctx:LSLParser.LogicalOrExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#logicalOrExpression.
    def exitLogicalOrExpression(self, ctx:LSLParser.LogicalOrExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#logicalAndExpression.
    def enterLogicalAndExpression(self, ctx:LSLParser.LogicalAndExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#logicalAndExpression.
    def exitLogicalAndExpression(self, ctx:LSLParser.LogicalAndExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#bitwiseOrExpression.
    def enterBitwiseOrExpression(self, ctx:LSLParser.BitwiseOrExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#bitwiseOrExpression.
    def exitBitwiseOrExpression(self, ctx:LSLParser.BitwiseOrExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#bitwiseXorExpression.
    def enterBitwiseXorExpression(self, ctx:LSLParser.BitwiseXorExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#bitwiseXorExpression.
    def exitBitwiseXorExpression(self, ctx:LSLParser.BitwiseXorExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#bitwiseAndExpression.
    def enterBitwiseAndExpression(self, ctx:LSLParser.BitwiseAndExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#bitwiseAndExpression.
    def exitBitwiseAndExpression(self, ctx:LSLParser.BitwiseAndExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#equalityExpression.
    def enterEqualityExpression(self, ctx:LSLParser.EqualityExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#equalityExpression.
    def exitEqualityExpression(self, ctx:LSLParser.EqualityExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#relationalExpression.
    def enterRelationalExpression(self, ctx:LSLParser.RelationalExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#relationalExpression.
    def exitRelationalExpression(self, ctx:LSLParser.RelationalExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#shiftExpression.
    def enterShiftExpression(self, ctx:LSLParser.ShiftExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#shiftExpression.
    def exitShiftExpression(self, ctx:LSLParser.ShiftExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#additiveExpression.
    def enterAdditiveExpression(self, ctx:LSLParser.AdditiveExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#additiveExpression.
    def exitAdditiveExpression(self, ctx:LSLParser.AdditiveExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#multiplicativeExpression.
    def enterMultiplicativeExpression(self, ctx:LSLParser.MultiplicativeExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#multiplicativeExpression.
    def exitMultiplicativeExpression(self, ctx:LSLParser.MultiplicativeExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#unaryExpression.
    def enterUnaryExpression(self, ctx:LSLParser.UnaryExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#unaryExpression.
    def exitUnaryExpression(self, ctx:LSLParser.UnaryExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#postfixExpression.
    def enterPostfixExpression(self, ctx:LSLParser.PostfixExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#postfixExpression.
    def exitPostfixExpression(self, ctx:LSLParser.PostfixExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#postfixOperator.
    def enterPostfixOperator(self, ctx:LSLParser.PostfixOperatorContext):
        pass

    # Exit a parse tree produced by LSLParser#postfixOperator.
    def exitPostfixOperator(self, ctx:LSLParser.PostfixOperatorContext):
        pass


    # Enter a parse tree produced by LSLParser#primaryExpression.
    def enterPrimaryExpression(self, ctx:LSLParser.PrimaryExpressionContext):
        pass

    # Exit a parse tree produced by LSLParser#primaryExpression.
    def exitPrimaryExpression(self, ctx:LSLParser.PrimaryExpressionContext):
        pass


    # Enter a parse tree produced by LSLParser#functionCall.
    def enterFunctionCall(self, ctx:LSLParser.FunctionCallContext):
        pass

    # Exit a parse tree produced by LSLParser#functionCall.
    def exitFunctionCall(self, ctx:LSLParser.FunctionCallContext):
        pass


    # Enter a parse tree produced by LSLParser#argumentList.
    def enterArgumentList(self, ctx:LSLParser.ArgumentListContext):
        pass

    # Exit a parse tree produced by LSLParser#argumentList.
    def exitArgumentList(self, ctx:LSLParser.ArgumentListContext):
        pass


    # Enter a parse tree produced by LSLParser#literal.
    def enterLiteral(self, ctx:LSLParser.LiteralContext):
        pass

    # Exit a parse tree produced by LSLParser#literal.
    def exitLiteral(self, ctx:LSLParser.LiteralContext):
        pass


    # Enter a parse tree produced by LSLParser#vectorLiteral.
    def enterVectorLiteral(self, ctx:LSLParser.VectorLiteralContext):
        pass

    # Exit a parse tree produced by LSLParser#vectorLiteral.
    def exitVectorLiteral(self, ctx:LSLParser.VectorLiteralContext):
        pass


    # Enter a parse tree produced by LSLParser#rotationLiteral.
    def enterRotationLiteral(self, ctx:LSLParser.RotationLiteralContext):
        pass

    # Exit a parse tree produced by LSLParser#rotationLiteral.
    def exitRotationLiteral(self, ctx:LSLParser.RotationLiteralContext):
        pass


    # Enter a parse tree produced by LSLParser#listLiteral.
    def enterListLiteral(self, ctx:LSLParser.ListLiteralContext):
        pass

    # Exit a parse tree produced by LSLParser#listLiteral.
    def exitListLiteral(self, ctx:LSLParser.ListLiteralContext):
        pass


    # Enter a parse tree produced by LSLParser#listElement.
    def enterListElement(self, ctx:LSLParser.ListElementContext):
        pass

    # Exit a parse tree produced by LSLParser#listElement.
    def exitListElement(self, ctx:LSLParser.ListElementContext):
        pass


    # Enter a parse tree produced by LSLParser#lslType.
    def enterLslType(self, ctx:LSLParser.LslTypeContext):
        pass

    # Exit a parse tree produced by LSLParser#lslType.
    def exitLslType(self, ctx:LSLParser.LslTypeContext):
        pass



del LSLParser