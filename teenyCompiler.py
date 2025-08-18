from lex import *
from parse import *
import sys

def main():
    print("BASIC Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: compiler needs source file as argument")
    with open(sys.argv[1], 'r') as sourceFile:
        source = sourceFile.read()

    # initialise lexer and parser
    lexer = Lexer(source)
    parser = Parser(lexer)

    parser.program()  # start the parser
    print("Parsing completed.")

main()