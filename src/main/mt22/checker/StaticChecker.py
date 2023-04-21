from Visitor import Visitor
from StaticError import *
from AST import *
from abc import ABC


class MT22Type:
    def __init__(self, partype, rettype):
        self.partype = partype
        self.rettype = rettype


class Symbol:
    def __init__(self, name, type, value=None):
        self.name = name
        self.type = type
        self.value = value


class Utils:
    @staticmethod
    def searchDecl(name, typDecl, o):
        if o == None:
            return None
        for decl in o:
            if str(decl) == name and o[name]["declType"] == str(typDecl):
                return o[name]
        return None

    @staticmethod
    def searchInLoop(name, loopScope):
        if loopScope == []:
            return None
        for decl in loopScope:
            res = Utils.searchDecl(name, "Variable", decl)
            if res != None:
                return res
        return None

    @staticmethod
    def searchInScope(name, paramScope, globalScope, stmtScope):
        res = Utils.searchInLoop(name, stmtScope["loop"]) or Utils.searchDecl(name, "Variable", stmtScope) or Utils.searchDecl(name, "Parameter", paramScope) or Utils.searchDecl(
            name, "Variable", globalScope) or Utils.searchDecl(
            name, "Function", globalScope)
        return res

    @ staticmethod
    def convertVal2Type(typVal):
        if str(typVal)[0:3] == "Int":
            return "IntegerType"
        elif str(typVal)[0:3] == "Flo":
            return "FloatType"
        elif str(typVal)[0:3] == "Boo":
            return "BooleanType"
        elif str(typVal)[0:3] == "Str":
            return "StringType"
        else:
            return str(typVal)

    @ staticmethod
    def infer(name, infer_name, o):
        if type(infer_name) is Id:
            found = False
            for decl in o[2]:
                if decl == infer_name.name:
                    res = Utils.searchDecl(str(decl), "Variable", o[2])
                    if res != None:
                        o[0][name]["type"] = res["type"]
                        found = True
                        break

            for decl in o[0]:
                if decl == infer_name.name:
                    res = Utils.searchDecl(str(decl), "Parameter", o[0])
                    if res != None:
                        o[0][name]["type"] = res["type"]
                        found = True
                        break

            if found == False:
                for decl in o[1]:
                    if decl == infer_name.name:
                        res = Utils.searchDecl(str(decl), "Variable", o[1])
                        if res != None:
                            o[0][name]["type"] = res["type"]
                            break
            return o
        elif type(infer_name) is ArrayType:
            o[0][name]["type"] = str(infer_name)
            return o
        else:
            o[0][name]["type"] = Utils.convertVal2Type(infer_name)
            return o

    @ staticmethod
    def convertArrayLit(ast, arrList):
        exprList = list(arrList.explist)
        dimens = []
        dimen_size = len(exprList)
        if dimen_size > 0:
            dimens += [dimen_size]
            firstTyp = type(exprList[0])
            retTyp = None
            for expr in exprList:
                if type(expr) is not firstTyp:
                    raise IllegalArrayLiteral(ast)
                retTyp = Utils.convertVal2Type(expr)
        return dimen_size, retTyp


class StaticChecker(Visitor):
    global_envi = [
        Symbol("readInteger", MT22Type([], IntegerType())),
        Symbol("printInteger", MT22Type([IntegerType()], VoidType())),
        Symbol("readFloat", MT22Type([], FloatType())),
        Symbol("writeFloat", MT22Type([FloatType()], VoidType())),
        Symbol("readBoolean", MT22Type([], BooleanType())),
        Symbol("printBoolean", MT22Type([BooleanType()], VoidType())),
        Symbol("readString", MT22Type([], StringType())),
        Symbol("printString", MT22Type([StringType()], VoidType())),
        Symbol("super", MT22Type([[Expr()]], VoidType())),
        Symbol("preventDefault", MT22Type([], VoidType())),
    ]

    def __init__(self, ast):
        self.ast = ast
        self.inBlockStmt = 0
        self.countLoop = 0
        self.inheritFunc = False

    def check(self):
        return self.visitProgram(self.ast, [])

    # decls: List[Decl]
    def visitProgram(self, ast: Program, o):
        o = {}
        for decl in ast.decls:
            o = self.visit(decl, o)
        funcMain = Utils.searchDecl("main", "Function", o)
        if funcMain["type"] != "VoidType" or len(funcMain["params"]) != 0:
            raise NoEntryPoint()
        print(o)

    # name: str, typ: Type, init: Expr or None = None
    def visitVarDecl(self, ast: VarDecl, o):
        name = ast.name
        typ = ast.typ
        init = ast.init or None
        if type(init) is Id or type(init) is FuncCall:
            initValue = Utils.searchInScope(init.name, None, None, o)
            if initValue == None:
                raise Undeclared(Identifier(), init.name)
            if type(init) is FuncCall and initValue["type"] == "VoidType":
                raise TypeMismatchInExpression(ast)
            if initValue["type"] == "AutoType":
                o = Utils.infer(init.name, typ, o)
                initValue["type"] = str(typ)

        if type(init) is BinExpr:
            init = self.visit(init, o)

        if type(init) is ArrayLit:
            init = self.visit(init, o)

        if name in o:
            raise Redeclared(Variable(), str(name))
        if str(typ) == "AutoType":
            if type(init) is None:
                raise Invalid(Variable(), str(name))
            else:
                typ = Utils.convertVal2Type(init)

        initType = Utils.convertVal2Type(init)
        if initType == "VoidType":
            raise TypeMismatchInVarDecl(ast)
        if initType == "IntegerType" and str(typ) == "FloatType":
            initType = "FloatType"
            init = FloatLit(float(init.val))

        if initType != "None" and initType != str(typ):
            raise TypeMismatchInVarDecl(ast)
        if self.inBlockStmt > 0:
            if self.countLoop > 0:
                o[2]["loop"][self.countLoop - 1][name] = {
                    "declType": "Variable",
                    "type": str(typ),
                    "value": str(init)
                }
            else:
                o[2][name] = {
                    "declType": "Variable",
                    "type": str(typ),
                    "value": str(init)
                }
        else:
            o[name] = {
                "declType": "Variable",
                "type": str(typ),
                "value": str(init)
            }
        return o

    # name: str, typ: Type, out: bool = False, inherit: bool = False
    def visitParamDecl(self, ast: ParamDecl, o):
        name = ast.name
        typ = ast.typ
        out = ast.out
        inherit = ast.inherit
        if name in o:
            raise Redeclared(Parameter(), str(name))
        o[name] = {
            "declType": "Parameter",
            "type": str(typ),
            "inherit": str(inherit),
            "out": str(out)
        }
        return o

    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    def visitFuncDecl(self, ast: FuncDecl, o):
        name = ast.name
        ret = ast.return_type
        params = ast.params
        inherit = ast.inherit or None
        body = ast.body
        if name in o:
            raise Redeclared(Function(), str(name))
        o1 = {}
        for param in params:
            o1 = self.visit(param, o1)
        if inherit:
            parentFunc = Utils.searchDecl(inherit, "Function", o)
            if parentFunc == None:
                raise Undeclared(Function(), inherit)
            parentParams = parentFunc["params"]
            for param in params:
                inheritParam = Utils.searchDecl(
                    param.name, "Parameter", parentParams)
                if inheritParam != None and inheritParam["inherit"] == "True":
                    raise Invalid(Parameter(), param.name)
        o[name] = {
            "declType": "Function",
            "type": str(ret),
            "params": o1,
            "inherit": str(inherit)
        }
        o2 = [{}, {}, {}]
        o2[0] = o1
        o2[1] = {key: value for key, value in o.items()}
        o2[2] = {"loop": []}
        self.inheritFunc = inherit
        self.visit(body, o2)
        o[name].update({"stmt": o2[2]})
        return o

    def visitIntegerType(self, ast: IntegerType, o):
        return IntegerType()

    def visitFloatType(self, ast: FloatType, o):
        return FloatType()

    def visitBooleanType(self, ast: BooleanType, o):
        return BooleanType()

    def visitStringType(self, ast: StringType, o):
        return StringType()

    # dimensions: List[int], typ: AtomicType
    def visitArrayType(self, ast: ArrayType, o):
        return ArrayType(ast.dimensions, ast.typ)

    def visitAutoType(self, ast: AutoType, o):
        return AutoType()

    def visitVoidType(self, ast: VoidType, o):
        return VoidType()

    # op: str, left: Expr, right: Expr
    def visitBinExpr(self, ast: BinExpr, o):
        op = str(ast.op)
        left = self.visit(ast.left, o)
        right = self.visit(ast.right, o)
        leftValue, rightValue = None, None
        if type(left) is Id:
            leftValue = Utils.searchInScope(left.name, o[0], o[1], o[2])
            if leftValue == None:
                raise Undeclared(Variable(), left.name)
        elif type(left) is FuncCall:
            leftValue = Utils.searchInScope(left.name, o[0], o[1], o[2])
            if leftValue == None:
                raise Undeclared(Function(), left.name)

        if type(right) is Id:
            rightValue = Utils.searchInScope(right.name, o[0], o[1], o[2])
            if rightValue == None:
                raise Undeclared(Variable(), right.name)
        elif type(right) is FuncCall:
            rightValue = Utils.searchInScope(right.name, o[0], o[1], o[2])
            if rightValue == None:
                raise Undeclared(Function(), right.name)

        leftType, rightType = None, None
        if type(left) is Id:
            leftType = leftValue["type"]
        else:
            leftType = Utils.convertVal2Type(left)
        if type(right) is Id:
            rightType = rightValue["type"]
        else:
            rightType = Utils.convertVal2Type(right)

        if op in ["+", "-", "*", "/"]:
            if leftType != "IntegerType" and leftType != "FloatType":
                raise TypeMismatchInExpression(ast)
            if rightType != "IntegerType" and rightType != "FloatType":
                raise TypeMismatchInExpression(ast)
            if leftType == "FloatType" or rightType == "FloatType":
                return FloatType()
            return IntegerType()
        elif op in ['%']:
            if leftType != "IntegerType" or rightType != "IntegerType":
                raise TypeMismatchInExpression(ast)
            return IntegerType()

        elif op in ["&&", "||"]:
            if leftType != "BooleanType" or rightType != "BooleanType":
                raise TypeMismatchInExpression(ast)
            return BooleanType()

        elif op == "::":
            if leftType != "StringType" or rightType != "StringType":
                raise TypeMismatchInExpression(ast)
            return StringType()

        elif op in ["==", "!="]:
            if leftType == "IntegerType" and rightType == "IntegerType":
                return BooleanType()
            if leftType == "BooleanType" and rightType == "BooleanType":
                return BooleanType()
            raise TypeMismatchInExpression(ast)

        if op in ["<", ">", "<=", ">="]:
            if leftType == "IntegerType" and rightType == "FloatType":
                leftType = "FloatType"
            if rightType == "IntegerType" and leftType == "FloatType":
                rightType = "FloatType"
            if leftType != "IntegerType" and leftType != "FloatType":
                raise TypeMismatchInExpression(ast)
            if rightType != "IntegerType" and rightType != "FloatType":
                raise TypeMismatchInExpression(ast)
            return BooleanType()

        if op in ["&&", "||"]:
            if leftType == "BooleanType" and rightType == "BooleanType":
                return BooleanType()
            raise TypeMismatchInExpression(ast)

    # op: str, val: Expr
    def visitUnExpr(self, ast: UnExpr, o):
        val = self.visit(ast.val, o)
        op = ast.op
        operandVal = None
        if type(val) is Id:
            operandVal = Utils.searchInScope(val.name, o[0], o[1], o[2])
            if operandVal == None:
                raise Undeclared(Variable(), val.name)
        elif type(val) is FuncCall:
            operandVal = Utils.searchInScope(val.name, o[0], o[1], o[2])
            if operandVal == None:
                raise Undeclared(Function(), val.name)

        operandType = None
        if type(val) is Id:
            operandType = operandVal["type"]
        else:
            operandType = Utils.convertVal2Type(val)

        if op == "!":
            if operandType != "BooleanType":
                raise TypeMismatchInExpression(ast)
            return BooleanType()

        elif op == "-":
            if operandType == "IntegerType":
                return IntegerType()
            if operandType == "FloatType":
                return FloatType()
            raise TypeMismatchInExpression(ast)

    # name: str
    def visitId(self, ast: Id, o):
        return Id(str(ast.name))

    # name: str, cell: List[Expr]
    def visitArrayCell(self, ast: ArrayCell, o):
        arrayName = Utils.searchInScope(ast.name, o[0], o[1], o[2])
        if arrayName == None:
            raise Undeclared(Identifier(), ast.name)
        if arrayName["type"][0:3] != "Arr":
            raise TypeMismatchInExpression(ast)
        cellList = ast.cell
        for cell in cellList:
            if str(cell)[0:3] != "Int":
                raise TypeMismatchInExpression(ast)

    # val: int
    def visitIntegerLit(self, ast: IntegerLit, o):
        return IntegerLit(int(ast.val))

    # val: float
    def visitFloatLit(self, ast: FloatLit, o):
        return FloatLit(float(ast.val))

    # val: str
    def visitStringLit(self, ast: StringLit, o):
        return StringLit(str(ast.val))

    # val: bool
    def visitBooleanLit(self, ast: BooleanLit, o):
        return BooleanLit(bool(ast.val))

    # explist: List[Expr]
    def visitArrayLit(self, ast: ArrayLit, o):
        exprList = list(ast.explist)
        dimens = []
        dimen_row = len(exprList)
        if dimen_row > 0:
            dimens += [dimen_row]
            firstTyp = type(exprList[0])
            visitFirst = False
            retTyp = None
            for expr in exprList:
                if type(expr) is not firstTyp:
                    raise IllegalArrayLiteral(ast)
                retTyp = Utils.convertVal2Type(expr)
                if type(expr) is ArrayLit:
                    dimen_size, retTyp = Utils.convertArrayLit(ast, expr)
                    if visitFirst == False:
                        dimens += [dimen_size]
                        retTyp = retTyp
                        visitFirst = True
        return ArrayType(dimens, retTyp)

    # name: str, args: List[Expr]
    def visitFuncCall(self, ast: FuncCall, o):
        name = ast.name
        args = ast.args
        funcVal = Utils.searchInScope(name, o[0], o[1], o[2])
        if funcVal == None:
            raise Undeclared(Function(), name)
        funcRet = funcVal["type"]
        funcParams = funcVal["params"]
        args = list(args)
        lenFunc, lenCall = len(list(funcParams)), len(args)
        if lenFunc != lenCall:
            raise TypeMismatchInExpression(ast)
        for i in range(lenFunc):
            funcRet = list(funcParams.values())[i]
            paramRet = Utils.convertVal2Type(args[i])
            if funcRet["type"] == "AutoType":
                funcRet["type"] = paramRet
            if (funcRet["type"] != paramRet):
                raise TypeMismatchInExpression(ast)
        paraArgs = [self.visit(decl, o) for decl in args]
        return FuncCall(ast.name, paraArgs)

    # lhs: LHS, rhs: Expr
    def visitAssignStmt(self, ast: AssignStmt, o):
        rhs = self.visit(ast.rhs, o)
        lhs = self.visit(ast.lhs, o)
        lValue = None
        if type(rhs) is Id or type(rhs) is FuncCall:
            rValue = Utils.searchInScope(rhs.name, o[0], o[1], o[2])
            if rValue == None:
                raise Undeclared(Identifier(), rhs.name)
            if type(rhs) is FuncCall and rValue["type"] == "VoidType":
                raise TypeMismatchInStatement(ast)
            if rValue["type"] == "AutoType":
                o = Utils.infer(rhs.name, lhs, o)
                rValue = Utils.searchInScope(rhs.name, o[0], o[1], o[2])
            if type(lhs) is Id:
                lValue = Utils.searchInScope(lhs.name, o[0], o[1], o[2])
            if rValue["type"] != lValue["type"]:
                raise TypeMismatchInStatement(ast)

        if type(lhs) is Id:
            lValue = Utils.searchInScope(lhs.name, o[0], o[1], o[2])
            if lValue == None:
                raise Undeclared(Identifier(), lhs.name)
            if lValue["type"] == "AutoType":
                o = Utils.infer(lhs.name, rhs, o)
                lValue = Utils.searchInScope(lhs.name, o[0], o[1], o[2])
            if lValue["type"] == "FloatType" and str(rhs) == "IntegerType":
                rhs = FloatType()

            if type(rhs) is Id or type(rhs) is FuncCall:
                rValue = Utils.searchInScope(rhs.name, o[0], o[1], o[2])
                if rValue["type"] != lValue["type"]:
                    raise TypeMismatchInStatement(ast)
            else:
                rType = Utils.convertVal2Type(str(rhs))
                if rType != lValue["type"]:
                    raise TypeMismatchInStatement(ast)
        return lValue["type"]

    # body: List[Stmt or VarDecl]
    def visitBlockStmt(self, ast: BlockStmt, o):
        self.inBlockStmt += 1
        firstStmt = False
        for decl in ast.body:
            if self.inheritFunc == True and firstStmt == False:
                inheritCall = self.visit(decl, o)
                if str(inheritCall.name) == "super":
                    print("Super")

            if type(decl) is VarDecl:
                o = self.visit(decl, o)
            else:
                self.visit(decl, o)
            firstStmt = True
        self.inBlockStmt -= 1

    # cond: Expr, tstmt: Stmt, fstmt: Stmt or None = None
    def visitIfStmt(self, ast: IfStmt, o):
        cond = self.visit(ast.cond, o)
        if type(cond) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        self.visit(ast.tstmt, o)
        if type(ast.fstmt) is not None:
            self.visit(ast.fstmt, o)

    # init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt
    def visitForStmt(self, ast: ForStmt, o):
        self.countLoop += 1
        init = self.visit(ast.init, o)
        if init != "IntegerType":
            raise TypeMismatchInStatement(ast)
        cond = self.visit(ast.cond, o)
        if type(cond) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        upd = self.visit(ast.upd, o)
        if str(upd) != "IntegerType":
            raise TypeMismatchInStatement(ast)
        o[2]["loop"] = o[2]["loop"] + [{}]
        self.visit(ast.stmt, o)
        o[2]["loop"].pop(self.countLoop - 1)
        self.countLoop -= 1

    # cond: Expr, stmt: Stmt
    def visitWhileStmt(self, ast: WhileStmt, o):
        self.countLoop += 1
        cond = self.visit(ast.cond, o)
        if type(cond) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        o[2]["loop"] = o[2]["loop"] + [{}]
        self.visit(ast.stmt, o)
        o[2]["loop"].pop(self.countLoop - 1)
        self.countLoop -= 1

    # cond: Expr, stmt: BlockStmt
    def visitDoWhileStmt(self, ast: DoWhileStmt, o):
        self.countLoop += 1
        cond = self.visit(ast.cond, o)
        if type(cond) is not BooleanType:
            raise TypeMismatchInStatement(ast)
        o[2]["loop"] = o[2]["loop"] + [{}]
        self.visit(ast.stmt, o)
        o[2]["loop"].pop(self.countLoop - 1)
        self.countLoop -= 1

    def visitBreakStmt(self, ast: BreakStmt, o):
        if self.countLoop == 0:
            raise MustInLoop(ast)

    def visitContinueStmt(self, ast: ContinueStmt, o):
        if self.countLoop == 0:
            raise MustInLoop(ast)

    # expr: Expr or None = None
    def visitReturnStmt(self, ast: ReturnStmt, o): pass

    # name: str, args: List[Expr]
    def visitCallStmt(self, ast: CallStmt, o):
        name = ast.name
        args = ast.args
        funcVal = Utils.searchInScope(name, o[0], o[1], o[2])
        if funcVal == None:
            raise Undeclared(Function(), name)
        funcRet = funcVal["type"]
        funcParams = funcVal["params"]
        args = list(args)
        lenFunc, lenCall = len(list(funcParams)), len(args)
        if lenFunc != lenCall:
            raise TypeMismatchInStatement(ast)
        for i in range(lenFunc):
            funcRet = list(funcParams.values())[i]
            paramRet = Utils.convertVal2Type(args[i])
            if funcRet["type"] == "AutoType":
                funcRet["type"] = paramRet
            if (funcRet["type"] != paramRet):
                raise TypeMismatchInStatement(ast)
        return CallStmt(name, args)
