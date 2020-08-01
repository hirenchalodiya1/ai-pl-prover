from operations import BinaryOperation, UnaryOperation


class Knowledge(object):
    formula = None

    def __init__(self, formula, by_formula=False):
        if not by_formula:
            self.formula = formula.formula
        else:
            self.formula = formula

    def __repr__(self):
        return repr(self.formula)

    def __str__(self):
        return str(self.formula)

    def convert_to_cnf(self):
        self._eliminate_iff_and_implication()
        self._parse_not()
        self._parse_or_and()

    def _eliminate_iff_and_implication(self):
        self.formula.eliminate_iff()
        self.formula.eliminate_implication()

        # to be safe side
        self.formula.eliminate_iff()
        self.formula.eliminate_implication()

    def _parse_not(self):
        self.formula = self.formula.parse_not()
        # to be safe side
        self.formula = self.formula.parse_not()

    def _parse_or_and(self):
        self.formula = self.formula.parse_or_and()
        # to be safe side
        self.formula = self.formula.parse_or_and()

    def segregate(self, symbol):
        if type(self.formula) is BinaryOperation:
            return self.formula.segregate(symbol)
        return [self.formula]


class Pair(object):
    element1 = None
    element2 = None
    resolvent = None
    is_contradict = None

    def __init__(self, e1, e2):
        self.element1 = e1
        self.element2 = e2

    def __eq__(self, other):
        if type(other) is not Pair:
            return False

        e1 = self.element1
        e2 = self.element2
        oe1 = other.element1
        oe2 = other.element2
        return (e1 == oe1 and e2 == oe2) or (e1 == oe2 and e2 == oe1)

    def __str__(self):
        return f"({self.element1}, {self.element2})"

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.element1) + len(self.element2)

    def resolve(self):
        self.resolvent = BinaryOperation("|", self.element1, self.element2).optimize()
        if not self.resolvent:
            # P|Q and !P|!Q this resolves none but they do not contradict each other
            self.is_contradict = len(self.element1) == 1 and len(self.element2) == 1
        else:
            self.is_contradict = False


class PLLogicProblem(object):
    # inputs
    knowledge_base = None
    query = None
    mode = None

    # CNF converted
    CNF_KB = None
    negated_cnf_query = None

    # segregated by AND
    segregated_knowledge_base_clauses = None
    segregated_query_clauses = None

    # prover
    steps_to_prove = None
    is_query_true = None

    def __init__(self, knowledge_base, query, mode):
        self.mode = mode
        self.knowledge_base = []
        self.CNF_KB = []

        # prepare knowledge base
        for kb in knowledge_base:
            self.knowledge_base.append(Knowledge(kb))
            temp_kb = Knowledge(kb)
            temp_kb.convert_to_cnf()
            self.CNF_KB.append(temp_kb)

        # prepare proposition
        self.query = Knowledge(query)
        negated_proposition = UnaryOperation("!", self.query.formula)
        self.negated_cnf_query = Knowledge(negated_proposition, by_formula=True)
        self.negated_cnf_query.convert_to_cnf()
        # segregate query and knowledge base
        self._prepare_segregation()

        # optimize knowledge base and query
        self._optimize_kb_and_query()

        # prove query :)
        self.prove()

    def _prepare_segregation(self):
        # segregate knowledge base with symbol AND
        self.segregated_knowledge_base_clauses = []
        for kb in self.CNF_KB:
            self.segregated_knowledge_base_clauses += kb.segregate("&")

        self.segregated_query_clauses = self.negated_cnf_query.segregate("&")

    def _optimize_kb_and_query(self):
        # optimize segregated formulas
        def optimize(x):
            if type(x) is BinaryOperation:
                return x.optimize()
            return x

        temp = []
        for kb in self.segregated_knowledge_base_clauses:
            t = optimize(kb)
            if t and t not in temp:
                temp.append(t)
        self.segregated_knowledge_base_clauses = temp

        temp = []
        for kb in self.segregated_query_clauses:
            t = optimize(kb)
            if t and t not in temp:
                temp.append(t)
        self.segregated_query_clauses = temp

    def print_result(self, force=False, avoid=False):
        if avoid:
            print("1" if self.is_query_true else "0")
        elif force:
            print(self)
        else:
            if self.mode == 0:
                print("1" if self.is_query_true else "0")
            else:
                i = 1
                for t in self.segregated_knowledge_base_clauses:
                    print(f"{i:2}. {t} (CNF form)")
                    i += 1
                for t in self.segregated_query_clauses:
                    print(f"{i:2}. {t} (Negation of query)")
                    i += 1
                for t in self.steps_to_prove:
                    if t.resolvent:
                        print(f"{i:2}. {t.resolvent} [Using pair {t}]")
                    else:
                        if t.is_contradict:
                            print(f"{i:2}. Contradiction !! [Using pair {t}]")
                        else:
                            print(f"{i:2}. Resolved pair {t}")
                    i += 1
                if self.is_query_true:
                    print("1")
                else:
                    print(f"{i:2}. No pair found that supports query clauses or resolved clauses")
                    print("0")

    def __str__(self):
        ret = "------------------------------\n"
        ret += f'Mode: {self.mode}\n'

        ret += "\nStatement to prove:\n"
        ret += f'{self.query}\n'

        ret += "\nKnowledge base:\n"
        for k in self.knowledge_base:
            ret += f'{k}\n'

        ret += "\nCNF Knowledge base:\n"
        for k in self.CNF_KB:
            ret += f'{k}\n'

        ret += "\nNegation of statement to prove:\n"
        ret += f'{self.negated_cnf_query}\n'

        ret += "\nCNF Knowledge base segregated by AND:\n"
        for f in self.segregated_knowledge_base_clauses:
            ret += f'{f}\n'

        ret += "\nNegation of query to prove (segregated by AND):\n"
        for f in self.segregated_query_clauses:
            ret += f'{f}\n'

        ret += "\nSteps:\n"
        for s in self.steps_to_prove:
            ret += f'Resolvent: {s.resolvent}, Pair: {s}\n'

        ret += "\nResult:\n"
        ret += f"Above Query is {self.is_query_true}\n"
        ret += "------------------------------"
        return ret

    # @staticmethod
    # def segregate_knowledge(knowledge, symbol):
    #     # this method is depreciated as it is implemented in BinaryOperation class
    #     formula = knowledge.formula
    #     ret = [formula]
    #     while True:
    #         temp = []
    #         flag = False  # ret is changed or not
    #         for f in ret:
    #             if type(f) is BinaryOperation and f.operator == symbol:
    #                 flag = True
    #                 temp.append(f.left_operand)
    #                 temp.append(f.right_operand)
    #             else:
    #                 temp.append(f)
    #
    #         if flag:
    #             ret = temp
    #         else:
    #             break
    #     return ret

    # def prove(self):
    #     def is_resolvable(cl1, cl2):
    #         literals1 = cl1.segregate("|") if type(cl1) is BinaryOperation else [cl1]
    #         literals2 = cl2.segregate("|") if type(cl2) is BinaryOperation else [cl2]
    #         for literal in literals2:
    #             if UnaryOperation("!", literal).parse_not() in literals1:
    #                 return True
    #         return False
    #
    #     def find_resolvable_pair(cls, qcls, visited):
    #         # check query clauses with all clauses see if any pair is resolvable
    #         selected_pairs = []
    #         for q in qcls:
    #             for a in cls + qcls:
    #                 if q != a and is_resolvable(q, a):
    #                     select_pair = Pair(q, a)
    #                     if select_pair not in visited and select_pair not in selected_pairs:
    #                         selected_pairs.append(select_pair)
    #         # sort by length of pair, we are preferring unit resolution
    #         selected_pairs.sort(key=lambda x: len(x))
    #         return selected_pairs[0] if selected_pairs else None
    #
    #     kb_clauses = list(self.segregated_knowledge_base_clauses)
    #     query_clauses = list(self.segregated_query_clauses)
    #     self.steps_to_prove = []
    #
    #     resolved_pairs = []
    #
    #     # Execute till you find clauses
    #     while True:
    #         # find resolvable pair
    #         pair = find_resolvable_pair(kb_clauses, query_clauses, resolved_pairs)
    #
    #         # if we don't have pair then query is false
    #         if not pair:
    #             self.is_query_true = False
    #             return
    #
    #         # resolve pair
    #         pair.resolve()
    #
    #         # add pair to resolved pair
    #         resolved_pairs.append(pair)
    #
    #         # add pair to steps of proof
    #         self.steps_to_prove.append(pair)
    #
    #         # does pair proves contradiction
    #         if pair.is_contradict:
    #             self.is_query_true = True
    #             return
    #
    #         # add resolvent to query clause if already not present
    #         if pair.resolvent and pair.resolvent not in query_clauses:
    #             query_clauses.append(pair.resolvent)

    def prove(self):
        def is_resolvable(cl1, cl2):
            literals1 = cl1.segregate("|") if type(cl1) is BinaryOperation else [cl1]
            literals2 = cl2.segregate("|") if type(cl2) is BinaryOperation else [cl2]
            for literal in literals2:
                if UnaryOperation("!", literal).parse_not() in literals1:
                    return True
            return False

        def find_resolvable_pair(cls, visited):
            # check query clauses with all clauses see if any pair is resolvable
            selected_pairs = []
            for q in cls:
                for a in cls:
                    if not q == a and is_resolvable(q, a):
                        select_pair = Pair(q, a)
                        if not (select_pair in visited or select_pair in selected_pairs):
                            selected_pairs.append(select_pair)
            # sort by length of pair, we are preferring unit resolution
            selected_pairs.sort(key=lambda x: len(x))
            return selected_pairs[0] if selected_pairs else None

        kb_clauses = list(self.segregated_knowledge_base_clauses)
        query_clauses = list(self.segregated_query_clauses)
        self.steps_to_prove = []
        resolved_pairs = []

        clauses = kb_clauses + query_clauses
        # Execute till you find clauses
        while True:
            # find resolvable pair
            pair = find_resolvable_pair(clauses, resolved_pairs)

            # if we don't have pair then query is false
            if not pair:
                self.is_query_true = False
                return

            # resolve pair
            pair.resolve()

            # add pair to resolved pair
            resolved_pairs.append(pair)

            # add pair to steps of proof
            self.steps_to_prove.append(pair)

            # does pair proves contradiction
            if pair.is_contradict:
                self.is_query_true = True
                return

            # add resolvent to query clause if already not present
            if pair.resolvent and pair.resolvent not in clauses:
                clauses.append(pair.resolvent)
