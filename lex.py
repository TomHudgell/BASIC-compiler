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
        if self.curChar == '#':
            while self.curChar != '\n':
                self.nextChar()

    # return the next token
    def getToken(self):
        self.skipWhitespace()
        self.skipComments()
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
        elif self.curChar == '=':
            # check if this is = or ==
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.EQEQ)
            else:
                token = Token(self.curChar, TokenType.EQ)
        elif self.curChar == '>':
            # check if this is > or >=
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.GTEQ)
            else:
                token = Token(self.curChar, TokenType.GT)
        elif self.curChar == '<':
            # check if this is < or <=
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.LTEQ)
            else:
                token = Token(self.curChar, TokenType.LT)
        elif self.curChar == '!':
            if self.peek() == '=':
                lastChar = self.curChar
                self.nextChar()
                token = Token(lastChar + self.curChar, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.curChar == '\"':
            # get characters between quotations
            self.nextChar()
            startPos = self.curPos

            while self.curChar != '\"':
                # don't allow special characters - no escape chars, newlines, tabs, or %
                # will be using C's printf
                if self.curChar == '\r' or self.curChar == '\n' or self.curChar == '\t' or self.curChar == '\\' or self.curChar == '%':
                    self.abort("Illegal character in string.")
                self.nextChar()
            
            tokText = self.source[startPos : self.curPos] # get substring
            token = Token(tokText, TokenType.STRING)
        elif self.curChar.isdigit():
            # leading character is a digit so this must be a number
            # get all consecutive digits and decimal if there is one
            startPos = self.curPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.':  # decimal
                self.nextChar()

                # must have at least one digit after decimal point
                if not self.peek().isdigit():
                    self.abort("Illegal character in number.")
                while self.peek().isdigit():
                    self.nextChar()
            
            tokText = self.source[startPos : self.curPos + 1]  # get substring
            token = Token(tokText, TokenType.NUMBER)
        elif self.curChar.isalpha():
            # leading character is a letter so this must be an identifier or keyword
            # get all consecutive alphanumeric characters
            startPos = self.curPos
            while self.peek().isalnum():
                self.nextChar()

            # check if the token is in the list of keywords
            tokText = self.source[startPos : self.curPos + 1]
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None:  # identifier
                token = Token(tokText, TokenType.IDENT)
            else:  # keyword
                token = Token(tokText, keyword)
        else:
            self.abort("Unknown token: " + self.curChar)  # unknown token

        self.nextChar()
        return token


# token contains the original text and the type of token
class Token:
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText  # used for identifies, strings, numbers
        self.kind = tokenKind

    @staticmethod
    def checkIfKeyword(tokenText):
        for kind in TokenType:
            # relies on all keyword enum values being 1XX
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None

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