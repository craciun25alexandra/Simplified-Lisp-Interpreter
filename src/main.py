from sys import argv
from .Lexer import Lexer

# transforma un string ce contine mai multe lambda in elemente distincte
def parser_param(param):
	lambdas = param.split(':')
	return_list = []
	for i in lambdas:
		return_list.append(i)
		if i != lambdas[-1]:
			return_list.append(':')
	return return_list

# imparte stringul in tokens
def make_tokens(program):
	spec = [
		('DouaPuncte', r':'),
		('INT', r'[0-9]+'),
		('WHITE_SPACE', r'\ '),
		('VID', r'\(\)'),
		('CONCAT', r'\+\+'),
		('SUM', r'\+'),
		('LAMBDA', r'lambda\ [a-z]+'),
		('VARIABLE', r'[a-z]+'),
		('START', r'\('),
		('END', r'\)'),
	]
	lexer = Lexer(spec)
	return lexer.lex(program)

# numara cate paranteze deschise se afla inainte de lambda pentru a putea lua intregul argument al lui
def number_paran_before_lambda(tokens):
	
	for i in range(len(tokens)):
		if tokens[i][0] == 'LAMBDA':
			break
	nr = 0
	i -= 1
	while(i >= 0):
		if tokens[i][0] == 'START':
			nr += 1
		else:
			break
		i -= 1
	return nr

def parse_tokens(tokens, rest_params, old_operators, new_tokens):
	
	stack = []
	# in cazul reapelarii functiei, sa nu se piarda tokenurile
	tokens = new_tokens + tokens
	# nr de paranteze inaitnea primul lambda inainte sa se taie din ele
	start_before_lambda = number_paran_before_lambda(tokens)
	# idem pt operatori
	operators = old_operators
	# (caz intalnit la reapelare dupa calculul lambda), daca e un singur token, se afiseaza
	# si se termina programul
	if len(tokens) == 1:
		print(tokens[0][1])
		return 0
	token = tokens.pop(0)
	while tokens:
		if token[0] == 'START':
			list_aux = []
			token = tokens.pop(0)
			nr_brackets = 0
			# daca este o lista de elemente
			if token[0] == 'INT' or token[0] == 'VID' or token[0] == 'WHITE_SPACE':
				# se pune in stiva intreaga lista, anume cand nr de '(' este egal cu nr de ')'
				# contorizandu se
				while nr_brackets > -1 and len(tokens) > 0:
					if token[0] == 'VID' or token[0] == 'INT':
						list_aux.append(token[1])
					else:
						if token[0] == 'START':
							nr_brackets += 1
							list_aux.append(token[1])
						elif token[0] == 'END':
							nr_brackets -= 1
							# cea care marcheaza sfarsitul trebuie ignorata
							if (nr_brackets > -1):
								list_aux.append(token[1])
					token = tokens.pop(0)
			# daca a fost o lista de elemente se adauga in stack
			if(len(list_aux) > 0):
				stack.append(list_aux)
			# daca nu, se adauga ca operator
			else:
				operators.append("(")
		# se adauga operatorii
		elif token[0] == 'SUM' or token[0] == 'CONCAT':
			operators.append(token[1])
			token = tokens.pop(0)
		# se adauga elementele
		elif token[0] == 'INT' or token[0] == 'VID':
			stack.append(token[1])
			token = tokens.pop(0)
		elif token[0] == 'END':
			list2 = []
			sum = 0
			# daca am dat de un end != de cele care marcheaza sf unei liste si ultimul operator
			# este != de '(', adica sfarsitul este sfarsitul operatorului => se executa
			if len(operators) > 0:
				if operators[-1] == '++':
					for i in stack.pop():
						list2.append(i)
					stack.append(list2)
					operators.pop()
				elif operators[-1] == '+':
					for i in stack.pop():
						if i <= '9' and i >= '0':
							sum += int(i)
					stack.append(str(sum))
					operators.pop()
			token = tokens.pop(0)
		elif token[0] == 'LAMBDA':
			list_aux = []
			list_aux.append(token[1])
			end_after_lambda = start_before_lambda
			# va pune in list aux tot argumentul lambdei; id + expresie
			while(end_after_lambda > 0):
				token = tokens.pop(0)
				if token[0] == 'START':
					end_after_lambda += 1
				elif token[0] == 'END':
					end_after_lambda -= 1
				list_aux.append(token[1])
			# se va calcula lambda, se vor da si vechii operatori si tokenii ramasi pentru a se 
			# continua evaluarea intregii expresii dupa ce se va calcula lambda (tokenii + op se unesc
			# la inceput) si se va da return ca acest apel de functie sa se termine
			calculate_lambda(list_aux, rest_params, operators, tokens)
			return
		else:
			token = tokens.pop(0)
	# dupa ce s a creat stiva, ar trebui sa mai existe max un operator final, si se apeleaza finalize care
	# compune rez final
	finalize (stack, operators)
# functie care returneaza pozitiile la care trebuie inlocuit id ul cu valoarea, sau -1 daca in expresia ce era
# legata de acel lambda nu exista id ul de inlocuit
def is_doable(id, body):
	i = 0
	nr_lambda = 0
	nr_ids = 0
	positions = []
	# ultimul caracter din "lambda: x"
	var = id [len(id)-1]
	while(i < len(body)):
		if (body[i] == id):
			# daca se mai gaseste acelasi lambda cu acelasi argument, se sare dupa ':'
			i += 2
			# daca in expresia lui exista id ul vechiului, var ul este al lambda ului gasit, nu al celui dat,
			# deci nu se ia in considerare
			if body[i] == var:
				nr_lambda += 1
				nr_ids += 1
			# daca are ca expresie o lista, se cauta in lista var
			elif body[i] == '(':
				ok = 0
				while(body[i] != ')'):
					if body[i] == var:
						ok = 1
					i += 1
				if (ok):
					nr_lambda += 1
					nr_ids += 1
		# daca se gaseste o lista fara un lambda precedent
		elif body[i] == '(':
			ok = 0
			pos_aux = []
			# se cauta in lista resp var si se retin pozitiile in care apare
			while(body[i] != ')'):
				if body[i] == var:
					ok = 1
					pos_aux.append(i)
				i += 1
			if (ok):
				nr_ids += 1
				positions.append([nr_ids, pos_aux])
		# daca apare simplu
		elif body[i] == var:
			nr_ids += 1
			positions.append([nr_ids, i])
		i += 1
	# daca nr de lambda aparute == nr de var prezente, ele nu tin de lambda ul inspectat si se returneaza -1
	if nr_lambda == nr_ids:
		return -1
	# daca nu exista niciun lambda precedent, se returneaza positiile var gasite
	elif nr_lambda == 0:
		return positions
	else:
	# daca au existat lambda uri, se returneaza cel mai din coada, care apartine lambda ului cautat
		return positions[nr_lambda]
		

def calculate_lambda(list_given, rest_params, old_operators, tokens):
	param = []
	body = []
	i = 0
	#print(list_given)
	# parseaza lambda, pastrand in body expresia
	while i < len(list_given):
		if list_given[i] == ':':
			body.append(list_given[i])
			# daca gaseste un inceput de lista in expresie
			if list_given[i+1] == '(':
				body.append(list_given[i+1])
				i += 2
				nr_parant = 1
				# copiaza in body tot argumenteul, pana se inchide paranteza deschisa
				while nr_parant > 0:
					if list_given[i] == '(':
						nr_parant += 1
					elif list_given[i] == ')':
						nr_parant -= 1
					body.append(list_given[i])
					i += 1
				break
			# daca are ca expresie un nou lambda, trece la el
			elif list_given[i+1].startswith('lambda'):
				i += 1
			# daca are ca expresie un parametru
			else:
				body.append(list_given[i+1])
				i += 2
				break
		# lambda uri
		else:
			body.append(list_given[i])
			i += 1
	
	element = ''
	# baga parametrii
	while(i < len(list_given)):
		# incepe o lista
		if(list_given[i] == '('):
			# baga intreaga paranteza
			while(list_given[i] != ')'):
				element += list_given[i]
				i += 1
			element += list_given[i]
		# s a terminat un parametru; se adauga 
		if(list_given[i] == ')'):
			if element != '':
				param.append(element)
			element = ''
		# daca e un singur parametru
		elif(list_given[i] == ' ' and element == '' and (len(list_given)> i+2 and list_given[i+2] in {' ', ')'})):
			param.append(list_given[i+1])
			i += 1
		# pentru lambda uri, expresile lor, etc
		else:
			if list_given[i] not in {' ', ')', '('}:
				element += list_given[i]
		i += 1
		
	# se adauga vechii parametrii daca acestia existau (reapel de lambda)
	if rest_params != None:
		for i in rest_params:
			param.append(i)
	# se sterge ')' separatoare din sintaxa parametrilor din lambda; deja stiu ordinea
	param = [i for i in param if i != ')']
	i = 0
	# cat timp exista un lambda care trebuie rezolvat
	while(body[i].startswith('lambda')):
		element = body.pop(0)
		# daca se poate inlocui in expresie
		if is_doable(element, body) != -1:
			index = is_doable(element, body)
			# se ia primul param adaugat
			changer = param.pop(0)
			for k in range(len(index)):
				# se modifica in toate aparitiile
				if isinstance(index[k][1], list):
					for j in index[k][1]:
						body[j] = changer			
				else:
					body[index[k][1]] = changer
			body.pop(0)
			for m, word in enumerate(body):
				# daca am adaugat un parametru care e de fapt alta expresie lambda, il voi desparti
				# pe elemente
				if word.startswith('lambda') and len(word)> 8:
					body.pop(m)
					body[m:m] = parser_param(word)
		# daca nu se poate inlocui se sare peste lambda si peste parametrul cu care trebuia inlocuit
		else:
			body.pop(0)
			param.pop(0)
	# la finalul calculului, reapeleaza functia de parse pt a continua procesul
	new_text = "".join(body)
	parse_tokens(tokens, param, old_operators, make_tokens(new_text))

def print_concat(stack):
	
	rez = "( "
	aux_list = []
	stack = [i for i in stack if i != '()' and i != '(' and i != ')']
	
	while len(stack) > 0:
		aux = ""
		element = stack.pop()
		if isinstance(element, str):
			aux += element + " "
		else:
			for i in element:
				if i != '(' and i != ')':
					aux += i + " "
		aux_list.append(aux)

	aux_list = aux_list[::-1]

	for i in aux_list:
		rez += i

	rez += ")"
	print(rez)

def print_listing(stack):
	add_paran = 0
	if len(stack) == 1:
		rez = ""
	else:
		add_paran = 1
		rez = "( "
	while(len(stack) > 0):

		element = stack.pop(0)
		if isinstance(element, str):
			rez += element + " "	
		else:
			rez += "( "
			for i in element:
				rez += i + " "
			rez += ") "
	if add_paran:
		rez += ")"
	else:
		# se scoate spatiul de la final; el era despartitor pt elemente
		# daca e un singur element nu trebuie pus
		rez = rez[:-1]
	print(rez)

def print_sum(stack):
	sum = 0
	while(len(stack) > 0):
		element = stack.pop()
		if isinstance(element, str):
			sum += int(element)
		else:
			for i in element:
				if i <= '9' and i >= '0':
					sum += int(i)
	print(sum)

def finalize(stack, operators):
	# ne intereseaza doar operatiile
	operators = [i for i in operators if i != '(']
	# nu mai e operatie de facut, deci se listeaza elementele din stack
	if len(operators) == 0:
			print_listing(stack)
	else:
		if operators[0] == '++':
			print_concat(stack)
		elif operators[0] == '+':
			print_sum(stack)


def main():
	if len(argv) != 2:
		return
	
	filename = argv[1]
	with open(filename, 'r') as f:
		program = f.read()
		# sterge 2 spatii consecutive
		program = ' '.join(program.split())
		# sterge \n
		program = program.replace('\n', '')
	# exceptii de parsare
	program = program.replace("( +", "(+")
	program = program.replace("( ++", "(++")
	program = program.replace("( ", "(")
	program = program.replace(": ", ":")
	tokens = make_tokens(program)

	parse_tokens(tokens, None, [], [])
     
if __name__ == '__main__':
	main()
