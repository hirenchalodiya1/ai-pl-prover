class Operand(object):
    value = None

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if type(other) is not Operand:
            return False
        return self.value == other.value

    def __len__(self):
        return 1

    def eliminate_iff(self):
        pass

    def eliminate_implication(self):
        pass

    def parse_not(self):
        # Return itself
        return self

    def propagate_not(self):
        # Return negation of itself, no need to parse further because it will create loop
        return UnaryOperation("!", self)

    def parse_or_and(self):
        # Return itself
        return self


class UnaryOperation(object):
    operator = None
    operand = None

    def __init__(self, operator, operand):
        self.operator = operator
        self.operand = operand

    def __str__(self):
        o = str(self.operand)

        if len(o) > 1:
            return f"{self.operator}({o})"
        return f"{self.operator}{o}"

    def __repr__(self):
        if type(self.operand) is Operand:
            return f"{self.operator}{repr(self.operand)}"
        return f'[Unary: {self.operator}, {repr(self.operand)}]'

    def __eq__(self, other):
        if type(other) is not UnaryOperation:
            return False
        return self.operator == other.operator and self.operand == other.operand

    def __len__(self):
        if self.operand in [BinaryOperation, UnaryOperation]:
            return 1 + len(self.operand)
        return 1

    def eliminate_iff(self):
        # pass to operand
        self.operand.eliminate_iff()

    def eliminate_implication(self):
        # pass to operand
        self.operand.eliminate_implication()

    def parse_not(self):
        # if operator is NOT then propagate to operand
        if self.operator == "!":
            return self.operand.propagate_not()

        # otherwise parse operand and return self
        self.operand = self.operand.parse_not()
        return self

    def propagate_not(self):
        # case !(!A) = A, return operand with further parsing
        if self.operator == "!":
            return self.operand.parse_not()

        # do nothing
        return self

    def parse_or_and(self):
        # case !A return !A
        if type(self.operand) is Operand:
            return self

        # parse NOT first on operand and then check OR AND
        self.operand = self.operand.parse_not().parse_or_and()
        return self


class BinaryOperation(object):
    operator = None
    left_operand = None
    right_operand = None

    def __init__(self, operator, left_operand, right_operand):
        self.operator = operator
        self.left_operand = left_operand
        self.right_operand = right_operand

    def __str__(self):
        lo = str(self.left_operand)
        ro = str(self.right_operand)
        o = self.operator

        ret = ""
        ret += f'({lo})' if len(lo) > 2 else f'{lo}'
        ret += f'{o}'
        ret += f'({ro})' if len(ro) > 2 else f'{ro}'
        return ret

    def __repr__(self):
        lo = self.left_operand
        ro = self.right_operand
        o = self.operator
        return f'[Binary: {o}, {repr(lo)}, {repr(ro)}]'

    def __eq__(self, other):
        if type(other) is not BinaryOperation:
            return False

        if self.operator == other.operator:
            if self.operator in ["&", "|"]:
                _l = self.left_operand
                _r = self.right_operand
                _ol = other.left_operand
                _or = other.right_operand
                return (_l == _ol and _r == _or) or (_l == _or and _r == _ol)

            elif self.left_operand == other.left_operand and self.right_operand == other.right_operand:
                return True
        return False

    def __len__(self):
        return len(self.left_operand) + len(self.right_operand)

    def eliminate_iff(self):
        # Eliminate iff from right left operand first
        self.left_operand.eliminate_iff()
        self.right_operand.eliminate_iff()

        # replace A=B to (A>B)&(B>A)
        if self.operator == "=":
            self.operator = "&"
            lo = self.left_operand
            ro = self.right_operand
            self.left_operand = BinaryOperation(">", lo, ro)
            self.right_operand = BinaryOperation(">", ro, lo)

    def eliminate_implication(self):
        # Eliminate implication from left right operand first
        self.left_operand.eliminate_implication()
        self.right_operand.eliminate_implication()

        # replace A>B to !A|B
        if self.operator == ">":
            self.operator = "|"
            self.left_operand = UnaryOperation("!", self.left_operand)

    def parse_not(self):
        # parse not in left and right operand
        self.left_operand = self.left_operand.parse_not()
        self.right_operand = self.right_operand.parse_not()
        # return it self
        return self

    def propagate_not(self):
        # This function is only implemented for AND OR operator
        propagate_to_left_right = self.operator in ["|", "&"]  # check OR AND operator

        operator, lo, ro = None, None, None

        # case !(A&B) --- !A|!B
        if self.operator == "&":
            operator = "|"
        # case !(A|B) --- !A&!B
        if self.operator == "|":
            operator = "&"

        if propagate_to_left_right:
            # propagate NOT to left right operand
            lo = self.left_operand.propagate_not().parse_not()
            ro = self.right_operand.propagate_not().parse_not()
            return BinaryOperation(operator, lo, ro)
        else:
            # do nothing
            return self

    def parse_or_and(self):
        # parse OR AND in left operand
        self.left_operand = self.left_operand.parse_or_and()
        # parse OR AND in right operand
        self.right_operand = self.right_operand.parse_or_and()

        # if operator is OR then only we need to check
        if self.operator == "|":
            left_end = type(self.left_operand) == BinaryOperation and self.left_operand.operator == "&"
            right_end = type(self.right_operand) == BinaryOperation and self.right_operand.operator == "&"

            # case (A&B)|(C&D) --- (A|C)&(A|D)&(B|C)&(B|D)
            if left_end & right_end:
                # first left
                fl = self.left_operand.left_operand
                # first right
                fr = self.left_operand.right_operand
                # second left
                sl = self.right_operand.left_operand
                # second right
                sr = self.right_operand.right_operand

                # prepare left operand
                new_fl = BinaryOperation("|", fl, sl).parse_or_and()
                new_fr = BinaryOperation("|", fl, sr).parse_or_and()
                new_left = BinaryOperation("&", new_fl, new_fr)

                # prepare right operand
                new_sl = BinaryOperation("|", fr, sl).parse_or_and()
                new_sr = BinaryOperation("|", fr, sr).parse_or_and()
                new_right = BinaryOperation("&", new_sl, new_sr)

                return BinaryOperation("&", new_left, new_right).parse_or_and()

            # case (A&B)|C --- (A|C)&(B|C)
            elif left_end:
                # first left
                fl = self.left_operand.left_operand
                # first right
                fr = self.left_operand.right_operand
                # second operand
                s = self.right_operand

                new_left = BinaryOperation("|", fl, s).parse_or_and()
                new_right = BinaryOperation("|", fr, s).parse_or_and()
                return BinaryOperation("&", new_left, new_right).parse_or_and()

            # case A&(B|C) --- (A|B)&(A|C)
            elif right_end:
                # first
                f = self.left_operand
                # second left
                sl = self.right_operand.left_operand
                # second right
                sr = self.right_operand.right_operand

                new_left = BinaryOperation("|", f, sl).parse_or_and()
                new_right = BinaryOperation("|", f, sr).parse_or_and()
                return BinaryOperation("&", new_left, new_right).parse_or_and()

        # if operator is not OR then return itself
        return self

    def optimize_v1(self):
        # method is deprecated as it's improved version exists

        # This method is only written for OR Operation
        if not self.operator == "|":
            return self

        if type(self.left_operand) is BinaryOperation:
            self.left_operand = self.left_operand.optimize()

        if type(self.right_operand) is BinaryOperation:
            self.right_operand = self.right_operand.optimize()

        if not self.left_operand and not self.right_operand:
            return None

        if not self.left_operand:
            return self.right_operand

        if not self.right_operand:
            return self.left_operand

        # A OR A = A
        if self.left_operand == self.right_operand:
            return self.left_operand

        # (A OR B) OR A = A OR B
        if type(self.left_operand) is BinaryOperation and type(self.right_operand) is not BinaryOperation:
            ll = self.left_operand.left_operand
            lr = self.left_operand.right_operand
            r = self.right_operand

            if ll == r or lr == r:
                return self.left_operand

        # A OR (A OR B) = (A OR B)
        if type(self.right_operand) is BinaryOperation and type(self.left_operand) is not BinaryOperation:
            _l = self.left_operand
            rl = self.right_operand.left_operand
            rr = self.right_operand.right_operand

            if _l == rl or _l == rr:
                return self.right_operand

        # A OR !A = True -> ignore this
        if self.left_operand == UnaryOperation("!", self.right_operand).parse_not():
            return None

        return self

    def optimize(self):
        # this function is defined only for OR function
        if self.operator != "|":
            return self

        # segregate everything by OR
        literals = self.segregate("|")

        # store all unique literals
        literal_set = list()

        # loop over all literals
        for literal in literals:
            # if negation of literal exists then no need to include it in set
            if UnaryOperation("!", literal).parse_not() not in literals:

                # if literal is being repeated then no need to repeat
                if literal not in literal_set:
                    literal_set.append(literal)

        def create_clause_with_given_symbol(arr, symbol):
            if len(arr) == 0:
                return None

            if len(arr) == 1:
                return arr[0]

            if len(arr) == 2:
                return BinaryOperation(symbol, arr[0], arr[1])

            if len(arr) % 2 == 0:
                m = len(arr) // 2
            else:
                m = (len(arr) // 2) + 1

            return BinaryOperation(symbol, create_clause_with_given_symbol(arr[:m], symbol),
                                   create_clause_with_given_symbol(arr[m:], symbol))

        return create_clause_with_given_symbol(literal_set, "|")

    def segregate(self, symbol):
        if self.operator == symbol:
            ret = []
            if type(self.left_operand) is BinaryOperation:
                ret += self.left_operand.segregate(symbol)
            else:
                ret += [self.left_operand]

            if type(self.right_operand) is BinaryOperation:
                ret += self.right_operand.segregate(symbol)
            else:
                ret += [self.right_operand]

            return ret

        else:
            return [self]
