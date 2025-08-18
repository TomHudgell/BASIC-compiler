import sys
from lex import *

# parser object keeps track of current token and checks if code matches the grammar
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

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
        print("PROGRAM")

        # since some newlines are required in our grammar, need to skip the excess
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # parse all the statements in the program
        while not self.checkToken(TokenType.EOF):
            self.statement()

    def statement(self):
        # check the first token to see what kind of statement this is

        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # simple string
                self.nextToken()
            else:
                # expect an expression
                self.expression()
        
        # "IF" comparison "THEN" {statement} "ENDIF"
        elif self.checkToken(TokenType.IF):
            print("STATEMENT-IF")
            self.nextToken()
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()

            # zero or more statements in the body
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)

        # "WHILE" comparison "REPEAT" {statement} "ENDWHILE"
        elif self.checkToken(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.nextToken()
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()

            # zero or more statements in the body
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)

        # "LABEL" ident
        elif self.checkToken(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.nextToken()
            self.match(TokenType.IDENT)

        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.nextToken()
            self.match(TokenType.IDENT)

        # "LET" ident "=" expression
        elif self.checkToken(TokenType.LET):
            print("STATEMENT-LET")
            self.nextToken()
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.expression()

        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.nextToken()
            self.match(TokenType.IDENT)

        else:  # this is not a valid statement
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")
        
        self.nl()  # newline

    # return true if the current token is a comparison operator
    def isComparisonOperator(self):
        return self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ) or self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ)

    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self):
        print("COMPARISON")

        self.expression()
        # must be at least one comparison operator and another expression
        if self.isComparisonOperator():
            self.nextToken()
            self.expression()
        else:
            self.abort("Expected comparison operator at: " + self.curToken.text)

        # can have 0 or more comparison operators and expressions
        while self.isComparisonOperator():
            self.nextToken()
            self.expression()

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        print("EXPRESSION")

        self.term()
        # can have 0 or more -/+ and expressions
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
            self.term()

    # term ::= unary {( "/" | "*" ) unary}
    def term(self):
        print("TERM")

        self.unary()
        # can have 0 or more *// and unaries
        while self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.ASTERISK):
            self.nextToken()
            self.unary()

    # unary ::= [ "+" | "-" ] primary
    def unary(self):
        print("UNARY")

        # optional unary +/-
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.nextToken()
        self.primary()

    # primary ::= number | ident
    def primary(self):
        print("PRIMARY (" + self.curToken.text + ")")

        if self.checkToken(TokenType.NUMBER) or self.checkToken(TokenType.IDENT):
            self.nextToken()
        else:
            self.abort("Unexpected token at: " + self.curToken.text)

    # nl ::= '\n'+
    def nl(self):
        print("NEWLINE")

        # require at least one newline
        self.match(TokenType.NEWLINE)
        # and allow extra newlines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
    
