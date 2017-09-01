import re
from stdlib import *

def lex(fc):
    lexlists = []
    fc = fc.split("\n")
    for fcl in fc:
        lexlist = []
        tok = ""
        state = "undefined"
        cache = ""
        fcl = list(fcl)
        fcl.append("<EOL>")
        
        i = -1
        while i < len(fcl) - 1:
            i+=1
            char = fcl[i]
            tok += char
            if char == "<EOL>":
                if state == "string":
                    print("Parser error")
                    return
                elif state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                elif state == "function_name":
                    lexlist += [Token("FUNCTION_CALL", cache)]
                    cache = ""
                    state = "undefined"
            elif tok == "\"" and state == "undefined":
                state = "string"
                tok = ""
            elif tok == "\"" and fcl[i-1] != "\\" and state == "string":
                cache = cache.replace("\\n", "\n")
                cache = cache.replace("\\r", "\r")
                cache = cache.replace("\\t", "\t")
                cache = cache.replace("\\\\", "\\")
                lexlist += [Token("STRING", cache)]
                cache = ""
                state = "undefined"
                tok = ""
            elif state == "string":
                if tok == "\"" and fcl[i-1] == "\\":
                    cache = cache[:-1]
                cache += tok
                tok = ""
            elif tok == "#":
                break
            elif tok == "<" and fcl[i+1] == "<" and state == "undefined":
                state = "cast"
                cache = ""
                tok = ""
                i+=1
            elif tok == ">" and fcl[i+1] == ">" and state == "cast":
                state = "undefined"
                lexlist += [Token("CAST", cache)]
                cache = ""
                tok = ""
                i+=1
            elif state == "cast":
                cache += tok
                tok = ""
            elif tok == "[" and state == "undefined":
                state = "index"
                cache = ""
                tok = ""
            elif tok == "]" and state == "index":
                state = "undefined"
                lexlist += [Token("INDEX", cache)]
                cache = ""
                tok = ""
            elif state == "index":
                cache += tok
                tok = ""
            elif tok == "|" and state == "undefined":
                state = "stream"
                cache = ""
                tok = ""
            elif tok == "|" and state == "stream":
                state = "undefined"
                lexlist += [Token("STREAM", cache)]
                cache = ""
                tok = ""
            elif state == "stream":
                cache += tok
                tok = ""
            elif tok == "$" and state == "undefined":
                state = "variable_name"
                cache += tok
                tok = ""
            elif tok == "@" and state == "undefined":
                state = "function_name"
                cache += tok
                tok = ""
            elif tok == "&" and state == "undefined":
                state = "struct_name"
                cache += tok
                tok = ""
            elif state == "variable_name":
                if (len(cache) == 1 and re.match("[a-zA-Z_]", tok)) or (len(cache) > 1 and re.match("[a-zA-Z0-9_]", tok)):
                    cache += tok
                else:
                    lexlist += [Token("VARIABLE", cache)]
                    state = "undefined"
                    cache = ""
                    i-=1
                    tok = ""
                    continue
                tok = ""
            elif state == "function_name":
                if (len(cache) == 1 and re.match("[a-zA-Z_]", tok)) or (len(cache) > 1 and re.match("[a-zA-Z0-9_]", tok)):
                    cache += tok
                else:
                    lexlist += [Token("FUNCTION_CALL", cache)]
                    state = "undefined"
                    cache = ""
                    i-=1
                    tok = ""
                    continue
                tok = ""
            elif state == "struct_name":
                if (len(cache) == 1 and re.match("[a-zA-Z_]", tok)) or (len(cache) > 1 and re.match("[a-zA-Z0-9_]", tok)):
                    cache += tok
                else:
                    lexlist += [Token("STRUCT", cache)]
                    state = "undefined"
                    cache = ""
                    i-=1
                    tok = ""
                    continue
                tok = ""
            elif tok == "=" and fcl[i+1] == "=":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("EQUALITY_CHECK_SIGN")]
                tok = ""
                cache = ""
                i+=1
            elif tok == "!" and fcl[i+1] == "=":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("INEQUALITY_CHECK_SIGN")]
                tok = ""
                cache = ""
                i+=1
            elif tok == ":" and fcl[i+1] == ":":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("STRUCT_SUBITEM_SIGN")]
                tok = ""
                cache = ""
                i+=1
            elif tok == "=" and state == "undefined":
                lexlist += [Token("EQUAL_SIGN")]
                tok = ""
                cache = ""
            elif tok in ["true", "false"]:
                lexlist += [Token("BOOLEAN", tok)]
                tok = ""
            elif tok == "say":
                lexlist += [Token("OUTPUT_STMT")]
                tok = ""
            elif tok == "listen":
                lexlist += [Token("INPUT_STMT")]
                tok = ""
            elif tok == "fwrite":
                lexlist += [Token("FILE_WRITE_STMT")]
                tok = ""
            elif tok == "if":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("IF_START_STMT")]
                tok = ""
            elif tok == "then":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("THEN_STMT")]
                tok = ""
            elif tok == "sub":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("SUB_START_STMT")]
                tok = ""
            elif tok == "endsub":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("SUB_STOP_STMT")]
                tok = ""
            elif tok == "endif":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("IF_STOP_STMT")]
                tok = ""
            elif tok == "for":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("FOR_START_STMT")]
                tok = ""
            elif tok == "times":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("FOR_TIMES_STMT")]
                tok = ""
            elif tok == "endfor":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("FOR_STOP_STMT")]
                tok = ""
            elif tok == "struct":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("STRUCT_START_STMT")]
                tok = ""
            elif tok == "with":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("STRUCT_WITH_STMT")]
                tok = ""
            elif tok == "endstruct":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("STRUCT_STOP_STMT")]
                tok = ""
            elif tok == "use":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("USE_STMT")]
                tok = ""
            elif tok in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]:
                cache += tok
                if state == "undefined":
                    state = "expression"
                tok = ""
            elif tok == "." and state == "expression":
                cache += tok
                tok = ""
                state = "concrete"
            elif tok == "+":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist.append(Token("PLUS_SIGN"))
                tok = ""
            elif tok == "-":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist.append(Token("MINUS_SIGN"))
                tok = ""
            elif tok == "*":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                                
                lexlist.append(Token("TIMES_SIGN"))
                tok = ""
            elif tok == "/":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist.append(Token("BY_SIGN"))
                tok = ""
            elif tok == "(":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist.append(Token("BRACK_START_SIGN"))
                tok = ""
            elif tok == ")":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist.append(Token("BRACK_STOP_SIGN"))
                tok = ""
            elif tok == "<":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist.append(Token("SMALLER_THAN_SIGN"))
                tok = ""
            elif tok == ">":
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist.append(Token("GREATER_THAN_SIGN"))
                tok = ""
            elif tok == " " or tok == "\t":
                tok = ""
                if state == "variable_name":
                    lexlist += [Token("VARIABLE", cache)]
                if state == "string":
                    lexlist += [Token("STRING", cache)]
                if state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                    
                state = "undefined"
                cache = ""
            elif tok == "null":
                if state == "string":
                    print("Parser error")
                    return
                elif state == "expression":
                    lexlist.append(Token("NUMBER", cache))
                    cache = ""
                    state = "undefined"
                elif state == "concrete":
                    lexlist.append(ConcreteWrapper.froms(cache))
                    cache = ""
                    state = "undefined"
                    
                lexlist += [Token("NULL", None)]
            elif tok == ";":
                if state == "variable_name":
                    lexlist += [Token("VARIABLE", cache)]
                lexlists.append(lexlist)
                lexlist=[]
                tok = ""
        if state == "variable_name":
            lexlist += [Token("VARIABLE", cache)]
        lexlists.append(lexlist)
    return lexlists