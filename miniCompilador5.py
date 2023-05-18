import re

class Variable:
    def __init__(self, nombre, tipo):
        self.nombre = nombre
        self.tipo = tipo

def quita_comentarios(archivoEnt, archivoSal):
    archivo = open(archivoEnt, "r")
    texto = []
    cad = ""
    for linea in archivo:
        for c in linea:
            texto.append(c)    
    archivo.close()
    estado = "z"
    for c in texto:
        if estado=="z" and c=="/":
            estado="a"
        elif estado =="z" and c!="/":
            cad = cad + c
        elif estado =="a" and c=="*":
            estado = "b"
        elif estado =="a" and c!="*":
            estado = "z"
            cad = cad + "/"            
        elif estado=="b" and c=="*":
            estado = "c"
        elif estado =="c" and c=="/":
            estado = "z"
        elif estado =="c" and c!="/":
            estado="b"        
    archivo = open(archivoSal, "w")
    archivo.write(cad)    
    return None

def es_simbolo_esp(caracter):
    return caracter in "+-*;,.:!=%&/()[]<><=>=:="

def es_separador(caracter):
    return caracter in " \n\t"

def es_entero(cad):
    valido = True
    for c in cad:
        if c not in "0123456789":
            valido = False
    return valido

def es_flotante(cad):
    a=[]
    if cad[0]!="." and cad[-1]!="." and cad.count(".")==1:
        a = cad.split(".")                
        if es_entero(a[0]) and es_entero(a[1]):
            return True
        else:
            return False
    return True

def es_id(cad):
    if cad[0] in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_":
        return True
    else:
        return False


def separa_tokens(archivo):
    tokens = []
    tokens2 = []
    archivo = open(archivo, "r")
    dentro = False    
    for linea in archivo:
        for l in linea:
            if es_simbolo_esp(l) and not(dentro):
                tokens.append(l)
            if (es_simbolo_esp(l) or es_separador(l)) and dentro:
                tokens.append(cad)
                dentro = False
                if es_simbolo_esp(l):
                    tokens.append(l)
            if not (es_simbolo_esp(l)) and not (es_separador(l)) and not(dentro):
                dentro = True
                cad=""
            if not (es_simbolo_esp(l)) and not (es_separador(l)) and dentro:
                cad = cad + l        
    archivo.close()
    compuesto = False
    for c in range(len(tokens)-1):
        if compuesto:
            compuesto = False
            continue
        if tokens[c] in ":<>!" and tokens[c+1]=="=":
            tokens2.append(tokens[c]+"=")
            compuesto = True
        else:
            tokens2.append(tokens[c])
    tokens2.append(tokens[-1])    
    for c in range(1,len(tokens2)-1):
        if tokens2[c]=="." and es_entero(tokens2[c-1]) and es_entero(tokens2[c+1]):
            tokens2[c]=tokens2[c-1]+tokens2[c]+tokens2[c+1]
            tokens2[c-1]="borrar"
            tokens2[c+1]="borrar"    
    porBorrar = tokens2.count("borrar")
    for c in range(porBorrar):
        tokens2.remove("borrar")
    return tokens2

def separa_tokens2(filename):
    # Leer el archivo y cargar su contenido en una cadena
    with open(filename, 'r') as f:
        contents = f.read()

    # Definir una expresión regular que capture los tokens de C
    token_regex = re.compile(r'''
        /\*.*?\*/|           # comentarios multilinea
        //[^\n]*|             # comentarios de una línea
        ".*?"|                # literales de cadena
        \d+\.\d+|\w+|         # números decimales y palabras
        !=|==|<=|>=|&&|\|\||   # operadores
        \+|\-|\*|/|%|         # operadores aritméticos
        =|,|;|\(|\)|\{|\}|\[|\] # símbolos especiales
    ''', re.DOTALL | re.VERBOSE)

    # Utilizar la expresión regular para dividir el contenido del archivo en tokens
    tokens = []
    for token in re.findall(token_regex, contents):
        if token.strip():
            tokens.append(token.strip())

    return tokens

def es_pal_res(token):
    return token in ["main","var","if","else","for","print","read","int","float","char","string", "function","return"]

def es_tipo(token):
    return token in ["int","float","char","string"]

def es_operador(token):
    return (token in ['+', '-', '*', '/', '^'])

def get_etiqueta(token):
    etiqueta = ""
    if es_id (token):
        if es_pal_res(token):
            if es_tipo(token):
                etiqueta = "tipo"
            else:
                etiqueta = "palres"
        else:
            etiqueta = "id"
    elif es_simbolo_esp(token):
        etiqueta = "simbolo"
    elif es_entero(token):
        etiqueta = "entero"
    elif es_flotante(token):
        etiqueta = "flotante"
    elif (token[0]=='"') and (token[0]==token[-1]):
        etiqueta = "cadena"
    else:
        etiqueta = "pendiente"
    return etiqueta

def imprime_tabla_tokens(tokens):    
    for t in tokens:
        print (t+ "\t" + get_etiqueta(t))        
        pass
    
def existe_var(v, tabla_var):
    existe = False
    for variable in tabla_var:
        if v == variable.nombre :
            existe = True
    return existe

def get_tipo(variables, id):
    encontrado = False
    for v in variables:
        if (v.nombre == id):
            encontrado = True
    return encontrado

def verifica_declara_var(tokens):
    '''
    si todo es correcto devuelve 0, de lo contrario devuelve un número que corresponde a un código de error
    '''
    tipo = ""       #semántico
    tabla_var = []  #semántico
    estado = "Z"    
    for t in tokens:
        if estado == "Z" and t=="var":
            estado = "A"
        elif (estado =="A"):
            if get_etiqueta(t)=="tipo":
                estado = "B"
                tipo = t  #parte del análisis semántico                
            else:
                print("error, se esperaba un tipo")
                return 1
        elif (estado =="B"):            
            if get_etiqueta(t)=="id":
                estado = "C"
                # ----------------------------------------
                # esto es parte del análisis semantico               
                if existe_var(t, tabla_var): #variable repetida
                    print("error, variable redeclarada:",t)
                    return 6
                else:
                    tabla_var.append(Variable(t, tipo))                   
                #-----------------------------------------
            else:
                print("error, se esperaba ID")
                return 2
        elif (estado =="C"):
            if(t==";"):
                estado = "D"
            elif (t==","):
                estado = "B"
            else:
                print('error, se esperaba ";"')
                return 3
        elif (estado =="D"):
            if (t=="main"):
                estado = "Z"
            elif(get_etiqueta(t)=="tipo"):
                estado = "B"
                tipo = t  #parte del análisis semántico
            else:
                print("Error, se esperaba tipo")
                return 4
    if estado == "Z": #todo es válido, se devuelve la tabla de variables
        return tabla_var
    else:
        return 5

def obtenerPrioridadOperador(o):
    # Función que trabaja con convertirInfijaA**.
    return {'(':1, ')':2, '+': 3, '-': 3, '*': 4, '/':4, '^':5}.get(o)

def infija2Posfija(infija):
    '''Convierte una expresión infija a una posfija, devolviendo una lista.'''    
    pila = []
    salida = []
    for e in infija:
        if e == '(':
            pila.append(e)
        elif e == ')':
            while pila[len(pila) - 1 ] != '(':
                salida.append(pila.pop())
            pila.pop()
        elif e in ['+', '-', '*', '/', '^']:
            while (len(pila) != 0) and (obtenerPrioridadOperador(e)) <= obtenerPrioridadOperador(pila[len(pila) - 1]):
                salida.append(pila.pop())
            pila.append(e)
        else:
            salida.append(e)
    while len(pila) != 0:
        salida.append(pila.pop())
    return salida

def hay_id(lista):
    '''
    devuelve verdadero si hay al menos un "id" en la lista
    '''
    existe = False
    for e in lista:
        if get_etiqueta(e)=='id':
            existe = True
    return existe

def posfija_a_intermedio(posfija):
    '''
    recibe una expresión posfija, la convierte en código intermedio
    '''
    intermedio = []
    codigo = []
    pila = []
    temp = 1
    for e in posfija:                
        if e in ['+','-','*','+']:
            op2 = pila.pop()
            op1 = pila.pop()
            intermedio.append('t'+str(temp).zfill(2)+"="+op1+e+op2)
            codigo.append('LDA '+op1+';')
            if e=="+":
                codigo.append('ADD '+op2+';')
            if e=="-":
                codigo.append('SUB '+op2+';')
            if e=="*":
                codigo.append('MUL '+op2+';')
            if e=="/":
                codigo.append('SUB '+op2+';')
            codigo.append('STA '+'t'+str(temp).zfill(2)+';')
            pila.append('t'+str(temp).zfill(2))
            temp += 1            
        else:
            pila.append(e)
    if (len(pila)==1): #solo debe quedar un elemento en la pila
        return intermedio, codigo
    else:
        print('expresión no válida')
        print(posfija)
        print(codigo)
        return None
    

def evalua_posfija(posfija):
    pila = []
    for e in posfija:        
        if get_etiqueta(e)=='entero':
            pila.append(int(e))
        elif get_etiqueta(e)=='flotante':
            pila.append(float(e))
        elif e in ['+','-','*','+']:
            op2 = pila.pop()
            op1 = pila.pop()
            if e=='+':
                pila.append(op1+op2)
            elif e=='-':
                pila.append(op1-op2)
            elif e=='*':
                pila.append(op1*op2)
            elif e=='/':
                pila.append(op1/op2)
            else:
                print(error)
                return None
    if (len(pila)==1): #solo debe quedar un elemento en la pila
        return pila[0]
    else:
        print('expresión no válida')
        return None

# Aqui inicia el proceso de compilación
quita_comentarios("uno.txt", "dos.txt")  # se quitan los comentario
tokens = separa_tokens2("dos.txt")        # se separa en tokens
#imprime_tabla_tokens(tokens)
variables = verifica_declara_var(tokens) # se validan que las variables sean correctas
if isinstance(variables, list):          # si devuelve una lista de variables es correcto
    print("variables válidas")           # si devuelve un número es un código de error
else:
    print("variables NO válidas")
pos = tokens.index('main')              # encontramos en que posición esta 'main'
tokens = tokens[pos+4:]                 # borramos todo lo que está antes del main (variables)
estado = 'Z'                            # estamos fuera de todo
codigo = []
expresion = []
for t in tokens:           # revisión de todos los tokens   
    if estado == 'Z':
        if t=='print':
            estado = 'A'
        elif (get_etiqueta(t)=='id'):
            estado = 'B'
            varCall = t
            expresion.append(t)
        elif (t== 'function'):
            estado = 'E'
        elif t == 'return':
            estado = 'E5'
    elif estado == 'A':   #estamos dentro de un print
        #print("Estoy dentro de un print!!!")
        if t=='(':
            estado = 'A1'
        else:
            print('error! se esperaba "("')
    elif estado == 'A1':
        #print("A ver si aqui esta el problema???")
        etiqueta = get_etiqueta(t)  #checamos si el print tiene variable o cadena
        if etiqueta == 'entero':          
            codigo.append('INT9 '+ t +';')
        elif etiqueta == 'flotante':          
            codigo.append('INT9 '+ t +';')
        elif etiqueta == 'cadena':
            codigo.append('INT9 '+ t +';')
        elif etiqueta == 'id':      #es una variable y tenemos que ver de que tipo
            tipo = get_tipo(variables, t)
            if tipo == 'entero':
                codigo.append('INT5 '+ t +';')
            elif tipo == 'float':
                codigo.append('INT6 '+ t +';')
        estado = 'A2'
    elif estado == 'A2':
        if t == ')':
            estado = 'A3'
        else:
            print('error!!, se esperaba ")"')
    elif estado == 'A3':
        if t == ';':
            estado = "Z"  #terminó bien el print
            
    elif estado == 'B':   #empezó con un ID
        if t=='=':        #es una asignación
            estado = 'B1'
            expresion.append('=')
        else:
            print('error!, se esperaba "="')
    elif estado == 'B1':
        if get_etiqueta(t)=='entero':
            codigo.append('LDV '+ t +';')
            codigo.append('STA '+expresion[0]+';')
            estado = 'B2'
        elif get_etiqueta(t)=='flotante':
            codigo.append('LDV '+ t +';')
            codigo.append('STA '+expresion[0]+';')
            estado = 'B2'
        elif get_etiqueta(t)=='id':
            if t == nombreFuncion:
                estado = 'E6'
            else:
                estado = 'B3'            
                expresion.append(t)
    elif estado == 'B2':
        if t==';':
            estado = 'Z'   #terminó bien la asignacion de la expresión            
            expresion = []
            
        else:
            print('error!, se esperaba ";"')
    elif estado == 'B3':
        if es_operador(t):
            estado='B4'
            expresion.append(t)
        elif (t==';'):            
            posfija = infija2Posfija(expresion[2:])
            cod_intermedio, cod = posfija_a_intermedio(posfija)
            codigo = codigo + cod
            expresion = []
            estado = 'Z'
    elif estado =='B4':
        if get_etiqueta(t)=='id':
            expresion.append(t)
            estado = 'B3'
    elif estado == 'E':
        #print("ESTOY EN EL ESTADO E!!!! TODO BIEN HASTA AQUI")
        if get_etiqueta(t) == 'id':
            nombreFuncion = t
            codigo.append('#'+t)
            estado = 'E1'
    elif estado == 'E1':
        #print("ESTOY EN EL ESTADO E1!!!! TODO BIEN HASTA AQUI")
        if t=='(':
            estado = 'E2'
        else:
            print('error! se esperaba "("')
    elif estado == 'E2':
        #print("ESTOY EN EL ESTADO E2!!!! TODO BIEN HASTA AQUI")
        argumento = t
        estado = 'E3'
    elif estado == 'E3':
        #print("ESTOY EN EL ESTADO E3!!!! TODO BIEN HASTA AQUI")
        if t == ')':
            estado = 'E4'
        else:
            print('error! se esperaba ")"')
    elif estado == 'E4':
        #print("ESTOY EN EL ESTADO E4!!!! TODO BIEN HASTA AQUI")
        if t=='{':
            estado = 'Z'
        else:
            print('error! se esperaba "{"')
    elif estado == 'E5':
        #print("ESTOY EN EL ESTADO E5!!!! TODO BIEN HASTA AQUI")
        if get_etiqueta(t) == 'id':
            asignacion = t
            codigo.pop()
            codigo.append('STA '+asignacion+';')
            codigo.append('LDA '+asignacion+';')
            
            pilatemp = []
            busqueda = codigo.index('LDA ' + argumento+';')
            while len(codigo) != busqueda:
                pilatemp.append(codigo.pop())
            pilatemp.pop()
            while len(pilatemp) != 0:
                codigo.append(pilatemp.pop())
            
            codigo.append('RET')
            estado = 'Z'
        else:
            print("Error! se esperaba '}'")
    elif estado == 'E6':
        #print("ESTOY EN EL ESTADO E6!!!! TODO BIEN HASTA AQUI")
        if t=='(':
            estado = 'E7'
        else:
            print('error! se esperaba "("')
    elif estado == 'E7':
        #print("ESTOY EN EL ESTADO E7!!!! TODO BIEN HASTA AQUI")
        codigo.append('LDA '+t+';')
        codigo.append('CALL #'+nombreFuncion)
        codigo.append('STA '+ varCall + ';')
        estado = 'E8'
    elif estado == 'E8':
       # print("ESTOY EN EL ESTADO E8!!!! TODO BIEN HASTA AQUI")
        if t == ')':
            estado = 'Z'
        else:
            print('error! se esperaba ")"')
        
        
if estado=='Z':  #toda la compilación fue correcta
    print(codigo)
else:
    print("errores en la compilación")
