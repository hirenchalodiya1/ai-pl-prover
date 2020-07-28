from pl_logic import PLLogicProblem
from operations import BinaryOperation, UnaryOperation


class FormulaParser(object):
    """
    Will store formula as a BinaryOperation or as a UnaryOperation or as a string
    """
    OPEN_PARENTHESIS = "("
    CLOSE_PARENTHESIS = ")"
    BINARY_OPERATORS = ["|", "&", ">", "="]
    UNARY_OPERATORS = ["!"]
    PRECEDENCE = {
        "!": 5,
        "&": 4,
        "|": 3,
        "=": 1,
        ">": 2
    }

    str_formula = None
    formula = None

    def __init__(self, formula):
        # first remove additional space from formula
        formula = "".join(formula.split())
        self.str_formula = formula

        postfix = self._convert_to_postfix(self.str_formula)
        self.formula = self._parse_postfix(postfix)

    # def _parse(self, string):
    #     # not useful as it does not consider precedence into considerations
    #     # this method is depreciated for subsequent use
    #
    #     # if string is empty then return None
    #     if len(string) == 0:
    #         return None
    #
    #     # if string has only one character then return string itself
    #     # eg. string is A, B like tokens
    #     if len(string) == 1:
    #         return string
    #
    #     # if first character is unary operator then make unary operation
    #     if string[0] in self.UNARY_OPERATORS:
    #         return UnaryOperation(string[0], self._parse(string[1:]))
    #
    #     # first character is parenthesis
    #     # multiple scenario eg. ()>(), ()=F
    #     if string[0] == self.OPEN_PARENTHESIS:
    #         strings = list()
    #         strings.append("")
    #         p_count = 0
    #         for char in string:
    #             if char is self.OPEN_PARENTHESIS:
    #                 p_count += 1
    #             if char is self.CLOSE_PARENTHESIS:
    #                 p_count -= 1
    #
    #             if not p_count and char in self.BINARY_OPERATORS:
    #                 # here binary operator is expected
    #                 strings.append(char)
    #                 strings.append("")
    #             else:
    #                 strings[-1] = f'{strings[-1]}{char}'
    #
    #         # scenario 1:
    #         # string object has only 1 object
    #         if len(strings) == 1:
    #             return self._parse(string[1:-1])
    #         elif len(strings) == 3:
    #             return BinaryOperation(strings[1], self._parse(strings[0]), self._parse(strings[2]))
    #         else:
    #             raise Exception("Parsing Error: Provide valid input")
    #
    #     # if first is character then two scenario
    #     # eg. E>F, E=()
    #     return BinaryOperation(string[1], self._parse(string[0]), self._parse(string[2:]))

    def _parse_postfix(self, postfix):
        stack = []
        for char in postfix:
            if char in self.UNARY_OPERATORS:
                left_operand = stack[-2]
                stack = stack[:-2]
                stack.append(UnaryOperation(char, left_operand))
            elif char in self.BINARY_OPERATORS:
                left_operand = stack[-2]
                right_operand = stack[-1]
                stack = stack[:-2]
                stack.append(BinaryOperation(char, left_operand, right_operand))
            else:
                stack.append(char)
        return stack[-1]

    def _convert_to_postfix(self, string):
        ret = ""
        stack = [None]
        for char in string:
            # If character is open parenthesis
            if char == self.OPEN_PARENTHESIS:
                stack.append(self.OPEN_PARENTHESIS)

            # Character is close parenthesis
            elif char == self.CLOSE_PARENTHESIS:
                while stack[-1] and stack[-1] != self.OPEN_PARENTHESIS:
                    c = stack.pop()
                    if c in self.UNARY_OPERATORS:
                        # add X as additional right operand
                        ret += f'X{c}'
                    else:
                        ret += c
                if stack[-1] == self.OPEN_PARENTHESIS:
                    _ = stack.pop()

            # Character is operator
            elif char in self.BINARY_OPERATORS or char in self.UNARY_OPERATORS:
                # <= condition maintains left to right associativity
                while stack[-1] and self.PRECEDENCE[char] <= self.PRECEDENCE.get(stack[-1], -1):
                    c = stack.pop()
                    if c in self.UNARY_OPERATORS:
                        # add X as additional right operand
                        ret += f'X{c}'
                    else:
                        ret += c
                stack.append(char)

            # Character is Symbol
            else:
                ret += char

        # apply rest of operator
        while stack[-1]:
            c = stack.pop()
            if c in self.UNARY_OPERATORS:
                # add X as additional right operand
                ret += f'X{c}'
            else:
                ret += c

        return ret

    def __repr__(self):
        return repr(self.formula) if type(self.formula) is not str else f"{self.formula}"

    def __str__(self):
        return str(self.formula)


class Parser(object):
    """
    Class to convert input into valid PL Logic problem
    """
    pl_logic_problem = None

    def __init__(self, problem):
        mode = int(problem[0].split()[1])
        formulas = problem[1:-1]
        query = problem[-1]

        knowledge_base = []

        for formula in formulas:
            parsed_formula = FormulaParser(formula)
            knowledge_base.append(parsed_formula)

        query = FormulaParser(query)
        self.pl_logic_problem = PLLogicProblem(knowledge_base, query, mode)

    def get_parsed_pl_problem(self):
        return self.pl_logic_problem
