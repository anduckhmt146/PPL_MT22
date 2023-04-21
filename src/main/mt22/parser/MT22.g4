// 2010102

grammar MT22;

@lexer::header {
from lexererr import *
}

options{
	language=Python3;
}

//------------------------------PARSER--------------------------------------

program: decls EOF;
decls: decl decls | decl;
decl: vardecl | funcdecl;

// ARRAYLIT
boolit: TRUE | FALSE;
arraylit: LP exprlist RP;
exprlist: exprprime | ;
exprprime: expr COMMA exprprime | expr;

// TYPE
atomictype: BOOLEAN | INTEGER | FLOAT | STRING;
arraytype: ARRAY LS dimensions RS OF atomictype;
dimensions: INTLIT COMMA dimensions | INTLIT;
vartype: atomictype | arraytype | AUTO;
functype: vartype | VOID;

// DECLARATION VARIABLE
vardecl: idlist COLON vartype SEMI | varinit;
varinit: idlist COLON vartype ASSIGN exprprime SEMI;
idlist: ID COMMA idlist | ID;

// EXPRESSION
expr: relaexpr CONCAT relaexpr | relaexpr;
relaexpr: logexpr1 (EQ | NOTEQ | LT | GT | LEQ | GEQ) logexpr1 | logexpr1;
logexpr1: logexpr1 (AND | OR) addexpr | addexpr;
addexpr: addexpr (ADD | SUB) mulexpr | mulexpr;
mulexpr: mulexpr (MUL | DIV | MOD) logexpr2 | logexpr2;
logexpr2: NOT logexpr2 | signexpr;
signexpr: SUB signexpr | indexop;
indexop: ID LS exprprime RS | operand;
operand: subexpr | ID | INTLIT | FLOATLIT | STRINGLIT | boolit | arraylit | callexpr;
subexpr: LB expr RB;
callexpr: ID LB exprlist RB;

// DECLARATION PARAMETER
paradecl: INHERIT OUT ID COLON vartype | ID COLON vartype | INHERIT ID COLON vartype | OUT ID COLON vartype;
paralist: paraprime | ;
paraprime: paradecl COMMA paraprime | paradecl;

// DECLARATION FUNCTION
funcdecl: ID COLON FUNCTION functype LB paralist RB INHERIT ID body | ID COLON FUNCTION functype LB paralist RB body;

// STATEMENTS
body: LP stmtlist RP;
stmtlist: stmt stmtlist | vardecl stmtlist | ;
stmt: assignstmt | ifstmt | forstmt | whilestmt | dowhilestmt | breakstmt | continuestmt | returnstmt | callstmt | blockstmt;
assignstmt: ID ASSIGN expr SEMI | ID LS exprprime RS ASSIGN expr SEMI;
ifstmt: IF LB expr RB stmt (ELSE stmt | );
forstmt: FOR LB ID ASSIGN expr COMMA expr COMMA expr RB stmt | FOR LB ID LS exprprime RS ASSIGN expr COMMA expr COMMA expr RB stmt;
whilestmt: WHILE LB expr RB stmt;
dowhilestmt: DO blockstmt WHILE LB expr RB SEMI;
breakstmt: BREAK SEMI;
continuestmt: CONTINUE SEMI;
returnstmt: RETURN expr SEMI | RETURN SEMI;
callstmt: ID LB exprlist RB SEMI;
blockstmt: LP stmtlist RP;

//------------------------------LEXER----------------------------------------

// KEYWORDS
AUTO: 'auto';
BREAK: 'break';
BOOLEAN: 'boolean';
DO: 'do';
ELSE: 'else';
FALSE: 'false';
FLOAT: 'float';
FOR: 'for';
FUNCTION: 'function';
IF: 'if';
INTEGER: 'integer';
RETURN: 'return';
STRING: 'string';
TRUE: 'true';
WHILE: 'while';
VOID: 'void';
OUT: 'out';
CONTINUE: 'continue';
OF: 'of';
INHERIT: 'inherit';
ARRAY: 'array';

// SEPERATORS
LB: '(';
RB: ')';
LS: '[';
RS: ']';
LP: '{';
RP: '}';
DOT: '.';
COMMA: ',';
SEMI: ';';
COLON: ':';
ASSIGN: '=';

// OPERATORS
ADD: '+';
SUB: '-';
MUL: '*';
DIV: '/';
MOD: '%';
NOT: '!';
AND: '&&';
OR: '||';
EQ: '==';
NOTEQ: '!=';
LT: '<';
LEQ: '<=';
GT: '>';
GEQ: '>=';
CONCAT: '::';
ID: [a-zA-Z_] [a-zA-Z0-9_]*;

// LITERALS
fragment ESC_SEQ : '\\' ['"bfnrt\\];
fragment CHARACTER: ~["\r\n\\] | ESC_SEQ;
fragment ILLEGAL_ESC_SEQ: '\\' ~[bfnrt'"\\] | '\\';
fragment INT_PART: [1-9] [0-9]* | [0];
fragment SPEC_PART: [1-9] [0-9]*;
fragment DECIMAL_PART: '.' [0-9]*;
fragment EXPONENT_PART: [eE] [+-]? [0-9]+;
fragment INT_UNDERSCORE_PART: INT_PART | SPEC_PART ('_' [0-9]+)*;
INTLIT: INT_PART | SPEC_PART ('_' [0-9]+)* {self.text = self.text.replace("_", "")};
FLOATLIT: INT_UNDERSCORE_PART DECIMAL_PART EXPONENT_PART 
					{self.text = self.text.replace("_", "")}
				| INT_UNDERSCORE_PART DECIMAL_PART 
					{self.text = self.text.replace("_", "")}
				| INT_UNDERSCORE_PART EXPONENT_PART 
					{self.text = self.text.replace("_", "")}
				| DECIMAL_PART EXPONENT_PART;
STRINGLIT: '"' (CHARACTER)* '"' {self.text = self.text[1:-1]};

// COMMENTS
BLOCK_COMMENT: '/*' (.)*? '*/' -> skip;
LINE_COMMENT:  '//' ~[\r\n]* -> skip;

WS : [ \t\b\f\r\n]+ -> skip ; // skip spaces, tabs, newlines

ERROR_CHAR: . {raise ErrorToken(self.text)};
UNCLOSE_STRING: '"' (CHARACTER)* (EOF|'\r'|'\f'|'\n') {
	if self.text[-1] in ['\r','\n','\f']:
		raise UncloseString(self.text[1:-1])
	else:
		raise UncloseString(self.text[1:])
};
ILLEGAL_ESCAPE: '"' (CHARACTER)* (ILLEGAL_ESC_SEQ) {raise IllegalEscape(self.text[1:])};