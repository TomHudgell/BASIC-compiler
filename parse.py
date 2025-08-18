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
        
        self.nl()  # newline

    # nl ::= '\n'+
    def nl(self):
        print("NEWLINE")

        # require at least one newline
        self.match(TokenType.NEWLINE)
        # and allow extra newlines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
    
