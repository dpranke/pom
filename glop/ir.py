# Copyright 2014 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class Grammar(object):
    def __init__(self, ast):
        ast = rewrite_sequences_with_labels_as_scopes(ast)
        self.ast = simplify(ast)
        self.rules = self.ast[1]
        self.rule_names = set(r[1] for r in self.rules)
        self.starting_rule = self.rules[0][1]

    def rename(self, prefix):
        """Renames all of the rules in the AST to have the given prefix."""
        return Grammar(rename(self.ast, prefix))

    def flatten(self, should_flatten):
        return Grammar(flatten(self.ast, should_flatten))

    def memoize(self, rules_to_memoize):
        return Grammar(memoize(self.ast, rules_to_memoize))


def memoize(ast, rules_to_memoize):
    new_rules = []
    for rule in ast[1]:
        _, name, node = rule
        if name in rules_to_memoize:
            new_rules.append(['rule', name, ['memo', node, name]])
        else:
            new_rules.append(rule)
    return ['rules', new_rules]


def rename(node, prefix):
    """Returns a new AST with all of the rule names prefixed by |prefix|."""
    if node[0] == 'rule':
        return [node[0], prefix + node[1], rename(node[2], prefix)]
    elif node[0] == 'apply':
        return [node[0], prefix + node[1]]
    elif node[0] in ('choice', 'rules', 'seq'):
        return [node[0], [rename(n, prefix) for n in node[1]]]
    elif node[0] in ('memo', 'not', 'opt', 'paren', 'plus', 'star'):
        return [node[0], rename(node[1], prefix)]
    elif node[0] == 'label':
        return [node[0], rename(node[1], prefix), node[2]]
    elif node[0] == 'scope':
        return [node[0], [rename(n, prefix) for n in node[1]],
                node[2]]
    else:
        return node


def simplify(node):
    """Returns a new, simplified version of an AST:

    * Any `choice`, `seq`, or `scope` node with only one child is replaced
      the child.
    * Any `paren` node is replaced by its child node.
    """
    node_type = node[0]
    if node_type == 'rules':
        return [node_type, [simplify(n) for n in node[1]]]
    elif node_type == 'rule':
        return [node_type, node[1], simplify(node[2])]
    elif node_type in ('choice', 'seq'):
        if len(node[1]) == 1:
            return simplify(node[1][0])
        return [node_type, [simplify(n) for n in node[1]]]
    elif node_type in ('not', 'opt', 'plus', 'star'):
        return [node_type, simplify(node[1])]
    elif node_type == 'paren':
        return simplify(node[1])
    elif node_type in ('label', 'memo'):
        return [node_type, simplify(node[1]), node[2]]
    elif node_type == 'scope':
        if len(node[1]) == 1:
            return simplify(node[1][0])
        return [node_type, [simplify(n) for n in node[1]], node[2]]
    else:
        return node


def rewrite_sequences_with_labels_as_scopes(ast):
    for rule in ast[1]:
        rule_name = rule[1]
        if rule[2][0] == 'choice':
            new_choices = []
            for choice in rule[2][1]:
                if choice[0] == 'seq':
                    if _has_labels(choice[1]):
                        new_choice = ['scope', choice[1], rule_name]
                    else:
                        new_choice = choice
                else:
                    new_choice = choice
                new_choices.append(new_choice)
            rule[2][1] = new_choices
    return ast


def _has_labels(node):
    if node and node[0] == 'label':
        return True
    for n in node:
        if isinstance(n, list) and _has_labels(n):
            return True
    return False


def flatten(ast, should_flatten):
    """Return a new ast with nested sequences or choices moved to new rules."""
    ast = rename(ast, '_r_')

    new_rules = []
    for _, old_name, old_node in ast[1]:
        new_subnode, new_subrules = _flatten(old_name, old_node, should_flatten)
        new_rules += [['rule', old_name, new_subnode]] + new_subrules
    return ['rules', new_rules]


def _flatten(old_name, old_node, should_flatten):
    old_type = old_node[0]
    new_rules = []
    if old_type in ('choice', 'scope', 'seq'):
        new_subnodes = []
        for i, subnode in enumerate(old_node[1]):
            new_name = '_s_%s_%s%d' % (old_name[3:], old_type[0], i)
            new_subnode, new_subrules = _flatten(new_name, subnode,
                                                 should_flatten)
            if should_flatten(new_subnode):
                new_subnodes.append(['apply', new_name])
                new_rules += [['rule', new_name, new_subnode]]
            else:
                new_subnodes.append(new_subnode)
            new_rules += new_subrules
        if old_type == 'scope':
            new_node = [old_type, new_subnodes, old_node[2]]
        else:
            new_node = [old_type, new_subnodes]
    elif old_type in ('label',):
        new_name = '_s_%s_%s' % (old_name[3:], old_type[0])
        new_subnode, new_subrules = _flatten(new_name, old_node[1],
                                             should_flatten)
        if should_flatten(new_subnode):
            new_node = [old_type, ['apply', new_name], old_node[2]]
            new_rules += [['rule', new_name, new_subnode]]
        else:
            new_node = [old_type, new_subnode, old_node[2]]
        new_rules += new_subrules
    elif old_type in ('memo', 'not', 'opt', 'paren', 'plus', 'star'):
        new_name = '_s_%s_%s' % (old_name[3:], old_type[0])
        new_subnode, new_subrules = _flatten(new_name, old_node[1],
                                             should_flatten)
        if should_flatten(new_subnode):
            new_node = [old_type, ['apply', new_name]]
            new_rules += [['rule', new_name, new_subnode]]
        else:
            new_node = [old_type, new_subnode]
        new_rules += new_subrules
    else:
        new_node = old_node
    return new_node, new_rules


def validate_ast(ast):
    if ast[0] != 'rules' or any(n[0] != 'rule' for n in ast[1]):
        return 'malformed ast'
    return None
