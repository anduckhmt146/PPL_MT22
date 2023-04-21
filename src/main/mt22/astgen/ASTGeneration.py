from MT22Visitor import MT22Visitor
from MT22Parser import MT22Parser
from AST import *


class ASTGeneration(MT22Visitor):
    # program: decls EOF;
    def visitProgram(self, ctx: MT22Parser.ProgramContext):
        return Program(self.visit(ctx.decls()))

    # decls: decl decls | decl;
    def visitDecls(self, ctx: MT22Parser.DeclsContext):
        if ctx.getChildCount() == 1:
            return self.visit(ctx.decl())
        return self.visit(ctx.decl()) + self.visit(ctx.decls())

    # decl: vardecl | funcdecl;
    def visitDecl(self, ctx: MT22Parser.DeclContext):
        if ctx.vardecl():
            return self.visit(ctx.vardecl())
        return self.visit(ctx.funcdecl())

    # boolit: TRUE | FALSE;
    def visitBoolit(self, ctx: MT22Parser.BoolitContext):
        return BooleanLit(True) if ctx.TRUE() else BooleanLit(False)

    # arraylit: LP exprlist RP;
    def visitArraylit(self, ctx: MT22Parser.ArraylitContext):
        return ArrayLit(self.visit(ctx.exprlist()))

    # exprlist: exprprime | ;
    def visitExprlist(self, ctx: MT22Parser.ExprlistContext):
        if ctx.exprprime():
            return self.visit(ctx.exprprime())
        return []

    # exprprime: expr COMMA exprprime | expr;
    def visitExprprime(self, ctx: MT22Parser.ExprprimeContext):
        if ctx.getChildCount() == 1:
            return [self.visit(ctx.expr())]
        return [self.visit(ctx.expr())] + self.visit(ctx.exprprime())

    # atomictype: BOOLEAN | INTEGER | FLOAT | STRING;
    def visitAtomictype(self, ctx: MT22Parser.AtomictypeContext):
        if ctx.BOOLEAN():
            return BooleanType()
        elif ctx.INTEGER():
            return IntegerType()
        elif ctx.FLOAT():
            return FloatType()
        else:
            return StringType()

    # arraytype: ARRAY LS dimensions RS OF atomictype;
    def visitArraytype(self, ctx: MT22Parser.ArraytypeContext):
        atomictype = self.visit(ctx.atomictype())
        dimensions = self.visit(ctx.dimensions())
        return ArrayType([x.val for x in dimensions], atomictype)

    # dimensions: INTLIT COMMA dimensions | INTLIT;
    def visitDimensions(self, ctx: MT22Parser.DimensionsContext):
        if ctx.getChildCount() == 1:
            return [IntegerLit(int(ctx.INTLIT().getText()))]
        return [IntegerLit(int(ctx.INTLIT().getText()))] + self.visit(ctx.dimensions())

    # vartype: atomictype | arraytype | AUTO;
    def visitVartype(self, ctx: MT22Parser.VartypeContext):
        if ctx.atomictype():
            return self.visit(ctx.atomictype())
        elif ctx.arraytype():
            return self.visit(ctx.arraytype())
        else:
            return AutoType()

    # functype: vartype | VOID;
    def visitFunctype(self, ctx: MT22Parser.FunctypeContext):
        if ctx.vartype():
            return self.visit(ctx.vartype())
        return VoidType()

    # vardecl: idlist COLON vartype SEMI | varinit;
    def visitVardecl(self, ctx: MT22Parser.VardeclContext):
        if ctx.varinit():
            return self.visit(ctx.varinit())
        else:
            idlist = self.visit(ctx.idlist())
            vartype = self.visit(ctx.vartype())
            return list(map(lambda x: VarDecl(x.name, vartype, None), idlist))

    # varinit: idlist COLON vartype ASSIGN exprprime SEMI;
    def visitVarinit(self, ctx: MT22Parser.VarinitContext):
        idlist = self.visit(ctx.idlist())
        vartype = self.visit(ctx.vartype())
        exprprime = self.visit(ctx.exprprime())
        return [VarDecl(idlist[i].name, vartype, exprprime[i]) for i in range(len(idlist))]

    # idlist: ID COMMA idlist | ID;
    def visitIdlist(self, ctx: MT22Parser.IdlistContext):
        if ctx.getChildCount() == 1:
            return [Id(ctx.ID().getText())]
        return [Id(ctx.ID().getText())] + self.visit(ctx.idlist())

    # expr: relaexpr CONCAT relaexpr | relaexpr;
    def visitExpr(self, ctx: MT22Parser.ExprContext):
        if ctx.CONCAT():
            left = self.visit(ctx.relaexpr(0))
            right = self.visit(ctx.relaexpr(1))
            return BinExpr(ctx.CONCAT().getText(), left, right)
        return self.visit(ctx.relaexpr(0))

    # relaexpr: logexpr1 (EQ | NOTEQ | LT | GT | LEQ | GEQ) logexpr1 | logexpr1;
    def visitRelaexpr(self, ctx: MT22Parser.RelaexprContext):
        if ctx.EQ():
            left = self.visit(ctx.logexpr1(0))
            right = self.visit(ctx.logexpr1(1))
            return BinExpr(ctx.EQ().getText(), left, right)
        elif ctx.NOTEQ():
            left = self.visit(ctx.logexpr1(0))
            right = self.visit(ctx.logexpr1(1))
            return BinExpr(ctx.NOTEQ().getText(), left, right)
        elif ctx.LT():
            left = self.visit(ctx.logexpr1(0))
            right = self.visit(ctx.logexpr1(1))
            return BinExpr(ctx.LT().getText(), left, right)
        elif ctx.GT():
            left = self.visit(ctx.logexpr1(0))
            right = self.visit(ctx.logexpr1(1))
            return BinExpr(ctx.GT().getText(), left, right)
        elif ctx.LEQ():
            left = self.visit(ctx.logexpr1(0))
            right = self.visit(ctx.logexpr1(1))
            return BinExpr(ctx.LEQ().getText(), left, right)
        elif ctx.GEQ():
            left = self.visit(ctx.logexpr1(0))
            right = self.visit(ctx.logexpr1(1))
            return BinExpr(ctx.GEQ().getText(), left, right)
        else:
            return self.visit(ctx.logexpr1(0))

    # logexpr1: logexpr1 (AND | OR) addexpr | addexpr;
    def visitLogexpr1(self, ctx: MT22Parser.Logexpr1Context):
        if ctx.AND():
            left = self.visit(ctx.logexpr1())
            right = self.visit(ctx.addexpr())
            return BinExpr(ctx.AND().getText(), left, right)
        elif ctx.OR():
            left = self.visit(ctx.logexpr1())
            right = self.visit(ctx.addexpr())
            return BinExpr(ctx.OR().getText(), left, right)
        else:
            return self.visit(ctx.addexpr())

    # addexpr: addexpr (ADD | SUB) mulexpr | mulexpr;
    def visitAddexpr(self, ctx: MT22Parser.AddexprContext):
        if ctx.ADD():
            left = self.visit(ctx.addexpr())
            right = self.visit(ctx.mulexpr())
            return BinExpr(ctx.ADD().getText(), left, right)
        elif ctx.SUB():
            left = self.visit(ctx.addexpr())
            right = self.visit(ctx.mulexpr())
            return BinExpr(ctx.SUB().getText(), left, right)
        else:
            return self.visit(ctx.mulexpr())

    # mulexpr: mulexpr (MUL | DIV | MOD) logexpr2 | logexpr2;
    def visitMulexpr(self, ctx: MT22Parser.MulexprContext):
        if ctx.MUL():
            left = self.visit(ctx.mulexpr())
            right = self.visit(ctx.logexpr2())
            return BinExpr(ctx.MUL().getText(), left, right)
        elif ctx.DIV():
            left = self.visit(ctx.mulexpr())
            right = self.visit(ctx.logexpr2())
            return BinExpr(ctx.DIV().getText(), left, right)
        elif ctx.MOD():
            left = self.visit(ctx.mulexpr())
            right = self.visit(ctx.logexpr2())
            return BinExpr(ctx.MOD().getText(), left, right)
        else:
            return self.visit(ctx.logexpr2())

    # logexpr2: NOT logexpr2 | signexpr;
    def visitLogexpr2(self, ctx: MT22Parser.Logexpr2Context):
        if ctx.NOT():
            return UnExpr(ctx.NOT().getText(), self.visit(ctx.logexpr2()))
        else:
            return self.visit(ctx.signexpr())

    # signexpr: SUB signexpr | indexop;
    def visitSignexpr(self, ctx: MT22Parser.SignexprContext):
        if ctx.SUB():
            return UnExpr(ctx.SUB().getText(), self.visit(ctx.signexpr()))
        else:
            return self.visit(ctx.indexop())

    # indexop: ID LS exprprime RS | operand;
    def visitIndexop(self, ctx: MT22Parser.IndexopContext):
        if ctx.operand():
            return self.visit(ctx.operand())
        else:
            name = Id(ctx.ID().getText()).name
            cell = self.visit(ctx.exprprime())
            return ArrayCell(name, cell)

    # operand: subexpr | ID | INTLIT | FLOATLIT | STRINGLIT | boolit | arraylit | callexpr;
    def visitOperand(self, ctx: MT22Parser.OperandContext):
        if ctx.subexpr():
            return self.visit(ctx.subexpr())
        elif ctx.ID():
            return Id(ctx.ID().getText())
        elif ctx.INTLIT():
            return IntegerLit(int(ctx.INTLIT().getText()))
        elif ctx.FLOATLIT():
            if str(ctx.FLOATLIT().getText())[0:2] == '.e' or str(ctx.FLOATLIT().getText())[0:2] == '.E':
                return FloatLit(0.0)
            return FloatLit(float(ctx.FLOATLIT().getText()))
        elif ctx.STRINGLIT():
            return StringLit(str(ctx.STRINGLIT().getText()))
        elif ctx.boolit():
            return self.visit(ctx.boolit())
        elif ctx.arraylit():
            return self.visit(ctx.arraylit())
        else:
            return self.visit(ctx.callexpr())

    # subexpr: LB expr RB;
    def visitSubexpr(self, ctx: MT22Parser.SubexprContext):
        return self.visit(ctx.expr())

    # callexpr: ID LB exprlist RB;
    def visitCallexpr(self, ctx: MT22Parser.CallexprContext):
        name = Id(ctx.ID().getText()).name
        args = self.visit(ctx.exprlist())
        return FuncCall(name, args)

    # paradecl: INHERIT OUT ID COLON vartype | ID COLON vartype | INHERIT ID COLON vartype | OUT ID COLON vartype;
    def visitParadecl(self, ctx: MT22Parser.ParadeclContext):
        name = Id(ctx.ID().getText()).name
        typ = self.visit(ctx.vartype())
        out = True if ctx.OUT() else False
        inherit = True if ctx.INHERIT() else False
        return ParamDecl(name, typ, out, inherit)

    # paralist: paraprime | ;
    def visitParalist(self, ctx: MT22Parser.ParalistContext):
        if ctx.paraprime():
            return self.visit(ctx.paraprime())
        return []

    # paraprime: paradecl COMMA paraprime | paradecl;
    def visitParaprime(self, ctx: MT22Parser.ParaprimeContext):
        if ctx.getChildCount() == 1:
            return [self.visit(ctx.paradecl())]
        return [self.visit(ctx.paradecl())] + self.visit(ctx.paraprime())

    # funcdecl: ID COLON FUNCTION functype LB paralist RB INHERIT ID body | ID COLON FUNCTION functype LB paralist RB body;
    def visitFuncdecl(self, ctx: MT22Parser.FuncdeclContext):
        name = Id(ctx.ID(0).getText()).name
        return_type = self.visit(ctx.functype())
        params = self.visit(ctx.paralist())
        inherit = Id(ctx.ID(1).getText()).name if ctx.INHERIT() else None
        body = self.visit(ctx.body())
        return [FuncDecl(name, return_type, params, inherit, body)]

    # body: LP stmtlist RP;
    def visitBody(self, ctx: MT22Parser.BodyContext):
        return BlockStmt(self.visit(ctx.stmtlist()))

    # stmtlist: stmt stmtlist | vardecl stmtlist | ;
    def visitStmtlist(self, ctx: MT22Parser.StmtlistContext):
        if ctx.vardecl():
            return self.visit(ctx.vardecl()) + self.visit(ctx.stmtlist())
        elif ctx.stmtlist():
            return [self.visit(ctx.stmt())] + self.visit(ctx.stmtlist())
        return []

    # stmt: assignstmt | ifstmt | forstmt | whilestmt | dowhilestmt | breakstmt | continuestmt | returnstmt | callstmt | blockstmt;
    def visitStmt(self, ctx: MT22Parser.StmtContext):
        if ctx.assignstmt():
            return self.visit(ctx.assignstmt())
        elif ctx.ifstmt():
            return self.visit(ctx.ifstmt())
        elif ctx.forstmt():
            return self.visit(ctx.forstmt())
        elif ctx.whilestmt():
            return self.visit(ctx.whilestmt())
        elif ctx.dowhilestmt():
            return self.visit(ctx.dowhilestmt())
        elif ctx.breakstmt():
            return self.visit(ctx.breakstmt())
        elif ctx.continuestmt():
            return self.visit(ctx.continuestmt())
        elif ctx.returnstmt():
            return self.visit(ctx.returnstmt())
        elif ctx.callstmt():
            return self.visit(ctx.callstmt())
        else:
            return self.visit(ctx.blockstmt())

    # assignstmt: ID ASSIGN expr SEMI | ID LS exprprime RS ASSIGN expr SEMI;
    def visitAssignstmt(self, ctx: MT22Parser.AssignstmtContext):
        if ctx.exprprime():
            name = Id(ctx.ID().getText()).name
            cell = self.visit(ctx.exprprime())
            lhs = ArrayCell(name, cell)
            rhs = self.visit(ctx.expr())
            return AssignStmt(lhs, rhs)
        else:
            lhs = Id(ctx.ID().getText())
            rhs = self.visit(ctx.expr())
            return AssignStmt(lhs, rhs)

    # ifstmt: IF LB expr RB stmt (ELSE stmt | );
    def visitIfstmt(self, ctx: MT22Parser.IfstmtContext):
        if ctx.stmt(1):
            cond = self.visit(ctx.expr())
            tstmt = self.visit(ctx.stmt(0))
            fstmt = self.visit(ctx.stmt(1))
            return IfStmt(cond, tstmt, fstmt)
        return IfStmt(self.visit(ctx.expr()), self.visit(ctx.stmt(0)), None)

    # forstmt: FOR LB ID ASSIGN expr COMMA expr COMMA expr RB stmt | FOR LB ID LS exprprime RS ASSIGN expr COMMA expr COMMA expr RB stmt;
    def visitForstmt(self, ctx: MT22Parser.ForstmtContext):
        if ctx.exprprime():
            name = Id(ctx.ID().getText()).name
            cell = self.visit(ctx.exprprime())
            lhs = ArrayCell(name, cell)
        else:
            lhs = Id(ctx.ID().getText())
        rhs = self.visit(ctx.expr(0))
        init = AssignStmt(lhs, rhs)
        cond = self.visit(ctx.expr(1))
        upd = self.visit(ctx.expr(2))
        stmt = self.visit(ctx.stmt())
        return ForStmt(init, cond, upd, stmt)

    # whilestmt: WHILE LB expr RB stmt;
    def visitWhilestmt(self, ctx: MT22Parser.WhilestmtContext):
        cond = self.visit(ctx.expr())
        stmt = self.visit(ctx.stmt())
        return WhileStmt(cond, stmt)

    # dowhilestmt: DO blockstmt WHILE LB expr RB SEMI;
    def visitDowhilestmt(self, ctx: MT22Parser.DowhilestmtContext):
        cond = self.visit(ctx.expr())
        stmt = self.visit(ctx.blockstmt())
        return DoWhileStmt(cond, stmt)

    # breakstmt: BREAK SEMI;
    def visitBreakstmt(self, ctx: MT22Parser.BreakstmtContext):
        return BreakStmt()

    # continuestmt: CONTINUE SEMI;
    def visitContinuestmt(self, ctx: MT22Parser.ContinuestmtContext):
        return ContinueStmt()

    # returnstmt: RETURN expr SEMI | RETURN SEMI;
    def visitReturnstmt(self, ctx: MT22Parser.ReturnstmtContext):
        if ctx.expr():
            expr = self.visit(ctx.expr())
            return ReturnStmt(expr)
        return ReturnStmt(None)

    # callstmt: ID LB exprlist RB SEMI;
    def visitCallstmt(self, ctx: MT22Parser.CallstmtContext):
        name = Id(ctx.ID().getText()).name
        args = self.visit(ctx.exprlist())
        return CallStmt(name, args)

    # blockstmt: LP stmtlist RP;
    def visitBlockstmt(self, ctx: MT22Parser.BlockstmtContext):
        return BlockStmt(self.visit(ctx.stmtlist()))
