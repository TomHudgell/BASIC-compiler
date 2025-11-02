import sys
from lex import *

# parser object keeps track of current token and checks if code matches the grammar
class Parser:
    def __init__(self, lexer, emitter):
        self.lexer = lexer
        self.emitter = emitter

        self.symbols = set()  # variables declared so far
        self.labelsDeclared = set()  # labels declared so far
        self.labelsGotoed = set()  # labels goto'ed so far

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()  # call twice to initialise current and peek

    # return true if the current token matches
    def checkToken(self, kind):
        return kind == self.curToken.kind

    # return true if the next token matches
    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    # try to match current token. if not, error. advances the current token
    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    # advances the current token
    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        # no need to pass EOF, lexer handles that

    def abort(self, message):
        sys.exit("Error. " + message)

    # production rules

    # program ::= {statement}
    def program(self):
        self.emitter.headerLine("#include <stdio.h>")
        self.emitter.headerLine("int main(void){")

        # since some newlines are required in our grammar, need to skip the excess
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # parse all the statements in the program
        while not self.checkToken(TokenType.EOF):
            self.statement()

        # wrap things up
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")

        # check that each label referenced in a goto is declared
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO undeclared label: " + label)

    def statement(self):
        # check the first token to see what kind of statement this is

        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # simple string, so print it
                self.emitter.emitLine("printf(\"" + self.curToken.text + "\\n\");")
                self.nextToken()
            else:
                # expect an expression and print the result as a float
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression()
                self.emitter.emitLine("));")
        
        # "IF" comparison "THEN" {statement} "ENDIF"
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")

            # zero or more statements in the body
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")

        # "WHILE" comparison "REPEAT" {statement} "ENDWHILE"
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")

            # zero or more statements in the body
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")

        # "LABEL" ident
        elif self.checkToken(TokenType.LABEL):
            self.nextToken()

            # make sure this label doesn't already exist
            if self.curToken.text in self.labelsDeclared:
                self.abort("Label already exists: " + self.curToken.text)
            self.labelsDeclared.add(self.curToken.text)

            self.emitter.emitLine(self.curToken.text + ":")
            self.match(TokenType.IDENT)

        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            self.nextToken()
            self.labelsGotoed.add(self.curToken.text)
            self.emitter.emitLine("goto " + self.curToken.text + ";")
            self.match(TokenType.IDENT)

        # "LET" ident "=" expression
        elif self.checkToken(TokenType.LET):
            self.nextToken()

            # check if ident exists in symbol table. if not, declare it
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            self.emitter.emit(self.curToken.text + " = ")
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
            self.emitter.emitLine(";")

        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()

            # if variable doesn't already exist, declare it
            if self.curToken.text not in self.symbols:
                self.symbols.add(self.curToken.text)
                self.emitter.headerLine("float " + self.curToken.text + ";")

            # emit scanf and validate the input. if invalid, set the variable to 0 and clear the input
            self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.curToken.text + ")) {")
            self.emitter.emitLine(self.curToken.text + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.match(TokenType.IDENT)

        else:  # this is not a valid statement
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")
        
        self.nl()  # newline

    # return true if the current token is a comparison operator
    def isComparisonOperator(self):
        return self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ) or self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ)

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        self.expression()
        # must be at least one comparison operator and another expression
        if self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.curToken.text)

        # can have 0 or more comparison operators and expressions
        while self.isComparisonOperator():
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        self.term()
        # can have 0 or more -/+ and expressions
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        self.unary()
        # can have 0 or more *// and unaries
        while self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.ASTERISK):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.unary()

    # unary ::= [ "+" | "-" ] primary
    def unary(self):
        # optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        self.primary()

    # primary ::= number | ident | (expression)
    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # ensure the variable exists
            if self.curToken.text not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.curToken.text)

            self.emitter.emit(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.OB):
            self.emitter.emit(self.curToken.text)
            self.nextToken()
            self.expression()
            self.emitter.emit(self.curToken.text)
            self.match(TokenType.CB)
        else:
            self.abort("Unexpected token at: " + self.curToken.text)

    # nl ::= '\n'+
    def nl(self):
        # require at least one newline
        self.match(TokenType.NEWLINE)
        # and allow extra newlines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
    
