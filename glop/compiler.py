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

    def compile(self):
        self.grammar = self.grammar.flatten(self._should_flatten)

        for _, rule, node in self.grammar.rules:
            self._methods[rule] = self._gen(node)

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
            methods += self._method_for(rule)

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
        if '_h_set' in self._needed and '_h_scope' in self._needed:
            args['bindings_fields'] = '        self._scopes = []\n'
        if self.memoize:
            args['memoizing_fields'] = '        self._cache = {}\n'
        return self.templates.TEXT.format(**args), None

    def _method_for(self, rule):
        if self.memoize and rule.startswith('_r_'):
            tmpl = self.templates.MEMOIZED_METHOD
        else:
            tmpl = self.templates.METHOD
        return '\n' + tmpl.format(
            rule=rule,
            lines=('        ' + '\n        '.join(self._methods[rule])))

    def _native_methods_of_type(self, ty):
        methods = ''
        for name in sorted(r for r in self._needed if r.startswith(ty)):
            methods += '\n'
            lines = textwrap.dedent(self._natives[name]['body']).splitlines()
            for l in lines:
                methods += '    %s\n' % (l,)
        return methods

    def _gen(self, node, as_callable=False):
        fn = getattr(self, '_%s_' % node[0])
        if not self._should_flatten(node):
            return fn(node, as_callable)
        return fn(node)

    def _should_flatten(self, node):
        if node[0] in ('label', 'not', 'paren', 'post'):
            return False # self._should_flatten(node[1])
        return node[0] not in ('action', 'apply', 'lit', 'range')

    def _inv(self, name, arg_str):
        if name in self._natives:
            self._need(name)
        return 'self.%s(%s)' % (name, arg_str)

    def _callable(self, node):
        if self._should_flatten(node):
            import pdb; pdb.set_trace()
        # assert not self._should_flatten(node)
        return self._gen(node, as_callable=True)

    def _need(self, name):
        self._needed.add(name)
        for need in self._natives.get(name, {}).get('needs', []):
            self._need(need)

    def _args(self, args, indent):
        sep = ',\n' + ' ' * indent
        return '[' + sep.join(self._callable(arg) for arg in args) + ']'

    #
    # Handlers for each AST node follow.
    #

    def _action_(self, node, as_callable=False):
        expr = self._inv('_h_succeed', self._gen(node[1]))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _apply_(self, node, as_callable=False):
        rule_name = node[1]
        if node[1] not in self.grammar.rule_names:
            self._need(rule_name)
        expr = 'self.%s' % rule_name
        if as_callable:
            return expr
        else:
            return ['%s()' % expr]

    def _choice_(self, node):
        return [self._inv('_h_choose', self._args(node[1], indent=24))]

    def _empty_(self, _node):
        return []

    def _label_(self, node, as_callable=False):
        var = lit.encode(node[2])
        expr = self._inv('_h_bind', '%s, %s' % (self._callable(node[1]), var))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _lit_(self, node, as_callable=False):
        arg = lit.encode(node[1])
        if len(node[1]) == 1:
            expr = self._inv('_h_ch', arg)
        else:
            expr = self._inv('_h_str', '%s, %d' % (arg, len(node[1])))
        if as_callable:
            return 'lambda: %s' % expr
        else:
            return [expr]

    def _ll_arr_(self, node):
        return '[' + ', '.join(self._gen(e) for e in node[1]) + ']'

    def _ll_call_(self, node):
        args = [str(self._gen(e)) for e in node[1]]
        return '(' + ', '.join(args) + ')'

    def _ll_getattr_(self, node):
        return '.' + node[1]

    def _ll_getitem_(self, node):
        return '[' + str(self._gen(node[1])) + ']'

    def _ll_lit_(self, node):
        return lit.encode(node[1])

    def _ll_num_(self, node):
        return node[1]

    def _ll_plus_(self, node):
        return '%s + %s' % (self._gen(node[1]), self._gen(node[2]))

    def _ll_qual_(self, node):
        v = self._gen(node[1])
        for p in node[2]:
            v += self._gen(p)
        return v

    def _ll_var_(self, node):
        name = node[1]
        if name in self._identifiers:
            return self._identifiers[name]
        if '_f_' + name in self._natives:
            self._need('_f_%s' % name)
            return 'self._f_%s' % name
        else:
            return self._inv('_h_get', "'%s'" % name)

    def _not_(self, node, as_callable=False):
        expr = self._inv('_h_not', self._callable(node[1]))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _paren_(self, node, as_callable=False):
        return self._gen(node[1], as_callable)

    def _post_(self, node, as_callable=False):
        if node[2] == '?':
            expr = self._inv('_h_opt', self._callable(node[1]))
        elif node[2] == '+':
            expr = self._inv('_h_plus', self._callable(node[1]))
        else:
            expr = self._inv('_h_star', self._callable(node[1]) + ', []')
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _pred_(self, node):
        return ['v = %s' % self._gen(node[1]),
                'if v:',
                '    ' + self._inv('_h_succeed', 'v'),
                'else:',
                '    ' + self._inv('_h_fail', '')]

    def _range_(self, node, as_callable=False):
        expr = self._inv('_h_range', '%s, %s' % (lit.encode(node[1][1]),
                                                 lit.encode(node[2][1])))
        if as_callable:
            return 'lambda: ' + expr
        return [expr]

    def _scope_(self, node):
        return [self._inv('_h_scope', "'%s', %s" % (
                                      node[2],
                                      self._args(node[1],
                                                 indent=27 + len(node[2]))))]

    def _seq_(self, node):
        return [self._inv('_h_seq', self._args(node[1], indent=21))]
