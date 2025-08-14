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
        pass

    # skip whitespaces excpet newlines, which we will use to indicate the end of a statement
    def skipWhitespace(self):
        pass

    # skip comments in the code
    def skipComments(self):
        pass

    # return the next token
    def getToken(self):
        pass