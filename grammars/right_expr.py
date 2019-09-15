#!/usr/bin/env python

from __future__ import print_function

import argparse
import json
import os
import re
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
        self._h_scope('grammar', [lambda: self._h_bind(self._r_expr, '_1'),
                                  lambda: self._h_re('\n'),
                                  self._r_end,
                                  lambda: self._h_succeed(self._h_get('_1'))])

    def _r_expr(self):
        self._h_choose([self._s_expr_c0,
                        self._s_expr_c1,
                        self._s_expr_c2,
                        self._s_expr_c3])

    def _s_expr_c0(self):
        self._h_scope('expr', [lambda: self._h_bind(lambda: self._h_capture(self._r_num), '_1'),
                               lambda: self._h_ch('*'),
                               lambda: self._h_bind(self._r_expr, '_3'),
                               lambda: self._h_succeed([self._h_get('_1'), '*', self._h_get('_3')])])

    def _s_expr_c1(self):
        self._h_scope('expr', [lambda: self._h_bind(lambda: self._h_capture(self._r_num), '_1'),
                               lambda: self._h_ch('+'),
                               lambda: self._h_bind(self._r_expr, '_3'),
                               lambda: self._h_succeed([self._h_get('_1'), '+', self._h_get('_3')])])

    def _s_expr_c2(self):
        self._h_scope('expr', [lambda: self._h_bind(lambda: self._h_capture(self._r_num), '_1'),
                               lambda: self._h_ch('-'),
                               lambda: self._h_bind(self._r_expr, '_3'),
                               lambda: self._h_succeed([self._h_get('_1'), '-', self._h_get('_3')])])

    def _s_expr_c3(self):
        self._h_scope('expr', [lambda: self._h_bind(lambda: self._h_capture(self._r_num), '_1'),
                               lambda: self._h_succeed(self._h_get('_1'))])

    def _r_num(self):
        self._h_re('([0-9])+')

    def _r_end(self):
        if self.pos == self.end:
            self._h_succeed(None)
        else:
            self._h_fail()

    def _h_bind(self, rule, var):
        rule()
        if not self.failed:
            self._h_set(var, self.val)

    def _h_capture(self, rule):
        start = self.pos
        rule()
        if not self.failed:
            self._h_succeed(self.msg[start:self.pos],
                            self.pos)

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
            thing = repr(self.msg[self.errpos])
            if thing[0] == 'u':
                thing = thing[1:]
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

    def _h_re(self, pattern):
        try:
            pat = self._regexps[pattern]
        except KeyError as e:
            pat = self._regexps.setdefault(pattern, re.compile(pattern, flags=re.DOTALL))
        m = pat.match(self.msg, self.pos, self.end)
        if m:
            self._h_succeed(m.group(0), self.pos + len(m.group(0)))
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

    def _h_set(self, var, val):
        self._scopes[-1][1][var] = val

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

    if not args.file or args.file[0] == '-':
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
