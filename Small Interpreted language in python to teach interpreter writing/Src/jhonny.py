import sys


if len(sys.argv) == 1:
    print("expected jhonny.py [filename]")
    exit(1)
code = open(sys.argv[1],'r').read().replace("\\n","\n")
tokens = []
stack = []
return_address_stack = []
symbol_table = {}
keywords = ["if","while","for","var","start","end","program","return"];
symbols = ['+','-','*','/','=','!','<','>','~','|','^','&',';','.',':','#']
pc = 0 # program counter

def lexer():
    global code
    index = 0 #index in code
    buffer = "" #buffer in code
    while index<len(code):
        if code[index] == '\n' or code[index] == ' ' or code[index] == '\r' or code[index] == '\t':
            if len(buffer) != 0:
                tokens.append([buffer,"identifier"])
                buffer=""
            index+=1
            continue;
        if code[index] in symbols or code[index].isdigit():
            if len(buffer) != 0:
                tokens.append([buffer,"identifier"])
                buffer=""

        buffer += code[index]
       
       
        if(code[index] == '/' and code[index+1] == '/'):
            buffer = ""
            while(code[index] != '\n'):
                index+=1
        if buffer in keywords:
            tokens.append([buffer,"keyword"])
            buffer = ""
        if code[index] in symbols:
            tokens.append([buffer,"symbol"])
            buffer = ""
        if code[index].isdigit():
            index+=1
            while(code[index].isdigit()):
                buffer+=code[index]
                index+=1
            tokens.append([int(buffer),"number"])
            buffer = ""
            index-=1
        if(code[index] == '"'):
            buffer = ""
            index+=1
            while(code[index] != '"'):
                buffer+=code[index]
                index+=1
            index+=1
            tokens.append([buffer,"string"])
            buffer =""
        index += 1



def match(s):
    global pc
    if s == tokens[pc][0]:
        pc+=1
    else:
        print("error with match got: " + tokens[pc][0] + " expected: " + s)
        exit()
       
       
def program_pae():
    match("program")
    block_pae()
   
   
def skip_block():
    global pc
    match("start")
    while tokens[pc][0] != "end":
        #print(pc, len(tokens),tokens[pc+1])
        pc+=1
        if(tokens[pc][0] == "start"):
            skip_block()
           
       
    match("end")
   
def block_pae():
    global pc
   
    match("start")
   
    while tokens[pc][0] != "end":
       
        curtok =tokens[pc][0]
        curtok_t =tokens[pc][1]
        if(curtok == "if"):
            if_pae()
        elif(curtok == "while"):
            while_pae()
        elif(curtok == "for"):
            for_pae()
        elif(curtok == "var"):
            var_pae()
        elif(curtok_t == "identifier"):
            if tokens[pc+1][0] == '=':
                mutate_pae()
            else:
                expr_pae()
        elif(curtok == ":"):
            match(":")
            func_name = tokens[pc][0]
            pc+=1
            symbol_table[func_name] = [pc,'func']
            skip_block()
           
        elif(curtok == "return"):
            match("return")
            expr_pae();
        else:
            expr_pae()
       
       
    match("end")

def mutate_pae():
                global pc
                curtok = tokens[pc][0]
                name = curtok
                pc+=1
                match("=")
                expr_pae()
                symbol_table[name][0] = stack.pop()

def var_pae():
    global pc
    global symbol_table
    match("var")
    name = tokens[pc][0]
    pc+=1
    match("=")
    expr_pae()
    symbol_table[name] = [stack.pop(),"var"]
def expr_pae():
    global pc
    global symbol_table
    while(tokens[pc][0] in symbols or
    tokens[pc][1] == "number" or
    tokens[pc][1] == "string" or
    tokens[pc][1] == "identifier"):
       
        if(tokens[pc][0] == ";"):
            pc+=1
            break;
        elif(tokens[pc][1] == "number" or tokens[pc][1] == "string"):
            stack.append(tokens[pc][0])
            pc+=1
        elif tokens[pc][1] == "identifier":
            if symbol_table[tokens[pc][0]][1] == "var":
                stack.append(symbol_table[tokens[pc][0]][0])
                pc+=1
            elif symbol_table[tokens[pc][0]][1] == "func":
                return_address_stack.append(pc)
                pc = symbol_table[tokens[pc][0]][0]
                block_pae()
                pc = return_address_stack.pop()+1
        else:
            symbol_pae()
       
def symbol_pae():
    global pc
    curtok = tokens[pc][0]

    #symbols = ['+','-','*','/','=','!','<','>','~','|','^','&']
    if(not (curtok == '!' or curtok == '~' or curtok == '.')):
        op2 = stack.pop()
        op1 = stack.pop()
       
        if(curtok == '+'):
            stack.append(op1+op2)
        elif(curtok == '-'):
            stack.append(op1-op2)
        elif(curtok == '*'):
            stack.append(op1*op2)
        elif(curtok == '/'):
            stack.append(op1/op2)
        elif(curtok == '='):
            stack.append(op1==op2)
        elif(curtok == '<'):
            stack.append(op1<op2)
        elif(curtok == '>'):
            stack.append(op1>op2)
        elif(curtok == '|'):
            stack.append(op1|op2)
        elif(curtok == '^'):
            stack.append(op1^op2)
        elif(curtok == '&'):
            stack.append(op1&op2)

    else:
        if(curtok == '!'):
            stack.append(not stack.pop())
        elif(curtok == "~"):
            stack.append(~ stack.pop())
        elif(curtok == "."):
            print(stack.pop(),end = "")
    pc+=1
def if_pae():
    match("if")
    expr_pae()
    if(stack.pop()):
        block_pae()
    else:
        skip_block()
def while_pae():
    global pc
    match("while")
    pc_buff = pc #holds the location of the current expr
    expr_pae()
   
    while stack.pop():
        block_pae()
        pc = pc_buff
        expr_pae()
    skip_block()

def for_pae():
    global pc
    match("for")
    name = tokens[pc+1][0]
    var_pae()
    symbol_table[name][0] -= 1 # starts for loop at certain index
    mutate_pc = pc
    mutate_pae()
    condition_pc = pc
    expr_pae()
    while stack.pop():
        block_pae()
        pc = mutate_pc
        mutate_pae()
        expr_pae()
    skip_block()
   
lexer()
program_pae()
#print(stack,symbol_table)
#print(tokens)
