# Copyright 2014 Dirk Pranke. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 as found in the LICENSE file.
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

import textwrap

from . import ir
from . import lit
from . import python_templates


class Compiler(object):
    def __init__(self, grammar, classname, main_wanted, memoize):
        self.grammar = grammar
        self.classname = classname
        self.memoize = memoize
        self.main_wanted = main_wanted
        self.templates = python_templates

        self._methods = {}
        self._method_lines = []
        self._identifiers = self.templates.IDENTIFIERS
        self._natives = self.templates.METHODS
        self._needed = set(['_h_err'])
        self._regexps = {}

    def compile(self):
        ast = self.grammar.ast
        ast = ir.regexpify(ast)
        ast = ir.flatten(ast, self._should_flatten)
        if self.memoize:
            original_names = set('_r_' + name
                                 for name in self.grammar.rule_names)
            ast = ir.memoize(ast, original_names)
        self.grammar = ir.Grammar(ast)

        for _, rule, node in self.grammar.rules:
            self._methods[rule] = self._gen(node, as_callable=False)

        imports = self.templates.IMPORTS
        for name in self._needed:
            for imp in self._natives.get(name, {}).get('imports', []):
                imports.add(imp)
        if self.main_wanted:
            for imp in self.templates.MAIN_IMPORTS:
                imports.add(imp)
        imports_str = '\n'.join(sorted(imports))

        methods = ''
        for _, rule, _ in self.grammar.rules:
            methods += self.templates.METHOD.format(
               rule=rule,
               lines=('        ' + '\n        '.join(self._methods[rule])))

        methods += self._native_methods_of_type('_r_')
        methods += self._native_methods_of_type('_f_')
        methods += self._native_methods_of_type('_h_')

        args = {
          'bindings_fields': '',
          'classname': self.classname,
          'imports': imports_str,
          'main_header': '',
          'main_footer': '',
          'memoizing_fields': '',
          'methods': methods,
          'starting_rule': self.grammar.starting_rule,
        }
        if self.main_wanted:
            args['main_header'] = self.templates.MAIN_HEADER.format(**args)
            args['main_footer'] = self.templates.MAIN_FOOTER.format(**args)
        args['optional_fields'] = ''
        if '_h_set' in self._needed and '_h_scope' in self._needed:
            args['optional_fields'] += '        self._scopes = []\n'
        if self.memoize:
            args['optional_fields'] += '        self._cache = {}\n'
        return self.templates.TEXT.format(**args), None

    def _native_methods_of_type(self, ty):
        methods = ''
        for name in sorted(r for r in self._needed if r.startswith(ty)):
            methods += '\n'
            lines = textwrap.dedent(self._natives[name]['body']).splitlines()
            for l in lines:
                methods += '    %s\n' % (l,)
        return methods

    def _gen(self, node, as_callable):
        fn = getattr(self, '_%s_' % node[0])
        return fn(node, as_callable)

    # Using a MAX_DEPTH of three ensures that we don't unroll expressions
    # too much; in particular, by making sure that any of the nodes that
    # contain more than one child are set to MAX_DEPTH, we don't nest
    # two of them at once. This keeps things fairly readable.
    _MAX_DEPTH = 3

    def _depth(self, node):
        ty = node[0]
        if ty in ('choice', 'scope', 'seq'):
            return max(self._depth(n) for n in node[1]) + self._MAX_DEPTH
        elif ty in ('label', 'not', 'opt', 'paren', 'plus', 're', 'star'):
            return self._depth(node[1]) + 1
        else:
            return 1

    def _should_flatten(self, node):
        return self._depth(node) > self._MAX_DEPTH

    def _inv(self, name, arg_str):
        if name in self._natives:
            self._need(name)
        return 'self.%s(%s)' % (name, arg_str)

    def _need(self, name):
        self._needed.add(name)
        for need in self._natives.get(name, {}).get('needs', []):
            self._need(need)

    def _args(self, args, indent):
        sep = ',\n' + ' ' * indent
        return '[' + sep.join(self._gen(arg, as_callable=True) for arg in args) + ']'

    #
    # Handlers for each AST node follow.
    #

    def _action_(self, node, as_callable):
        expr = self._inv('_h_succeed', self._gen(node[1], as_callable=True))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _apply_(self, node, as_callable):
        rule_name = node[1]
        if node[1] not in self.grammar.rule_names:
            self._need(rule_name)
        expr = 'self.%s' % rule_name
        if as_callable:
            return expr
        else:
            return ['%s()' % expr]

    def _choice_(self, node, as_callable):
        expr = self._inv('_h_choose', self._args(node[1], indent=24))
        if as_callable:
            return 'lambda: ' + expr
        else:
            return [expr]

    def _empty_(self, _node, as_callable):
        if as_callable:
            return ''
        else:
            return []

    def _label_(self, node, as_callable):
        var = lit.encode(node[2])
        expr = self._inv('_h_bind', '%s, %s' % (
                         self._gen(node[1], as_callable=True), var))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _lit_(self, node, as_callable):
        arg = lit.encode(node[1])
        if len(node[1]) == 1:
            expr = self._inv('_h_ch', arg)
        else:
            expr = self._inv('_h_str', '%s, %d' % (arg, len(node[1])))
        if as_callable:
            return 'lambda: %s' % expr
        else:
            return [expr]

    def _ll_arr_(self, node, _as_callable):
        return '[' + ', '.join(self._gen(e, as_callable=True) for e in node[1]) + ']'

    def _ll_call_(self, node, _as_callable):
        args = [str(self._gen(e, as_callable=True)) for e in node[1]]
        return '(' + ', '.join(args) + ')'

    def _ll_getattr_(self, node, _as_callable):
        return '.' + node[1]

    def _ll_getitem_(self, node, _as_callable):
        return '[' + str(self._gen(node[1], as_callable=True)) + ']'

    def _ll_lit_(self, node, _as_callable):
        return lit.encode(node[1])

    def _ll_num_(self, node, _as_callable):
        return node[1]

    def _ll_plus_(self, node, _as_callable):
        return '%s + %s' % (self._gen(node[1], as_callable=True),
                            self._gen(node[2], as_callable=True))

    def _ll_qual_(self, node, _as_callable):
        v = self._gen(node[1], as_callable=True)
        for p in node[2]:
            v += self._gen(p, as_callable=True)
        return v

    def _ll_var_(self, node, _as_callable):
        name = node[1]
        if name in self._identifiers:
            return self._identifiers[name]
        if '_f_' + name in self._natives:
            self._need('_f_%s' % name)
            return 'self._f_%s' % name
        else:
            return self._inv('_h_get', "'%s'" % name)

    def _memo_(self, node, as_callable):
        var = lit.encode(node[2])
        expr = self._inv('_h_memo', '%s, %s' % (
                         self._gen(node[1], as_callable=True), var))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _not_(self, node, as_callable):
        expr = self._inv('_h_not', self._gen(node[1], as_callable=True))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _opt_(self, node, as_callable):
        expr = self._inv('_h_opt', self._gen(node[1], as_callable=True))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _paren_(self, node, as_callable):
        return self._gen(node[1], as_callable)

    def _plus_(self, node, as_callable):
        expr = self._inv('_h_plus', self._gen(node[1], as_callable=True))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _pred_(self, node, as_callable):
        if as_callable:
            return ('lambda: (lambda x: ' + self._inv('_h_succeed', 'x') +
                    ' if x else ' + self._inv('_h_fail', '') +
                    ')(%s)' % self._gen(node[1], as_callable=True))
        else:
            return ['v = %s' % self._gen(node[1], as_callable=True),
                    'if v:',
                    '    ' + self._inv('_h_succeed', 'v'),
                    'else:',
                    '    ' + self._inv('_h_fail', '')]

    def _range_(self, node, as_callable):
        expr = self._inv('_h_range', '%s, %s' % (lit.encode(node[1][1]),
                                                 lit.encode(node[2][1])))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _re_(self, node, as_callable):
        expr = self._inv('_h_re', '%s' % lit.encode(node[1]))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _scope_(self, node, as_callable):
        expr = self._inv('_h_scope', "'%s', %s" % (
                   node[2],
                   self._args(node[1], indent=27 + len(node[2]))))
        if as_callable:
            return 'lambda: ' + expr
        else:
            return [expr]

    def _seq_(self, node, as_callable):
        expr = self._inv('_h_seq', self._args(node[1], indent=21))
        if as_callable:
            return 'lambda: ' + expr
        else:
            return [expr]

    def _star_(self, node, as_callable):
        expr = self._inv('_h_star',
                         self._gen(node[1], as_callable=True) + ', []')
        if as_callable:
            return 'lambda: ' + expr
        return [expr]
