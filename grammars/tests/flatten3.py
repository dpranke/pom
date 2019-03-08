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

    def parse(self):
        self._r_grammar()
        if self.failed:
            return self._h_err()
        return self.val, None, self.pos

    def _r_grammar(self):
        self._h_seq([lambda: self._h_re('(?!Bug\\([a-z]+\\))(?!( |\n|#)).+'),
                     self._r_end])

    def _r_bug(self):
        self._h_re('Bug\\([a-z]+\\)')

    def _r_id(self):
        self._h_re('(?!( |\n|#)).+')

    def _r_end(self):
        if self.pos == self.end:
            self._h_succeed(None)
        else:
            self._h_fail()

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

    def _h_seq(self, rules):
        for rule in rules:
            rule()
            if self.failed:
                return

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
