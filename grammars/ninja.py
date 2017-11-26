#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import os
import sys

if sys.version_info[0] < 3:
    # pylint: disable=redefined-builtin
    chr = unichr
    str = unicode

# pylint: disable=line-too-long


class Parser(object):
    def __init__(self, msg, fname):
        self.msg = str(msg)
        self.end = len(self.msg)
        self.fname = fname
        self.val = None
        self.pos = 0
        self.failed = False
        self.errpos = 0
        self._scopes = []

    def parse(self):
        self._r_grammar()
        if self.failed:
            return self._h_err()
        return self.val, None, self.pos

    def _r_grammar(self):
        self._h_scope('_r_grammar', [self._s_grammar_s0,
                                     self._s_grammar_s1,
                                     self._r_end,
                                     self._s_grammar_s3])

    def _s_grammar_s0(self):
        self._h_bind(self._s_grammar_s0_l, 'ds')

    def _s_grammar_s0_l(self):
        self._h_star(self._s_grammar_s0_l_p, [])

    def _s_grammar_s0_l_p(self):
        self._h_seq([self._s_grammar_s0_l_p_s0,
                     self._r_ws,
                     self._r_decl])

    def _s_grammar_s0_l_p_s0(self):
        self._h_star(self._r_empty_line, [])

    def _s_grammar_s1(self):
        self._h_star(self._r_empty_line, [])

    def _s_grammar_s3(self):
        self._h_succeed(self._h_get('ds'))

    def _r_decl(self):
        self._h_choose([self._r_build,
                        self._r_rule,
                        self._r_var,
                        self._r_subninja,
                        self._r_include,
                        self._r_pool,
                        self._r_default])

    def _r_build(self):
        self._h_scope('_r_build', [lambda: self._h_str('build', 5),
                                   self._r_ws,
                                   self._s_build_s2,
                                   self._r_ws,
                                   lambda: self._h_ch(':'),
                                   self._r_ws,
                                   self._s_build_s6,
                                   self._s_build_s7,
                                   self._s_build_s8,
                                   self._s_build_s9,
                                   self._r_eol,
                                   self._s_build_s11,
                                   self._s_build_s12])

    def _s_build_s11(self):
        self._h_bind(self._s_build_s11_l, 'vs')

    def _s_build_s11_l(self):
        self._h_star(self._s_build_s11_l_p, [])

    def _s_build_s11_l_p(self):
        self._h_seq([self._r_ws,
                     self._r_var])

    def _s_build_s12(self):
        self._h_succeed(['build', self._h_get('os'), self._h_get('rule'), self._h_get('eds'), self._h_get('ids'), self._h_get('ods'), self._h_get('vs')])

    def _s_build_s2(self):
        self._h_bind(self._r_paths, 'os')

    def _s_build_s6(self):
        self._h_bind(self._r_name, 'rule')

    def _s_build_s7(self):
        self._h_bind(self._r_explicit_deps, 'eds')

    def _s_build_s8(self):
        self._h_bind(self._r_implicit_deps, 'ids')

    def _s_build_s9(self):
        self._h_bind(self._r_order_only_deps, 'ods')

    def _r_rule(self):
        self._h_scope('_r_rule', [lambda: self._h_str('rule', 4),
                                  self._r_ws,
                                  self._s_rule_s2,
                                  self._r_eol,
                                  self._s_rule_s4,
                                  self._s_rule_s5])

    def _s_rule_s2(self):
        self._h_bind(self._r_name, 'n')

    def _s_rule_s4(self):
        self._h_bind(self._s_rule_s4_l, 'vs')

    def _s_rule_s4_l(self):
        self._h_star(self._s_rule_s4_l_p, [])

    def _s_rule_s4_l_p(self):
        self._h_seq([self._r_ws,
                     self._r_var])

    def _s_rule_s5(self):
        self._h_succeed(['rule', self._h_get('n'), self._h_get('vs')])

    def _r_var(self):
        self._h_scope('_r_var', [self._s_var_s0,
                                 self._r_ws,
                                 lambda: self._h_ch('='),
                                 self._r_ws,
                                 self._s_var_s4,
                                 self._r_eol,
                                 self._s_var_s6])

    def _s_var_s0(self):
        self._h_bind(self._r_name, 'n')

    def _s_var_s4(self):
        self._h_bind(self._r_value, 'v')

    def _s_var_s6(self):
        self._h_succeed(['var', self._h_get('n'), self._h_get('v')])

    def _r_value(self):
        self._h_scope('_r_value', [self._s_value_s0,
                                   self._s_value_s1])

    def _s_value_s0(self):
        self._h_bind(self._s_value_s0_l, 'vs')

    def _s_value_s0_l(self):
        self._h_star(self._s_value_s0_l_p, [])

    def _s_value_s0_l_p(self):
        self._h_seq([self._s_value_s0_l_p_s0,
                     self._s_value_s0_l_p_s1])

    def _s_value_s0_l_p_s0(self):
        self._h_not(self._r_eol)

    def _s_value_s0_l_p_s1(self):
        self._h_choose([self._s_value_s0_l_p_s1_c0,
                        self._r_anything])

    def _s_value_s0_l_p_s1_c0(self):
        self._h_seq([self._r_ws,
                     self._s_value_s0_l_p_s1_c0_s1])

    def _s_value_s0_l_p_s1_c0_s1(self):
        self._h_succeed('')

    def _s_value_s1(self):
        self._h_succeed(''.join(self._h_get('vs')))

    def _r_subninja(self):
        self._h_scope('_r_subninja', [lambda: self._h_str('subninja', 8),
                                      self._r_ws,
                                      self._s_subninja_s2,
                                      self._s_subninja_s3])

    def _s_subninja_s2(self):
        self._h_bind(self._r_path, 'p')

    def _s_subninja_s3(self):
        self._h_succeed(['subninja', self._h_get('p')])

    def _r_include(self):
        self._h_scope('_r_include', [lambda: self._h_str('include', 7),
                                     self._r_ws,
                                     self._s_include_s2,
                                     self._s_include_s3])

    def _s_include_s2(self):
        self._h_bind(self._r_path, 'p')

    def _s_include_s3(self):
        self._h_succeed(['include', self._h_get('p')])

    def _r_pool(self):
        self._h_scope('_r_pool', [lambda: self._h_str('pool', 4),
                                  self._r_ws,
                                  self._s_pool_s2,
                                  self._r_eol,
                                  self._s_pool_s4,
                                  self._s_pool_s5])

    def _s_pool_s2(self):
        self._h_bind(self._r_name, 'n')

    def _s_pool_s4(self):
        self._h_bind(self._s_pool_s4_l, 'vars')

    def _s_pool_s4_l(self):
        self._h_star(self._s_pool_s4_l_p, [])

    def _s_pool_s4_l_p(self):
        self._h_seq([self._r_ws,
                     self._r_var])

    def _s_pool_s5(self):
        self._h_succeed(['pool', self._h_get('n'), self._h_get('vars')])

    def _r_default(self):
        self._h_scope('_r_default', [lambda: self._h_str('default', 7),
                                     self._r_ws,
                                     self._s_default_s2,
                                     self._r_eol,
                                     self._s_default_s4])

    def _s_default_s2(self):
        self._h_bind(self._r_paths, 'ps')

    def _s_default_s4(self):
        self._h_succeed(['default', self._h_get('ps')])

    def _r_paths(self):
        self._h_scope('_r_paths', [self._s_paths_s0,
                                   self._s_paths_s1,
                                   self._s_paths_s2])

    def _s_paths_s0(self):
        self._h_bind(self._r_path, 'hd')

    def _s_paths_s1(self):
        self._h_bind(self._s_paths_s1_l, 'tl')

    def _s_paths_s1_l(self):
        self._h_star(self._s_paths_s1_l_p, [])

    def _s_paths_s1_l_p(self):
        self._h_seq([self._r_ws,
                     self._r_path])

    def _s_paths_s2(self):
        self._h_succeed([self._h_get('hd')] + self._h_get('tl'))

    def _r_path(self):
        self._h_scope('_r_path', [self._s_path_s0,
                                  self._s_path_s1])

    def _s_path_s0(self):
        self._h_bind(self._s_path_s0_l, 'p')

    def _s_path_s0_l(self):
        self._h_plus(self._s_path_s0_l_p)

    def _s_path_s0_l_p(self):
        self._h_choose([self._s_path_s0_l_p_c0,
                        self._s_path_s0_l_p_c1])

    def _s_path_s0_l_p_c0(self):
        self._h_seq([lambda: self._h_ch('$'),
                     lambda: self._h_ch(' ')])

    def _s_path_s0_l_p_c1(self):
        self._h_seq([self._s_path_s0_l_p_c1_s0,
                     self._r_anything])

    def _s_path_s0_l_p_c1_s0(self):
        self._h_not(self._s_path_s0_l_p_c1_s0_n)

    def _s_path_s0_l_p_c1_s0_n(self):
        self._s_path_s0_l_p_c1_s0_n_p()

    def _s_path_s0_l_p_c1_s0_n_p(self):
        self._h_choose([self._s_path_s0_l_p_c1_s0_n_p_c0,
                        self._s_path_s0_l_p_c1_s0_n_p_c1,
                        self._s_path_s0_l_p_c1_s0_n_p_c2,
                        self._s_path_s0_l_p_c1_s0_n_p_c3,
                        self._s_path_s0_l_p_c1_s0_n_p_c4])

    def _s_path_s0_l_p_c1_s0_n_p_c0(self):
        self._h_seq([lambda: self._h_ch(' ')])

    def _s_path_s0_l_p_c1_s0_n_p_c1(self):
        self._h_seq([lambda: self._h_ch(':')])

    def _s_path_s0_l_p_c1_s0_n_p_c2(self):
        self._h_seq([lambda: self._h_ch('=')])

    def _s_path_s0_l_p_c1_s0_n_p_c3(self):
        self._h_seq([lambda: self._h_ch('|')])

    def _s_path_s0_l_p_c1_s0_n_p_c4(self):
        self._h_seq([self._r_eol])

    def _s_path_s1(self):
        self._h_succeed(self._f_join('', self._h_get('p')))

    def _s_paths_s0(self):
        self._h_bind(self._r_path, 'hd')

    def _s_paths_s1(self):
        self._h_bind(self._s_paths_s1_l, 'tl')

    def _s_paths_s1_l(self):
        self._h_star(self._s_paths_s1_l_p, [])

    def _s_paths_s1_l_p(self):
        self._h_seq([self._r_ws,
                     self._r_path])

    def _s_paths_s2(self):
        self._h_succeed([self._h_get('hd')] + self._h_get('tl'))

    def _r_name(self):
        self._h_scope('_r_name', [self._s_name_s0,
                                  self._s_name_s1,
                                  self._s_name_s2])

    def _s_name_s0(self):
        self._h_bind(self._r_letter, 'hd')

    def _s_name_s1(self):
        self._h_bind(self._s_name_s1_l, 'tl')

    def _s_name_s1_l(self):
        self._h_star(self._s_name_s1_l_p, [])

    def _s_name_s1_l_p(self):
        self._h_choose([self._r_letter,
                        self._r_digit,
                        lambda: self._h_ch('_')])

    def _s_name_s2(self):
        self._h_succeed(self._f_join('', [self._h_get('hd')] + self._h_get('tl')))

    def _r_letter(self):
        self._h_choose([self._s_letter_c0,
                        self._s_letter_c1])

    def _s_letter_c0(self):
        self._h_range('a', 'z')

    def _s_letter_c1(self):
        self._h_range('A', 'Z')

    def _r_digit(self):
        self._h_range('0', '9')

    def _r_explicit_deps(self):
        self._h_choose([self._s_explicit_deps_c0,
                        self._s_explicit_deps_c1])

    def _s_explicit_deps_c0(self):
        self._h_scope('_s_explicit_deps_c0', [self._r_ws,
                                              self._s_explicit_deps_c0_s1,
                                              self._s_explicit_deps_c0_s2])

    def _s_explicit_deps_c0_s1(self):
        self._h_bind(self._r_paths, 'ps')

    def _s_explicit_deps_c0_s2(self):
        self._h_succeed(self._h_get('ps'))

    def _s_explicit_deps_c1(self):
        self._h_succeed([])

    def _r_implicit_deps(self):
        self._h_choose([self._s_implicit_deps_c0,
                        self._s_implicit_deps_c1])

    def _s_implicit_deps_c0(self):
        self._h_scope('_s_implicit_deps_c0', [self._r_ws,
                                              lambda: self._h_ch('|'),
                                              self._r_ws,
                                              self._s_implicit_deps_c0_s3,
                                              self._s_implicit_deps_c0_s4])

    def _s_implicit_deps_c0_s3(self):
        self._h_bind(self._r_paths, 'ps')

    def _s_implicit_deps_c0_s4(self):
        self._h_succeed(self._h_get('ps'))

    def _s_implicit_deps_c1(self):
        self._h_succeed([])

    def _r_order_only_deps(self):
        self._h_choose([self._s_order_only_deps_c0,
                        self._s_order_only_deps_c1])

    def _s_order_only_deps_c0(self):
        self._h_scope('_s_order_only_deps_c0', [self._r_ws,
                                                lambda: self._h_str('||', 2),
                                                self._r_ws,
                                                self._s_order_only_deps_c0_s3,
                                                self._s_order_only_deps_c0_s4])

    def _s_order_only_deps_c0_s3(self):
        self._h_bind(self._r_paths, 'ps')

    def _s_order_only_deps_c0_s4(self):
        self._h_succeed(self._h_get('ps'))

    def _s_order_only_deps_c1(self):
        self._h_succeed([])

    def _r_empty_line(self):
        self._r_eol()

    def _r_eol(self):
        self._h_seq([self._r_ws,
                     self._s_eol_s1])

    def _s_eol_s1(self):
        self._h_choose([self._r_comment,
                        lambda: self._h_ch('\n')])

    def _r_ws(self):
        self._h_star(self._s_ws_p, [])

    def _s_ws_p(self):
        self._h_choose([lambda: self._h_ch(' '),
                        self._s_ws_p_c1])

    def _s_ws_p_c1(self):
        self._h_seq([lambda: self._h_ch('$'),
                     lambda: self._h_ch('\n')])

    def _r_comment(self):
        self._h_seq([lambda: self._h_ch('#'),
                     self._s_comment_s1,
                     lambda: self._h_ch('\n')])

    def _s_comment_s1(self):
        self._h_star(self._s_comment_s1_p, [])

    def _s_comment_s1_p(self):
        self._h_seq([self._s_comment_s1_p_s0,
                     self._r_anything])

    def _s_comment_s1_p_s0(self):
        self._h_not(self._s_comment_s1_p_s0_n)

    def _s_comment_s1_p_s0_n(self):
        self._h_ch('\n')

    def _r_anything(self):
        if self.pos < self.end:
            self._h_succeed(self.msg[self.pos], self.pos + 1)
        else:
            self._h_fail()

    def _r_end(self):
        if self.pos == self.end:
            self._h_succeed(None)
        else:
            self._h_fail()

    def _f_join(self, s, vs):
        return s.join(vs)

    def _h_bind(self, rule, var):
        rule()
        if not self.failed:
            self._h_set(var, self.val)

    def _h_ch(self, ch):
        p = self.pos
        if p < self.end and self.msg[p] == ch:
            self._h_succeed(ch, p + 1)
        else:
            self._h_fail()

    def _h_choose(self, rules):
        p = self.pos
        for rule in rules[:-1]:
            rule()
            if not self.failed:
                return
            self._h_rewind(p)
        rules[-1]()

    def _h_err(self):
        lineno = 1
        colno = 1
        for ch in self.msg[:self.errpos]:
            if ch == '\n':
                lineno += 1
                colno = 1
            else:
                colno += 1
        if self.errpos == len(self.msg):
            thing = 'end of input'
        else:
            thing = '"%s"' % self.msg[self.errpos]
        err_str = '%s:%d Unexpected %s at column %d' % (
            self.fname, lineno, thing, colno)
        return None, err_str, self.errpos

    def _h_fail(self):
        self.val = None
        self.failed = True
        if self.pos >= self.errpos:
            self.errpos = self.pos

    def _h_get(self, var):
        return self._scopes[-1][1][var]

    def _h_not(self, rule):
        p = self.pos
        rule()
        if self.failed:
            self._h_succeed(None, p)
        else:
            self._h_rewind(p)
            self._h_fail()

    def _h_plus(self, rule):
        vs = []
        rule()
        vs.append(self.val)
        if self.failed:
            return
        self._h_star(rule, vs)

    def _h_range(self, i, j):
        p = self.pos
        if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
            self._h_succeed(self.msg[p], self.pos + 1)
        else:
            self._h_fail()

    def _h_rewind(self, pos):
        self._h_succeed(None, pos)

    def _h_scope(self, name, rules):
        self._scopes.append((name, {}))
        for rule in rules:
            rule()
            if self.failed:
                self._scopes.pop()
                return
        self._scopes.pop()

    def _h_seq(self, rules):
        for rule in rules:
            rule()
            if self.failed:
                return

    def _h_set(self, var, val):
        self._scopes[-1][1][var] = val

    def _h_star(self, rule, vs):
        vs = vs or []
        while not self.failed:
            p = self.pos
            rule()
            if self.failed:
                self._h_rewind(p)
                break
            else:
                vs.append(self.val)
        self._h_succeed(vs)

    def _h_str(self, s, l):
        p = self.pos
        if (p + l <= self.end) and self.msg[p:p + l] == s:
            self._h_succeed(s, self.pos + l)
        else:
            self._h_fail()

    def _h_succeed(self, v, newpos=None):
        self.val = v
        self.failed = False
        if newpos is not None:
            self.pos = newpos


def main(argv=sys.argv[1:], stdin=sys.stdin, stdout=sys.stdout,
         stderr=sys.stderr, exists=os.path.exists, opener=open):
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('file', nargs='?')
    args = arg_parser.parse_args(argv)

    if not args.file or args.file[1] == '-':
        fname = '<stdin>'
        fp = stdin
    elif not exists(args.file):
        print('Error: file "%s" not found.' % args.file, file=stderr)
        return 1
    else:
        fname = args.file
        fp = opener(fname)

    msg = fp.read()
    obj, err, _ = Parser(msg, fname).parse()
    if err:
        print(err, file=stderr)
        return 1
    print(json.dumps(obj), file=stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
