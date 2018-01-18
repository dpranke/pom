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
    elif node[0] in ('memo', 'not', 'opt', 'paren', 'plus', 're', 'star'):
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
    elif node_type in ('not', 'opt', 'plus', 're', 'star'):
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
        new_subnode, new_subrules = _flatten(old_name, old_node,
                                             should_flatten)
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
    elif old_type in ('memo', 'not', 'opt', 'paren', 'plus', 're', 'star'):
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


def regexpify(old_node, rules=None, force=False, rules_to_re=None):
    if rules is None:
        rules = {}
        for _, name, val in old_node[1]:
            rules[name] = val

    old_typ = old_node[0]
    old_subnode = old_node[1]
    if old_typ == 'choice':
        if all(_can_regexpify(sn, rules) for sn in old_subnode):
            return ['re', _merge_choices(regexpify(sn, rules, force=True)[1]
                                         for sn in old_subnode)]
        else:
            return [old_typ, old_subnode]
    elif old_typ == 'rules':
        if rules_to_re is not None:
          return [old_typ, [regexpify(sn, rules)
                            if sn[1] in rules_to_re else sn
                            for sn in old_subnode]]
        return [old_typ, [regexpify(sn, rules) for sn in old_subnode]]
    elif old_typ in ('scope', 'seq'):
        subnodes = [regexpify(sn, rules, force=True) for sn in old_subnode]
        collapsed_subnodes = []
        l = None
        while subnodes:
            r = subnodes.pop(0)
            if not l:
                l = r
            elif not _can_regexpify(l, rules) or not _can_regexpify(r, rules):
                collapsed_subnodes.append(l)
                l = r
                continue
            else:
                l = ['re', regexpify(l, rules)[1] + regexpify(r, rules)[1]]
        collapsed_subnodes.append(l)
        if len(collapsed_subnodes) == 1:
            return collapsed_subnodes[0]
        if old_typ == 'scope':
            return [old_typ, collapsed_subnodes, old_node[2]]
        else:
            return [old_typ, collapsed_subnodes]
    elif old_typ in ('label',) and _can_regexpify(old_subnode, rules,
                                                  in_label=True):
        return [old_typ, regexpify(old_subnode, rules), old_node[2]]
    elif old_typ in ('rule',):
        rules[old_node[1]] = regexpify(old_node[2], rules)
        return [old_typ, old_node[1], rules[old_node[1]]]
    elif old_typ == 'opt' and _can_regexpify(old_subnode, rules):
        return ['re', _post(regexpify(old_subnode, rules, force=True)[1], '?')]
    elif old_typ == 'plus' and _can_regexpify(old_subnode, rules):
        return ['re', _post(regexpify(old_subnode, rules, force=True)[1], '+')]
    elif old_typ == 'star' and _can_regexpify(old_subnode, rules):
        return ['re', _post(regexpify(old_subnode, rules, force=True)[1], '*')]
    elif old_typ == 'not' and _can_regexpify(old_subnode, rules):
        return ['re', '(?!%s)' % regexpify(old_subnode, rules, force=True)[1]]
    elif old_typ in ('memo', 'not', 'opt', 'paren', 'plus', 'star'):
        return [old_typ, regexpify(old_subnode, rules)]
    elif old_typ in ('lit', 'range') and force:
        return ['re', _re_esc(old_node)]
    elif old_typ == 'apply'and force:
        if old_subnode == 'anything':
            return ['re', '.']
        elif old_subnode == 'end':
            return old_node
        else:
            return regexpify(rules[old_subnode], rules, force=force)
    else:
        return old_node


def _merge_choices(nodes):
    nodes = list(nodes)
    if all(n[0] == '[' for n in nodes):
        return '[%s]' % ''.join(n[1:-1] for n in nodes)
    return '(' + '|'.join(n for n in nodes) + ')'


def _post(re_expr, op):
    if re_expr[0] in ('(', '[') or len(re_expr) == 1:
        return re_expr + op
    return '(%s)%s' % (re_expr, op)


def _can_regexpify(node, rules, visited=None, in_label=False):
    visited = visited or set()
    return (node[0] in ('lit', 'range', 're') or
            node == ['apply', 'anything'] or
            (node[0] in ('not',) and
             _can_regexpify(node[1], rules, visited, in_label)) or
            (node[0] in ('opt', 'plus', 'star') and not in_label and
             _can_regexpify(node[1], rules, visited, in_label)) or
            (node[0] == 'apply' and not node[1] in visited and
             not node[1] == 'end' and
            _can_regexpify(rules[node[1]], rules, visited.union({node[1]}),
                           in_label)) or
            (node[0] in ('choice', 'scope', 'seq') and
             all(_can_regexpify(sn, rules, visited, in_label)
                 for sn in node[1])))


def _re_esc(node):
    if node[0] == 'lit':
        return ''.join('\\%s' % c if (c in '\\[].+*?^$()') else c
                       for c in node[1])
    elif node[0] == 'range':
        return '[%s-%s]' % (node[1][1], node[2][1])
    elif node[0] == 're':
        return node[1]
    assert False, 'unexpected node: %s' % repr(node)


def validate_ast(ast):
    if ast[0] != 'rules' or any(n[0] != 'rule' for n in ast[1]):
        return 'malformed ast'
    return None
