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
        self._regexps = {}
        self._scopes = []

    def parse(self):
        self._r_grammar()
        if self.failed:
            return self._h_err()
        return self.val, None, self.pos

    def _r_grammar(self):
        self._h_scope('grammar', [lambda: self._h_bind(lambda: self._h_star(self._s_grammar_s0_l_s), 'ds'),
                                  lambda: self._h_star(self._r_empty_line),
                                  self._r_end,
                                  lambda: self._h_succeed(self._h_get('ds'))])

    def _s_grammar_s0_l_s(self):
        self._h_seq([lambda: self._h_star(self._r_empty_line),
                     self._r_decl])

    def _r_decl(self):
        self._h_choose([self._r_build,
                        self._r_rule,
                        self._r_var,
                        self._r_subninja,
                        self._r_include,
                        self._r_pool,
                        self._r_default])

    def _r_build(self):
        self._h_scope('build', [lambda: self._h_str('build', 5),
                                self._r_ws,
                                lambda: self._h_bind(self._r_paths, 'os'),
                                lambda: self._h_bind(self._r_imps, 'ios'),
                                lambda: self._h_opt(self._r_ws),
                                lambda: self._h_ch(':'),
                                lambda: self._h_opt(self._r_ws),
                                lambda: self._h_bind(self._r_name, 'n'),
                                lambda: self._h_bind(self._r_exps, 'es'),
                                lambda: self._h_bind(self._r_imps, 'is'),
                                lambda: self._h_bind(self._r_ords, 'ods'),
                                self._r_eol,
                                lambda: self._h_bind(self._r_vars, 'vs'),
                                lambda: self._h_succeed(['build', self._h_get('os'), self._h_get('ios'), self._h_get('n'), self._h_get('es'), self._h_get('is'), self._h_get('ods'), self._h_get('vs')])])

    def _r_exps(self):
        self._h_choose([self._s_exps_c0,
                        lambda: self._h_succeed([])])

    def _s_exps_c0(self):
        self._h_scope('exps', [self._r_ws,
                               lambda: self._h_bind(self._r_paths, 'ps'),
                               lambda: self._h_succeed(self._h_get('ps'))])

    def _r_imps(self):
        self._h_choose([self._s_imps_c0,
                        lambda: self._h_succeed([])])

    def _s_imps_c0(self):
        self._h_scope('imps', [lambda: self._h_opt(self._r_ws),
                               lambda: self._h_ch('|'),
                               lambda: self._h_opt(self._r_ws),
                               lambda: self._h_bind(self._r_paths, 'ps'),
                               lambda: self._h_succeed(self._h_get('ps'))])

    def _r_ords(self):
        self._h_choose([self._s_ords_c0,
                        lambda: self._h_succeed([])])

    def _s_ords_c0(self):
        self._h_scope('ords', [lambda: self._h_opt(self._r_ws),
                               lambda: self._h_str('||', 2),
                               lambda: self._h_opt(self._r_ws),
                               lambda: self._h_bind(self._r_paths, 'ps'),
                               lambda: self._h_succeed(self._h_get('ps'))])

    def _r_rule(self):
        self._h_scope('rule', [lambda: self._h_str('rule', 4),
                               self._r_ws,
                               lambda: self._h_bind(self._r_name, 'n'),
                               self._r_eol,
                               lambda: self._h_bind(lambda: self._h_star(self._s_rule_s4_l_s), 'vs'),
                               lambda: self._h_succeed(['rule', self._h_get('n'), self._h_get('vs')])])

    def _s_rule_s4_l_s(self):
        self._h_seq([self._r_ws,
                     self._r_var])

    def _r_vars(self):
        self._h_star(self._s_vars_s)

    def _s_vars_s(self):
        self._h_seq([self._r_ws,
                     self._r_var])

    def _r_var(self):
        self._h_scope('var', [lambda: self._h_bind(self._r_name, 'n'),
                              lambda: self._h_opt(self._r_ws),
                              lambda: self._h_ch('='),
                              lambda: self._h_opt(self._r_ws),
                              lambda: self._h_bind(self._r_value, 'v'),
                              self._r_eol,
                              lambda: self._h_succeed(['var', self._h_get('n'), self._h_get('v')])])

    def _r_value(self):
        self._h_scope('value', [lambda: self._h_bind(lambda: self._h_star(self._s_value_s0_l_s), 'vs'),
                                lambda: self._h_succeed(self._f_cat(self._h_get('vs')))])

    def _s_value_s0_l_s(self):
        self._h_seq([lambda: self._h_not(self._r_eol),
                     self._s_value_s0_l_s_s1])

    def _s_value_s0_l_s_s1(self):
        self._h_choose([self._s_value_s0_l_s_s1_c0,
                        self._r_anything])

    def _s_value_s0_l_s_s1_c0(self):
        self._h_seq([self._r_ws,
                     lambda: self._h_succeed(' ')])

    def _r_subninja(self):
        self._h_scope('subninja', [lambda: self._h_str('subninja', 8),
                                   self._r_ws,
                                   lambda: self._h_bind(self._r_path, 'p'),
                                   lambda: self._h_succeed(['subninja', self._h_get('p')])])

    def _r_include(self):
        self._h_scope('include', [lambda: self._h_str('include', 7),
                                  self._r_ws,
                                  lambda: self._h_bind(self._r_path, 'p'),
                                  lambda: self._h_succeed(['include', self._h_get('p')])])

    def _r_pool(self):
        self._h_scope('pool', [lambda: self._h_str('pool', 4),
                               self._r_ws,
                               lambda: self._h_bind(self._r_name, 'n'),
                               self._r_eol,
                               lambda: self._h_bind(lambda: self._h_star(self._s_pool_s4_l_s), 'vars'),
                               lambda: self._h_succeed(['pool', self._h_get('n'), self._h_get('vars')])])

    def _s_pool_s4_l_s(self):
        self._h_seq([self._r_ws,
                     self._r_var])

    def _r_default(self):
        self._h_scope('default', [lambda: self._h_str('default', 7),
                                  self._r_ws,
                                  lambda: self._h_bind(self._r_paths, 'ps'),
                                  self._r_eol,
                                  lambda: self._h_succeed(['default', self._h_get('ps')])])

    def _r_paths(self):
        self._h_scope('paths', [lambda: self._h_bind(self._r_path, 'hd'),
                                lambda: self._h_bind(lambda: self._h_star(self._s_paths_s1_l_s), 'tl'),
                                lambda: self._h_succeed([self._h_get('hd')] + self._h_get('tl'))])

    def _s_paths_s1_l_s(self):
        self._h_seq([self._r_ws,
                     self._r_path])

    def _r_path(self):
        self._h_scope('path', [lambda: self._h_bind(lambda: self._h_plus(self._s_path_s0_l_p), 'ps'),
                               lambda: self._h_succeed(self._f_cat(self._h_get('ps')))])

    def _s_path_s0_l_p(self):
        self._h_choose([self._r_esc,
                        self._s_path_s0_l_p_c1])

    def _s_path_s0_l_p_c1(self):
        self._h_seq([lambda: self._h_not(self._r_path_sep),
                     self._r_anything])

    def _r_esc(self):
        self._h_choose([self._s_esc_c0,
                        self._s_esc_c1,
                        self._s_esc_c2,
                        self._s_esc_c3,
                        self._s_esc_c4,
                        self._s_esc_c5])

    def _s_esc_c0(self):
        self._h_seq([lambda: self._h_str('$ ', 2),
                     lambda: self._h_succeed(' ')])

    def _s_esc_c1(self):
        self._h_seq([lambda: self._h_str('$\n', 2),
                     lambda: self._h_star(lambda: self._h_ch(' ')),
                     lambda: self._h_succeed('')])

    def _s_esc_c2(self):
        self._h_seq([lambda: self._h_str('$:', 2),
                     lambda: self._h_succeed(':')])

    def _s_esc_c3(self):
        self._h_scope('esc', [lambda: self._h_ch('$'),
                              lambda: self._h_bind(self._r_name, 'n'),
                              lambda: self._h_succeed('$' + self._h_get('n'))])

    def _s_esc_c4(self):
        self._h_scope('esc', [lambda: self._h_str('${', 2),
                              lambda: self._h_bind(self._r_name, 'n'),
                              lambda: self._h_ch('}'),
                              lambda: self._h_succeed('${' + self._h_get('n') + '}')])

    def _s_esc_c5(self):
        self._h_seq([lambda: self._h_str('$$', 2),
                     lambda: self._h_succeed('$')])

    def _r_name(self):
        self._h_scope('name', [lambda: self._h_bind(self._r_letter, 'hd'),
                               lambda: self._h_bind(lambda: self._h_star(self._s_name_s1_l_s), 'tl'),
                               lambda: self._h_succeed(self._h_get('hd') + self._f_cat(self._h_get('tl')))])

    def _s_name_s1_l_s(self):
        self._h_choose([self._r_letter,
                        self._r_digit,
                        lambda: self._h_ch('_')])

    def _r_letter(self):
        self._h_choose([lambda: self._h_range('a', 'z'),
                        lambda: self._h_range('A', 'Z')])

    def _r_digit(self):
        self._h_range('0', '9')

    def _r_path_sep(self):
        self._h_choose([lambda: self._h_ch(' '),
                        lambda: self._h_ch(':'),
                        lambda: self._h_ch('|'),
                        lambda: self._h_ch('\n')])

    def _r_empty_line(self):
        self._r_eol()

    def _r_eol(self):
        self._h_seq([lambda: self._h_opt(self._r_ws),
                     lambda: self._h_opt(self._r_comment),
                     lambda: self._h_ch('\n')])

    def _r_ws(self):
        self._h_plus(self._s_ws_p)

    def _s_ws_p(self):
        self._h_choose([lambda: self._h_ch(' '),
                        lambda: self._h_str('$\n', 2)])

    def _r_comment(self):
        self._h_seq([lambda: self._h_ch('#'),
                     lambda: self._h_star(self._s_comment_s1_s)])

    def _s_comment_s1_s(self):
        self._h_seq([lambda: self._h_not(lambda: self._h_ch('\n')),
                     self._r_anything])

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

    def _f_cat(self, strs):
        return ''.join(strs)

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
            thing = '%s' % repr(self.msg[self.errpos])[1:]
        err_str = '%s:%d Unexpected %s at column %d' % (self.fname, lineno,
                                                        thing, colno)
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

    def _h_opt(self, rule):
        p = self.pos
        rule()
        if self.failed:
            self._h_succeed([], p)
        else:
            self._h_succeed([self.val])

    def _h_plus(self, rule):
        vs = []
        rule()
        if self.failed:
            return
        vs = [self.val]
        while not self.failed:
            p = self.pos
            rule()
            if self.failed:
                self._h_rewind(p)
                break
            else:
                vs.append(self.val)
        self._h_succeed(vs)

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

    def _h_star(self, rule):
        vs = []
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
