from lex import *
from emit import *
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
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program()  # start the parser
    emitter.writeFile()  # write the output to file
    print("Compiling completed.")

main()