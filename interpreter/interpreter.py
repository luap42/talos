import sys, copy, time

from stdlib import *
from lexer import *
Symbols = SymbolTable()
Procedures = SymbolTable()
Structures = SymbolTable()
Instances = SymbolTable()
RANDOM_SEED = Random()
OBJECT_COUNT = Random()

def eval_term(term): 
    term = [t if not t.type == "CONCRETE" else Token("EVALCONC", str(round(float(t.value), t.value.c))) for t in term]        
    i = 0
    while i < len(term):
        st = term[i]
        if st.type == "BRACK_START_SIGN":
            nt = []
            n = 1
            while n > 0:
                nt.append(st)
                del(term[i])
                if i >= len(term):
                    return Error("SyntaxError", "Unclosed bracket")
                st = term[i]
                if st.type == "BRACK_START_SIGN":
                    n+=1
                elif st.type == "BRACK_STOP_SIGN":
                    n-=1
            term[i] = eval_term(nt[1:])
            if term[i].isError:
                return term[i]
        elif st.type == "BRACK_STOP_SIGN":
            return Error("SyntaxError", "Unopened bracket")
        i+=1
    
    i = 0
    while i < len(term):
        st = term[i]
        if st.type == "MINUS_SIGN" and ((term[i-1].type not in ["NUMBER", "EVALCONC", "CONCRETE"]) or i == 0):
            del term[i]
            if term[i].type == "NUMBER":
                term[i].value = str(-1*int(term[i].value))
            elif term[i].type == "EVALCONC":
                term[i].value = str(-1*float(term[i].value))
            elif term[i].type == "CONCRETE":
                term[i] = term[i].value.mod(ConcreteWrapper.froms("-1"))
            else:
                return Error("SyntaxError", "Only Numbers or Concretes may follow Negation sign")
        i+=1
    # instance = instance_call("@init", (instance["@init"][1],args), instance, "&"+term[i].value[1:])
    
    i = 0
    while i < len(term):
        term[i] = solvevars(term[i])
        if term[i].isError:
            return term[i]
        if term[i].type == "STRUCT_SUBITEM_SIGN":
            if term[i-1].type != "INSTANCE":
                return Error("SyntaxError", "Only objects may have subitems")
            if term[i+1].type not in ["FUNCTION_CALL", "VARIABLE"]:
                return Error("SyntaxError", "Only methods and properties are valid subitems")
            if term[i+1].type == "VARIABLE":
                tim1 = term[i-1]
                tip1 = term[i+1]
                del term[i+1]
                del term[i]
                if not Instances[tim1.value].__hasitem__(tip1.value):
                    return Error("NotFoundError", "Property not found")
                term[i-1] = Instances[tim1.value][tip1.value]
                i-=1
            else:
                tim1 = term[i-1]
                tip1 = term[i+1]
                if not Instances[tim1.value].__hasitem__(tip1.value):
                    return Error("NotFoundError", "Method not found")
                argnum = len(Instances[tim1.value][tip1.value][1])
                term_i = term[i+1]
                if i+argnum > len(term):
                    return Error("ArgumentsError", "Not enough arguments for function " + term[i].value + ".")
                args = []
                for _ in range(argnum):
                    k+=1
                    args += [term[k]]
                ret = instance_call(tip1.value, (Instances[tim1.value][tip1.value][1],args), tim1, tim1.object)
                if ret[0].type=="ERROR_RETURN":
                    return ret[0]
                return_ = ret[1]
                del term[i+1]
                del term[i]
                term[i-1] = return_
                i -= 1
        i += 1
        
        
    if term == [None]:
        return Token("ARRAY", [])
    
    i = len(term) - 1
    while i >= 0:
        if term[i].type == "FUNCTION_CALL":
            k = i
            if Structures.__hasitem__("&"+term[i].value[1:]):
                struct = Structures["&"+term[i].value[1:]]
                instance = create_instance(struct)
                OBJECT_COUNT.next()
                oc = OBJECT_COUNT.get()
                Instances[oc] = instance
                if instance.__hasitem__("@init"):
                    argnum = len(instance["@init"][1])
                    term_i = term[i]
                    if i+argnum > len(term):
                        return Error("ArgumentsError", "Not enough arguments for function " + term[i].value + ".")
                    args = []
                    for _ in range(argnum):
                        k+=1
                        args += [term[k]]
                    instance_call("@init", (instance["@init"][1],args), Token("INSTANCE", oc), "&"+term[i].value[1:])
                term_i = Token("INSTANCE", oc)
                term_i.object = "&"+term[i].value[1:]
            elif term[i].value != "@random":
                argnum = function_parameter_number(term[i])
                term_i = term[i]
                if i+argnum > len(term):
                    return Error("ArgumentsError", "Not enough arguments for function " + term[i].value + ".")
                args = []
                for _ in range(argnum):
                    k+=1
                    args += [term[k]]
                term_i = solvefuncs(term_i, args)
                if term_i is not None and (term_i.type == "ERROR_RETURN" or term_i.isError):
                    return term_i
            else:
                t = time.time()
                argnum = 2
                if i+argnum > len(term):
                    return Error("ArgumentsError", "Not enough arguments for function " + term[i].value + ".")
                args = []
                for _ in range(argnum):
                    k+=1
                    args += [term[k]]
                low, high = args
                term_i = Token("NUMBER", int(int(low.value)+(((t**3) / (t+(RANDOM_SEED.get()%(int(high.value)-int(low.value))))%(int(high.value)-int(low.value))))))
                RANDOM_SEED.next()
            del term[i:k]
            if term_i != None and term_i.isError:
                return term[i]
            if term_i == None:
                del term[i]
            else:
                term[i] = term_i
        i-=1
        
    if term == [None]:
        return Token("ARRAY", [])
        
    i = 0
    while i < len(term):
        st = term[i]
        if st.type == "INDEX":
            if i == 0:
                return Error("SyntaxError", "Index cannot be first")
            t = term[i-1]
            if t.type != "ARRAY":
                print(term)
                return Error("SyntaxError", "Index must follow array")
            k = eval_term(lex(st.value)[0])
            if k.isError:
                return k
            elif k.type != "NUMBER":
                return Error("SyntaxError", "Index must be number")
            if int(k.value) >= len(t.value):
                return Error("OverflowError", "Index out of range")
            
            del term[i]
            term[i-1] = t.value[int(k.value)]
            i-=1
        i+=1
    
    i = len(term) - 1
    while i>=0:
        st = term[i]
        if st.type == "CAST":
            castto = st.value
            del term[i]
            st = term[i]
            if castto.endswith("[]"):
                if st.type != "ARRAY":
                    return Error("UncastableError", "Cannot cast value from type `"+st.type+"` to typed array")
                else:
                    if castto[:-2] == "string":
                        st.value = [Token("STRING", str(s.value)) for s in st.value]
                    elif castto[:-2] == "int":
                        if None in [re.match("^[0-9]+(\.[0-9]+)?$", s.value) for s in st.value]:
                            return Error("UncastableError", "Cannot cast to typed array when values don't match target type. Type: integer")
                        st.value = [Token("NUMBER", int(float(s.value))) for s in st.value]
                    elif castto[:-2] == "concrete":
                        if None in [re.match("^[0-9]+(\.[0-9]+)?$", s.value) for s in st.value]:
                            return Error("UncastableError", "Cannot cast to typed array when values don't match target type. Type: concrete")
                        st.value = [ConcreteWrapper.froms(s.value) for s in st.value]
                        st.value = [t if not t.type == "CONCRETE" else Token("EVALCONC", str(round(float(t.value), t.value.c))) for t in st.value]
                    elif castto[:-2] == "boolean":
                        if not False in [[s.type,  s.value] in [["STRING","true"], ["STRING","false"], ["STRING","1"], ["STRING","0"], ["NUMBER","1"], ["NUMBER","0"]] for s in st.value]:
                            st = [Token("BOOLEAN", "true") if s.value in ["true", "1"] else Token("BOOLEAN", "false") for s in st]
                        else:
                            return Error("UncastableError", "Cannot cast to typed array when values don't match target type. Type: boolean")
                    else:
                        return Error("CastTargetNotFoundError", "Cannot find cast type `"+castto[:-2]+"`")
            elif castto == "string":
                if st.type != "ARRAY":
                    if st.type == "FILE_STREAM":
                        st = solvefile(st)
                    else:
                        st.value = str(st.value)
                else:
                    st.value = ", ".join([str(s.value) for s in st.value])
                st.type = "STRING"
            elif castto == "int":
                if re.match("^[0-9]+(\.[0-9]+)?$", st.value):
                    st.type = "NUMBER"
                    st.value = str(int(float(st.value)))
                else:
                    return Error("UncastableError", "Cannot cast `"+st.value+"` to integer")
            elif castto == "concrete":
                if re.match("^[0-9]+(\.[0-9]+)?$", st.value):
                    st = ConcreteWrapper.froms(st.value)
                    st = Token("EVALCONC", str(round(float(st.value), st.value.c)))
                else:
                    return Error("UncastableError", "Cannot cast `"+st.value+"` to concrete")
            elif castto == "boolean":
                if [st.type,  st.value] in [["STRING","true"], ["STRING","false"], ["STRING","1"], ["STRING","0"], ["NUMBER","1"], ["NUMBER","0"]]:
                    if st.value in ["true", "1"]:
                        st = Token("BOOLEAN", "true")
                    else:
                        st = Token("BOOLEAN", "false")
                else:
                    return Error("UncastableError", "Cannot cast `"+st.type+":"+st.value+"` to boolean")
            elif castto == "file":
                if st.isError:
                    return st
                if st.type == "STRING":
                    st = Token("FILE_STREAM", st.value)
                else:
                    return Error("UncastableError", "Cannot cast `"+st.type+"` to file")
            elif castto == "count":
                if st.isError:
                    return st
                if st.type in ["ARRAY", "STRING"]:
                    st = Token("NUMBER", len(st.value))
                else:
                    return Error("UncastableError", "Cannot cast `"+st.type+"` to count")
            else:
                return Error("CastTargetNotFoundError", "Cannot find cast type `"+castto+"`")
            term[i] = st
        i-=1
    i = 0
    while i < len(term):
        st = term[i]
        if st.type == "TIMES_SIGN":
            op1 = term[i-1]
            op2 = term[i+1]
            if (op1.type, op2.type) in [("NUMBER", "NUMBER"), ("STRING", "NUMBER"), ("NUMBER", "STRING"), ("NUMBER","EVALCONC"), ("EVALCONC", "EVALCONC"), ("EVALCONC", "NUMBER")]:
                if op1.type == op2.type == "NUMBER":
                    res = Token("NUMBER", int(op1.value) * int(op2.value))
                elif (op1.type, op2.type) == ("NUMBER", "EVALCONC") or (op1.type, op2.type) == ("EVALCONC", "EVALCONC") or (op1.type, op2.type) == ("EVALCONC", "NUMBER"):
                    res = ConcreteWrapper.froms(str(op1.value)).value.mul(ConcreteWrapper.froms(str(op2.value)).value)
                elif op1.type == "STRING":
                    if(int(op2.value)<=0):
                        return Error("ValueError", "Cannot multiply string with negative integer or zero")
                    res = Token("STRING", op1.value * int(op2.value))
                else:
                    if(int(op1.value)<=0):
                        return Error("ValueError", "Cannot multiply string with negative integer or zero")
                    res = Token("STRING", int(op1.value) * op2.value)
                del term[i]
                del term[i]
                term[i-1] = res
                i -= 1
            else:
                return Error("TypeError", "Cannot multiply `"+op1.type+"` and `"+op2.type+"`")
        i += 1
        
    i = 0
    while i < len(term):
        st = term[i]
        if st.type == "BY_SIGN":
            op1 = term[i-1]
            op2 = term[i+1]
            if (op1.type, op2.type) in [("NUMBER", "NUMBER"), ("NUMBER","EVALCONC"), ("EVALCONC", "EVALCONC"), ("EVALCONC", "NUMBER")]:
                if(op1.type == op2.type == "NUMBER"):
                    if(0 in [int(op1.value), int(op2.value)]):
                        return Error("Div0Error", "Division by zero")
                    res = Token("NUMBER", int(int(op1.value) / int(op2.value)))
                elif (op1.type, op2.type) == ("NUMBER", "EVALCONC") or (op1.type, op2.type) == ("EVALCONC", "EVALCONC") or (op1.type, op2.type) == ("EVALCONC", "NUMBER"):
                    if 0.0 in [float(op1.value), float(op2.value)]:
                        return Error("Div0Error", "Division by zero")
                    res = ConcreteWrapper.froms(str(op1.value)).value.div(ConcreteWrapper.froms(str(op2.value)).value)
                del term[i] 
                del term[i]
                term[i-1] = res
                i -= 1
            else:
                return Error("TypeError", "Cannot divide `"+op1.type+"` and `"+op2.type+"`")
        i += 1
        
    i = 0
    while i < len(term):
        st = term[i]
        if st.type == "PLUS_SIGN":
            op1 = term[i-1]
            op2 = term[i+1]
            if (op1.type, op2.type) in [("NUMBER", "NUMBER"), ("NUMBER","EVALCONC"), ("EVALCONC", "EVALCONC"), ("EVALCONC", "NUMBER")] or "ARRAY" in (op1.type, op2.type) or "STRING" in (op1.type, op2.type):
                if (op1.type, op2.type) == ("NUMBER", "NUMBER"):
                    res = Token("NUMBER", int(int(op1.value) + int(op2.value)))
                elif (op1.type, op2.type) == ("NUMBER", "EVALCONC") or (op1.type, op2.type) == ("EVALCONC", "EVALCONC") or (op1.type, op2.type) == ("EVALCONC", "NUMBER"):
                    res = ConcreteWrapper.froms(str(op1.value)).value.add(ConcreteWrapper.froms(str(op2.value)).value)
                elif op1.type == "ARRAY":
                    res = Token("ARRAY", op1.value+[op2])
                elif op2.type == "ARRAY":
                    res = Token("ARRAY", [op1]+op2.value)
                else:
                    res = Token("STRING", str(op1.value) + str(op2.value))
                del term[i]
                del term[i]
                term[i-1] = res
                i -= 1
            else:
                return Error("TypeError", "Cannot add `"+op1.type+"` and `"+op2.type+"`")
        i += 1
        
    i = 0
    while i < len(term):
        st = term[i]
        if st.type == "MINUS_SIGN":
            op1 = term[i-1]
            op2 = term[i+1]
            if (op1.type, op2.type) in [("NUMBER", "NUMBER"), ("NUMBER","EVALCONC"), ("EVALCONC", "EVALCONC"), ("EVALCONC", "NUMBER")]:
                if(op1.type == op2.type == "NUMBER"):
                    res = Token("NUMBER", int(int(op1.value) - int(op2.value)))
                elif (op1.type, op2.type) == ("NUMBER", "EVALCONC") or (op1.type, op2.type) == ("EVALCONC", "EVALCONC") or (op1.type, op2.type) == ("EVALCONC", "NUMBER"):
                    res = ConcreteWrapper.froms(str(op1.value)).value.sub(ConcreteWrapper.froms(str(op2.value)).value)
                del term[i]
                del term[i]
                term[i-1] = res
                i -= 1
            else:
                return Error("TypeError", "Cannot subtract `"+op1.type+"` and `"+op2.type+"`")
        i += 1
        
    i = 0
    while i < len(term):
        st = term[i]
        if st.type not in  ["INSTANCE", "ARRAY"]:
            st = Token(st.type, str(st.value)) if not st.type == "CONCRETE" else Token("EVALCONC", str(round(float(st.value), st.value.c)))
        term[i] = st
        i+=1
    
    if len(term) != 1:
        term = Token("ARRAY", term)
    else:
        term = term[0]
    return term

def solvefile(expr):
    if expr.type == "FILE_STREAM":
        try:
            f = open(expr.value, "r")
            c = f.read()
            f.close()
            return Token("STRING", c)
        except:
            return Error("FileNotFoundError", "The file `"+expr.value+"` was not found.")
    return expr

def solvevars(var):
    if var == None: return Token("NULL", None)
    if var.isError: return var
    while var.type == "VARIABLE":
        if Symbols.__hasitem__(var.value):
            var = Symbols[var.value]
        else:
            return Error("NotFoundError", "Variable not found")
    return var

def function_parameter_number(func):
    if not Procedures.__hasitem__(func.value):
        return 0
    return len(Procedures[func.value][1])
    
def solvefuncs(func, params=[]):
    if func.type != "FUNCTION_CALL":
        return func
    else:
        if not Procedures.__hasitem__(func.value):
            return Error("NotFoundError", "Function not found")
        return subparse(Procedures[func.value][0], "$"+func.value[1:], (Procedures[func.value][1],params))
    
def subparse(prod, lookforreturn, params=((),())):
    mProcedurestable = copy.deepcopy(Procedures.table)
    mSymbolstable = copy.deepcopy(Symbols.table)
    i = 0
    for p in params[0]:
        Symbols[p.value] = params[1][i]
        i+=1
    if parse(prod) == -1:
        return Token("ERROR_RETURN", "")
    return_ = None
    if Symbols.__hasitem__(lookforreturn):
        return_ = Symbols[lookforreturn]
    Procedures.table = copy.deepcopy(mProcedurestable)
    Symbols.table = copy.deepcopy(mSymbolstable)
    return return_
    
def create_instance(struct):
    mProcedurestable = copy.deepcopy(Procedures.table)
    mSymbolstable = copy.deepcopy(Symbols.table)
    OneStructure = SymbolTable()
    Procedures.table = OneStructure.table
    Symbols.table = OneStructure.table
    if parse(struct) == -1:
        return Token("ERROR_RETURN", "")
    Procedures.table = copy.deepcopy(mProcedurestable)
    Symbols.table = copy.deepcopy(mSymbolstable)
    return OneStructure
    
def instance_call(func_name, args, obj, obj_name):
    func = Instances[obj.value][func_name][0]
    mProcedurestable = copy.deepcopy(Procedures.table)
    mSymbolstable = copy.deepcopy(Symbols.table)
    Symbols["$"+obj_name[1:]] = obj
    Symbols["$"+obj_name[1:]].object = obj_name
    i = 0
    for p in args[0]:
        Symbols[p.value] = args[1][i]
        i+=1
    if parse(func) == -1:
        return Token("ERROR_RETURN", ""), None
    return_ = None
    if Symbols.__hasitem__("$"+func_name[1:]):
        return_ = Symbols["$"+func_name[1:]]
    ret = obj
    Procedures.table = copy.deepcopy(mProcedurestable)
    Symbols.table = copy.deepcopy(mSymbolstable)
    return ret, return_

def parse(toks):
    if toks is None: return
    #print(toks)
    #return
    j = 0
    while j < len(toks):
        i = 0
        handled = False
        line = toks[j]
        while i < len(line):
            if line[i].type == "USE_STMT":
                handled = True
                if line[i+1].type != "STRING":
                    Error("SyntaxError", "Only string may follow USE statement").printMessage()
                    return -1
                what = line[i+1].value
                if what.startswith("mod:"):
                    what = what[4:] + ".talos"
                    try:
                        data = open_file(what)
                        tokens = lex(data)
                        parse(tokens)
                    except:
                        Error("ImportError", "Cannot load module `"+what+"`").printMessage()
                        return -1
                elif what.startswith("ext:"):
                    Error("NotSupportedError", "TALOS-Extensions not supported yet").printMessage()
                    return -1
                else:
                    Error("ImportTypeError", "Only mod: and ext: are valid import types").printMessage()
                    return -1
            elif line[i].type == "OUTPUT_STMT":
                handled = True
                i+=1
                op = eval_term(line[i:])
                if op.type == "ARRAY" and op.value == []:
                    print()
                    break
                if op.type == "ARRAY":
                    op = Token("ARRAY", [solvefile(p) for p in op.value if p.value is not None])
                else:
                    op = (solvefile(op))
                if op.isError or (op.type == "ARRAY" and True in [p.isError for p in op.value]):
                    if op.type == "ARRAY":
                        err = None
                        for p in op.value:
                            if p.isError:
                                err = p
                    else:
                        err = op
                    err.printMessage()
                    return -1
                if op.type == "ARRAY":
                    print(", ".join([str(p.value) for p in op.value]))
                else:
                    print(op.value)
                break
            elif line[i].type == "INPUT_STMT":
                handled = True
                output = line[i+2:]
                saveto_var = line[i+1]
                if saveto_var.type != "STREAM":
                    output.insert(0, saveto_var)
                    saveto_var = None
                op = eval_term(output)
                
                if op.type == "ARRAY":
                    op = ([solvefile(p) for p in op.value if p.value is not None])
                else:
                    op = (solvefile(op))
                if op.isError or (op.type == "ARRAY" and True in [p.isError for p in op.value]):
                    if op.type == "ARRAY":
                        err = None
                        for p in op.value:
                            if p.isError:
                                err = p
                    else:
                        err = op
                    err.printMessage()
                    return -1
                if op.type == "ARRAY":
                    result = input(", ".list(join(str(op.value))))
                else:
                    result = input(op.value)
                    
                if saveto_var:
                    Symbols[saveto_var.value] = Token("STRING", result)
                break
            elif line[i].type == "FILE_WRITE_STMT":
                handled = True
                output = line[i+2:]
                saveto_file = line[i+1]
                if saveto_file.type != "STREAM":
                    Error("SyntaxError", "fwrite needs to be followed by strean")
                    return -1
                saveto_file.type = "VARIABLE"
                op = eval_term(output)
                
                if op.type == "ARRAY":
                    op = ([solvefile(p) for p in op.value if p.value is not None])
                else:
                    op = (solvefile(op))
                if op.isError or (op.type == "ARRAY" and True in [p.isError for p in op.value]):
                    if op.type == "ARRAY":
                        err = None
                        for p in op.value:
                            if p.isError:
                                err = p
                    else:
                        err = op
                    err.printMessage()
                    return -1
                if op.type == "ARRAY":
                    result = (", ".list(join(str(op.value))))
                else:
                    result = (op.value)
                    
                
                f = open(solvevars(saveto_file).value, "w")
                f.write(result)
                f.close()
                saveto_file.type = "STREAM"
                break
            elif line[i].type == "EQUAL_SIGN":
                handled = True
                if line[0].type == "VARIABLE":
                    output = line[i+1:]
                    op = eval_term(output)
                    if op.isError or (op.type == "ARRAY" and True in [p.isError for p in op.value]):
                        if op.type == "ARRAY":
                            err = None
                            for p in op.value:
                                if p.isError:
                                    err = p
                        else:
                            err = op
                        err.printMessage()
                        return -1
                    else:
                        result = op
                    varname = line[0]
                    if i != 1:
                        if Symbols.__hasitem__(varname.value):
                            sv = solvevars(varname)
                            k = 1
                            sub = None
                            super_ = None
                            while k < len(line[:i]):
                                item = line[k]
                                if item.type == "INDEX":
                                    if sv.type == "ARRAY":
                                        if int(eval_term(lex(item.value)[0]).value) > len(sv.value):
                                            Error("OverflowError", "Index out of range").printMessage()
                                            return -1
                                        if k == len(line[:i]) - 1:
                                            super_ = sv.value
                                            sub = int(eval_term(lex(item.value)[0]).value)
                                            break
                                        else:
                                            sv = sv.value[int(eval_term(lex(item.value)[0]).value)]
                                    else:
                                        Error("SyntaxError", "Only arrays have index").printMessage()
                                        return -1
                                elif item.type == "STRUCT_SUBITEM_SIGN":
                                    if sv.type == "INSTANCE":
                                        if line[k+1].type == "VARIABLE":
                                            variable_name = line[k+1].value
                                            k += 1
                                            if k == len(line[:i]) - 1:
                                                super_ = Instances[sv.value]
                                                sub = variable_name
                                                break
                                            else:
                                                sv = Instances[sv.value][variable_name]
                                        else:
                                            Error("SyntaxError", "Only properties can be changed").printMessage()
                                            return -1
                                    else:
                                        Error("SyntaxError", "Only objects may have subitems").printMessage()
                                        return -1
                                elif k != len(line[:i]) - 1:
                                    Error("AssignmentError", "Cannot assign value-to-value").printMessage()
                                    return -1
                                k += 1
                            super_[sub] = result
                        else:
                            Error("AssignmentError", "Cannot assign value-to-value").printMessage()
                            return -1
                    else:
                        Symbols[varname.value] = result
                else:
                    Error("AssignmentError", "Cannot assign value-to-value").printMessage()
                    return -1
            elif line[i].type == "SUB_START_STMT":
                handled = True
                name = line[i+1]
                if name.type != "FUNCTION_CALL":
                    Error("SyntaxError", "Invalid function name").printMessage()
                    return -1
                name = name.value
                i+=2
                arglist = []
                while i < len(line):
                    if line[i].type != "VARIABLE":
                        Error("SyntaxError", "Only parameters might follow function definition").printMessage()
                        return -1
                    arglist += [line[i]]
                    i+=1
                contentlist = []
                broken = False
                while j < len(toks) and not broken:
                    handled = True
                    line = toks[j]
                    cl = []
                    while i < len(line):
                        if line[i].type == "SUB_STOP_STMT":
                            broken = True
                            break
                        cl.append(line[i])
                        i += 1
                    contentlist.append(cl)
                    if broken: break
                    i = 0
                    j+=1
                Procedures[name] = (contentlist[1:-1], arglist)
            elif line[i].type == "STRUCT_START_STMT":
                handled = True
                name = line[i+1]
                if name.type != "STRUCT":
                    Error("SyntaxError", "Invalid struct name").printMessage()
                    return -1
                name = name.value
                i+=2
                if line[i].type != "STRUCT_WITH_STMT":
                    Error("SyntaxError", "Invalid struct statement: missing WITH").printMessage()
                    return -1
                i += 1
                contentlist = []
                broken = False
                while j < len(toks) and not broken:
                    handled = True
                    line = toks[j]
                    cl = []
                    while i < len(line):
                        if line[i].type == "STRUCT_STOP_STMT":
                            broken = True
                            break
                        cl.append(line[i])
                        i += 1
                    contentlist.append(cl)
                    if broken: break
                    i = 0
                    j+=1
                Structures[name] = (contentlist[1:-1])
            elif line[i].type == "FOR_START_STMT":
                handled = True
                number = line[i+1]
                expr = []
                while number.type != "FOR_TIMES_STMT":
                    expr.append(number)
                    i+=1
                    if i >= len(line):
                        Error("SyntaxError", "FOR must be followed by TIMES").printMessage()
                        return -1
                    number = line[i+1]
                number = eval_term(expr)
                if number.type != "NUMBER":
                    Error("SyntaxError", "FOR must be followed by integer").printMessage()
                    return -1
                number = int(number.value)
                counter = None
                if len(line) > i+2 and line[i+2].type == "STREAM":
                    counter = line[i+2].value
                    i+=1
                i+=3
                ij = [i, j]
                contentlist = []
                n = 1
                while j < len(toks) and n > 0:
                    line = toks[j]
                    cl = []
                    while i < len(line) and n > 0:
                        if line[i].type == "FOR_STOP_STMT":
                            n -= 1
                        elif line[i].type == "FOR_START_STMT":
                            n += 1
                        cl.append(line[i])
                        i += 1
                    contentlist.append(cl)
                    i = 0
                    j+=1
                forstmt = (contentlist[1:-1])
                for k in range(number):
                    if counter:
                        Symbols[counter] = Token("NUMBER", k)
                    parse(forstmt)
                if counter:
                    del Symbols[counter]
                j-=1
                i = 0
            elif line[i].type == "IF_START_STMT":
                handled = True
                old_i = i
                while i < len(line):
                    i+=1
                    if line[i].type in ["EQUALITY_CHECK_SIGN", "INEQUALITY_CHECK_SIGN", "GREATER_THAN_SIGN", "SMALLER_THAN_SIGN"]:
                        break
                else:
                    Error("SyntaxError", "If must be followed by either `==`, `>`, `<` or `!=`").showMessage()
                    return -1
                end_i = i
                while end_i < len(line):
                    end_i += 1
                    if line[end_i].type == "THEN_STMT":
                        break
                else:
                    Error("SyntaxError", "If must be followed by `then`").showMessage()
                    return -1
                
                term1 = eval_term(line[old_i+1:i])
                term2 = eval_term(line[i+1:end_i])
                if (((line[i].type == "EQUALITY_CHECK_SIGN" and (term1.type, term1.value) != (term2.type, term2.value))) or ((line[i].type == "INEQUALITY_CHECK_SIGN" and (term1.type, term1.value) == (term2.type, term2.value))) or ((line[i].type == "SMALLER_THAN_SIGN" and term1.type != term2.type or term1.value >= term2.value)) or ((line[i].type == "GREATER_THAN_SIGN" and term1.type != term2.type or term1.value <= term2.value))):
                    n = None
                    i = old_i
                    while n is None or (j < len(toks) and n > 0):
                        line = toks[j]
                        while i < len(line):
                            if line[i].type == "IF_START_STMT":
                                if n == None:
                                    n = 1
                                else:
                                    n += 1
                            elif line[i].type == "IF_STOP_STMT":
                                n -= 1
                            i += 1
                        i = 0
                        j+=1
                    j -= 1
                    break
                else:
                    i = end_i
            i+=1
        if not handled:
            r = eval_term(line)
            if r.isError:
                r.printMessage()
                return -1
            elif r.type == "ERROR_RETURN":
                return -1
        j+=1
            
def run():
    if len(sys.argv) != 2:
        print("Only one argument: filename")
        return
    data = open_file(sys.argv[1])
    
    tokens = lex(data)
    parse(tokens)
run()
#print(Symbols)
#a = ConcreteWrapper.froms("10").value
#b = ConcreteWrapper.froms("1.5").value
#c = a.div(b).value
#print(float(c))
