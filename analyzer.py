class Grammar(object):
    def __init__(self, rules, start='grammar'):
        self.rules = rules
        self.start = start


class Analyzer(object):
    def __init__(self, ast):
        self.ast = ast

    def analyze(self):
        rules = {}
        for n in self.ast:
            assert n[0] == 'rule'
            rules[n[1]] = n[2]

        return Grammar(rules, 'grammar'), None