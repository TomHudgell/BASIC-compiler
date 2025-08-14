import enum
import sys

class Lexer:
    def __init__(self, source):
        self.source = source + '\n'  # source code to lex as a string, newline added to simplify processing of last statement
        self.curChar = ''
        self.curPos = -1
        self.nextChar()

    # process the next character
    def nextChar(self):
        self.curPos += 1
        if self.curPos >= len(self.source):
            self.curChar = '\0'  # EOF
        else:
            self.curChar = self.source[self.curPos]

    # return the lookahead character
    def peek(self):
        if self.curPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.curPos + 1]

    # invalid token found, print error message and exit
    def abort(self, message):
        sys.exit("Lexing error. " + message)

    # skip whitespaces except newlines, which we will use to indicate the end of a statement
    def skipWhitespace(self):
        while self.curChar == ' ' or self.curChar == '\t' or self.curChar == '\r':
            self.nextChar()

    # skip comments in the code
    def skipComments(self):
        pass

    # return the next token
    def getToken(self):
        self.skipWhitespace()
        token = None

        # check the first character of this toke to see if we can decide what it is
        # if it is a multiple character token then we will continue processing
        if self.curChar == '+':
            token = Token(self.curChar, TokenType.PLUS)
        elif self.curChar == '-':
            token = Token(self.curChar, TokenType.MINUS)
        elif self.curChar == '*':
            token = Token(self.curChar, TokenType.ASTERISK)
        elif self.curChar == '/':
            token = Token(self.curChar, TokenType.SLASH)
        elif self.curChar == '\n':
            token = Token(self.curChar, TokenType.NEWLINE)
        elif self.curChar == '\0':
            token = Token('', TokenType.EOF)
        else:
            self.abort("Unknown token: " + self.curChar)  # unknown token

        self.nextChar()
        return token


# token contains the original text and the type of token
class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText  # used for identifies, strings, numbers
        self.kind = tokenKind

# enum for all the types of tokens
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3

    # keywords
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111

    # operators
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211