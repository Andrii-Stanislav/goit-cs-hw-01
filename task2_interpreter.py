INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF = (
def term(self):
node = self.factor()
while self.current_token.type in (MUL, DIV):
token = self.current_token
if token.type == MUL:
self.eat(MUL)
else:
self.eat(DIV)
node = BinOp(node, token, self.factor())
return node


def expr(self):
node = self.term()
while self.current_token.type in (PLUS, MINUS):
token = self.current_token
if token.type == PLUS:
self.eat(PLUS)
else:
self.eat(MINUS)
node = BinOp(node, token, self.term())
return node


def parse(self):
node = self.expr()
if self.current_token.type != EOF:
raise Exception('Unexpected characters')
return node


class Interpreter:
def __init__(self, parser):
self.parser = parser


def visit(self, node):
method_name = 'visit_' + type(node).__name__
return getattr(self, method_name)(node)


def visit_Num(self, node):
return node.value


def visit_UnaryOp(self, node):
if node.op.type == PLUS:
return +self.visit(node.expr)
else:
return -self.visit(node.expr)


def visit_BinOp(self, node):
if node.op.type == PLUS:
return self.visit(node.left) + self.visit(node.right)
elif node.op.type == MINUS:
return self.visit(node.left) - self.visit(node.right)
elif node.op.type == MUL:
return self.visit(node.left) * self.visit(node.right)
elif node.op.type == DIV:
return self.visit(node.left) / self.visit(node.right)


def interpret(self):
tree = self.parser.parse()
return self.visit(tree)


if __name__ == '__main__':
while True:
try:
text = input('calc> ')
except (EOFError, KeyboardInterrupt):
break
if not text:
continue
lexer = Lexer(text)
parser = Parser(lexer)
interpreter = Interpreter(parser)
print(interpreter.interpret())