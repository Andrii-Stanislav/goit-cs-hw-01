# ===== file: task2_interpreter.py =====
"""
Завдання 2 — інтерпретатор арифметичних виразів.
Підтримує: +, -, *, /, дужки (), унарні + та -.
Ділення за замовчуванням — звичайне (float).

Граматика (ліва асоціативність):
    expr   : term ((PLUS | MINUS) term)*
    term   : factor ((MUL  | DIV)  factor)*
    factor : (PLUS | MINUS) factor | INTEGER | LPAREN expr RPAREN

Ролі:
- factor відповідає за числа, дужки і унарні знаки.
- term   обробляє * та /.
- expr   обробляє + та -.
"""

from dataclasses import dataclass
from typing import Optional

# --- Типи токенів ---
INTEGER, PLUS, MINUS, MUL, DIV, LPAREN, RPAREN, EOF = (
    "INTEGER", "PLUS", "MINUS", "MUL", "DIV", "LPAREN", "RPAREN", "EOF"
)

# --- Оголошення токена ---
@dataclass
class Token:
    type: str
    value: Optional[int]

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value!r})"


# --- Лексер ---
class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.current_char = text[self.pos] if text else None

    def advance(self) -> None:
        """Зсунути поточну позицію вперед на 1 символ."""
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self) -> None:
        """Пропустити пробіли/переноси рядків."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self) -> int:
        """Зібрати послідовність цифр у ціле число."""
        digits = []
        while self.current_char is not None and self.current_char.isdigit():
            digits.append(self.current_char)
            self.advance()
        return int("".join(digits))

    def get_next_token(self) -> Token:
        """Лексичний аналіз: повертати наступний токен зі вхідного рядка."""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            ch = self.current_char

            if ch.isdigit():
                return Token(INTEGER, self.integer())
            if ch == "+":
                self.advance()
                return Token(PLUS, "+")
            if ch == "-":
                self.advance()
                return Token(MINUS, "-")
            if ch == "*":
                self.advance()
                return Token(MUL, "*")
            if ch == "/":
                self.advance()
                return Token(DIV, "/")
            if ch == "(":
                self.advance()
                return Token(LPAREN, "(")
            if ch == ")":
                self.advance()
                return Token(RPAREN, ")")

            # Невідомий символ
            raise SyntaxError(f"Invalid character: {ch!r}")

        return Token(EOF, None)


# --- Вузли AST ---
class AST:
    pass


class Num(AST):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.value


class BinOp(AST):
    def __init__(self, left: AST, op: Token, right: AST) -> None:
        self.left = left
        self.op = op
        self.right = right


class UnaryOp(AST):
    def __init__(self, op: Token, expr: AST) -> None:
        self.op = op
        self.expr = expr


# --- Парсер ---
class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = lexer.get_next_token()

    def eat(self, token_type: str) -> None:
        """Спожити поточний токен, якщо тип очікуваний, і перейти до наступного."""
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            raise SyntaxError(
                f"Expected {token_type}, got {self.current_token.type}"
            )

    def factor(self) -> AST:
        """
        factor : (PLUS | MINUS) factor
               | INTEGER
               | LPAREN expr RPAREN
        """
        token = self.current_token

        # Унарні +/-
        if token.type in (PLUS, MINUS):
            self.eat(token.type)
            return UnaryOp(token, self.factor())

        # Число
        if token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)

        # Дужки
        if token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

        raise SyntaxError("Invalid syntax in factor")

    def term(self) -> AST:
        """
        term : factor ((MUL | DIV) factor)*
        """
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            else:
                self.eat(DIV)
            node = BinOp(node, token, self.factor())

        return node

    def expr(self) -> AST:
        """
        expr : term ((PLUS | MINUS) term)*
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            else:
                self.eat(MINUS)
            node = BinOp(node, token, self.term())

        return node

    def parse(self) -> AST:
        """Побудова AST для всього виразу."""
        node = self.expr()
        if self.current_token.type != EOF:
            raise SyntaxError("Unexpected characters after expression")
        return node


# --- Відвідувач/Інтерпретатор ---
class NodeVisitor:
    def visit(self, node: AST):
        method = getattr(self, "visit_" + type(node).__name__)
        return method(node)


class Interpreter(NodeVisitor):
    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def visit_Num(self, node: Num):
        return node.value

    def visit_UnaryOp(self, node: UnaryOp):
        value = self.visit(node.expr)
        return +value if node.op.type == PLUS else -value

    def visit_BinOp(self, node: BinOp):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        if node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        if node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        if node.op.type == DIV:
            right = self.visit(node.right)
            if right == 0:
                raise ZeroDivisionError("division by zero")
            return self.visit(node.left) / right
        raise RuntimeError("Unknown operator")

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


# --- Точка входу (REPL) ---
if __name__ == "__main__":
    while True:
        try:
            text = input("calc> ")
        except (EOFError, KeyboardInterrupt):
            print()  # гарне завершення рядком
            break

        if not text or not text.strip():
            continue

        try:
            lexer = Lexer(text)
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            result = interpreter.interpret()
            print(result)
        except ZeroDivisionError as e:
            print(f"Error: {e}")
        except SyntaxError as e:
            print(f"SyntaxError: {e}")
