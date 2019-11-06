from inspect import signature

LOGIC_OP_AND = 'and'
LOGIC_OP_OR = 'or'
LOGIC_OP_NAND = 'nand'
LOGIC_OP_NOR = 'nor'

class Sieve(object):

    def __init__(self, *args, logic_op=LOGIC_OP_AND):
        self._conditions = [*args]
        self.logic_op = logic_op

    def __call__(self, *args):
        outcomes = [condition(*args) for condition in self._conditions]
        if self.logic_op == LOGIC_OP_AND:
            for p in outcomes:
                if not p:
                    return False
            return True
        elif self.logic_op == LOGIC_OP_OR:
            for p in outcomes:
                if p:
                    return True
            return False
        elif self.logic_op == LOGIC_OP_NAND:
            for p in outcomes:
                if not p:
                    return True
            return False
        elif self.logic_op == LOGIC_OP_NOR:
            for p in outcomes:
                if p:
                    return False
            return True
        else:
            return True

    def add(self, condition):
        self._conditions.append(condition)

    def sift(self, batch):
        return [element for element in batch if self(element)]

    def sift_df_rows(self, df):
        return [row for _, row in df.iterrows() if self(row)]