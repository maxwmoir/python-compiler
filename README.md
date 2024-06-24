# python-compiler 

This is a compiler written in python I developed during a project for my 200 level formal languages and compilers class. 
The Compiler takes a BASIC like language as input. It first scans the input program, seperates it into tokens, parses these tokens, creates an abstract syntax tree, and compiles it into JVM code. This code can then be assembeled by Jasmin into a Java class file and run.

The accepted language has the following syntax (given in EBNF form)
https://en.wikipedia.orgwikiExtended_Backus%E2%80%93Naur_form

Program = Statements
Statements = Statement (; Statement)*
Statement = If | While | Assignment
If = if Comparison then Statements end
While = while Comparison do Statements end
Assignment = identifier := Expression
Comparison = Expression Relation Expression
Relation = = | != | < | <= | > | >=
Expression = Term ((+ | -) Term)*
Term = Factor ((* | /) Factor)*
Factor = (Expression) | number | identifier
BooleanExpression = BooleanTerm (or BooleanTerm)*
BooleanTerm = BooleanFactor (and BooleanFactor)*
BooleanFactor = not BooleanFactor | Comparison