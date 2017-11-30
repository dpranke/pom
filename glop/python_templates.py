# Copyright 2017 Dirk Pranke. All rights reserved.
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


IMPORTS = {'import sys'}

TEXT = '''\
{main_header}{imports}

if sys.version_info[0] < 3:
    # pylint: disable=redefined-builtin
    chr = unichr
    str = unicode

# pylint: disable=line-too-long


class {classname}(object):
    def __init__(self, msg, fname):
        self.msg = str(msg)
        self.end = len(self.msg)
        self.fname = fname
        self.val = None
        self.pos = 0
        self.failed = False
        self.errpos = 0
{optional_fields}
    def parse(self):
        self.{starting_rule}()
        if self.failed:
            return self._h_err()
        return self.val, None, self.pos
{methods}{main_footer}'''

MAIN_IMPORTS = {'import argparse', 'import json', 'import os', 'import sys'}

MAIN_HEADER = '''\
#!/usr/bin/env python

from __future__ import print_function

'''

MAIN_FOOTER = '''\


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
    obj, err, _ = {classname}(msg, fname).parse()
    if err:
        print(err, file=stderr)
        return 1
    print(json.dumps(obj), file=stdout)
    return 0


if __name__ == '__main__':
    sys.exit(main())
'''


METHOD = '''\

    def {rule}(self):
{lines}
'''

IDENTIFIERS = {
    'false': 'False',
    'null': 'None',
    'true': 'True',
}


METHODS = {
    # BUILT-IN RULES
    '_r_anything': {
        'needs': ['_h_fail', '_h_succeed'],
        'body': '''\
        def _r_anything(self):
            if self.pos < self.end:
                self._h_succeed(self.msg[self.pos], self.pos + 1)
            else:
                self._h_fail()
            ''',
    },
    '_r_end': {
        'needs': ['_h_fail', '_h_succeed'],
        'body': '''\
        def _r_end(self):
            if self.pos == self.end:
                self._h_succeed(None)
            else:
                self._h_fail()
        ''',
    },

    # BUILT-IN FUNCTIONS
    '_f_cat': {
        'body': '''\
        def _f_cat(self, strs):
            return ''.join(strs)
        '''
    },
    '_f_is_unicat': {
        'imports': ['import unicodedata'],
        'body': '''\
        def _f_is_unicat(self, var, cat):
            return unicodedata.category(var) == cat
        ''',
    },
    '_f_itou': {
        'body': '''\
        def _f_itou(self, n):
            return chr(n)
        ''',
    },
    '_f_join': {
        'body': '''\
        def _f_join(self, s, vs):
            return s.join(vs)
        ''',
    },
    '_f_utoi': {
        'body': '''\
        def _f_utoi(self, s):
            return int(s)
        ''',
    },
    '_f_xtoi': {
        'params': ['s'],
        'body': '''\
        def _f_xtoi(self, s):
            return int(s, base=16)
        ''',
    },
    '_f_xtou': {
        'body': '''\
        def _f_xtou(self, s):
            return chr(int(s, base=16))
        ''',
    },
 
    # HELPER METHODS
    '_h_bind': {
        'needs': ['_h_set'],
        'body': '''\
        def _h_bind(self, rule, var):
            rule()
            if not self.failed:
                self._h_set(var, self.val)
        ''',
    },
    '_h_ch': {
        'needs': ['_h_succeed', '_h_fail'], 
        'body': '''\
        def _h_ch(self, ch):
            p = self.pos
            if p < self.end and self.msg[p] == ch:
                self._h_succeed(ch, p + 1)
            else:
                self._h_fail()
        ''',
    },
    '_h_choose': {
        'needs': ['_h_rewind'],
        'body': '''\
        def _h_choose(self, rules):
            p = self.pos
            for rule in rules[:-1]:
                rule()
                if not self.failed:
                    return
                self._h_rewind(p)
            rules[-1]()
        ''',
    },
    '_h_err': {
        'body': '''\
        def _h_err(self):
            lineno = 1
            colno = 1
            for ch in self.msg[:self.errpos]:
                if ch == '\\n':
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
        ''',
    },
    '_h_fail': {
        'body': '''\
        def _h_fail(self):
            self.val = None
            self.failed = True
            if self.pos >= self.errpos:
                self.errpos = self.pos
        ''',
    },
    '_h_get': {
        'body': '''\
        def _h_get(self, var):
            return self._scopes[-1][1][var]
        ''',
    },
    '_h_memo': {
        'body': '''\
        def _h_memo(self, rule, rule_name):
            r = self._cache.get((rule_name, self.pos))
            if r is not None:
                self.val, self.failed, self.pos = r
                return
            pos = self.pos
            rule()
            self._cache[(rule_name, pos)] = (self.val, self.failed, self.pos)
        ''',
    },
    '_h_not': {
        'needs': ['_h_fail', '_h_rewind', '_h_succeed'],
        'body': '''\
        def _h_not(self, rule):
            p = self.pos
            rule()
            if self.failed:
                self._h_succeed(None, p)
            else:
                self._h_rewind(p)
                self._h_fail()
        ''',
    },
    '_h_opt': {
        'needs': ['_h_succeed'],
        'body': '''\
        def _h_opt(self, rule):
            p = self.pos
            rule()
            if self.failed:
                self._h_succeed([], p)
            else:
                self._h_succeed([self.val])
        ''',
    },
    '_h_plus': {
        'needs': ['_h_star'],
        'body': '''\
        def _h_plus(self, rule):
            vs = []
            rule()
            vs.append(self.val)
            if self.failed:
                return
            self._h_star(rule, vs)
        '''
    },
    '_h_range': {
        'needs': ['_h_fail', '_h_succeed'],
        'body': '''\
        def _h_range(self, i, j):
            p = self.pos
            if p != self.end and ord(i) <= ord(self.msg[p]) <= ord(j):
                self._h_succeed(self.msg[p], self.pos + 1)
            else:
                self._h_fail()
        ''',
    },
    '_h_re': {
        'imports': ['import re'],
        'needs': ['_h_succeed', '_h_fail'],
        'body': '''\
        def _h_re(self, pattern):
            m = re.match(pattern, self.msg[self.pos:], flags=re.DOTALL)
            if m:
              self._h_succeed(m.group(0), self.pos + len(m.group(0)))
            else:
              self._h_fail()
        ''',
    },
    '_h_rewind': {
        'needs': ['_h_succeed'],
        'body': '''\
        def _h_rewind(self, pos):
            self._h_succeed(None, pos)
        '''
    },
    '_h_scope': {
        'body': '''\
        def _h_scope(self, name, rules):
            self._scopes.append((name, {}))
            for rule in rules:
                rule()
                if self.failed:
                    self._scopes.pop()
                    return
            self._scopes.pop()
        '''
    },
    '_h_seq': {
        'body': '''\
        def _h_seq(self, rules):
            for rule in rules:
                rule()
                if self.failed:
                    return
        ''',
    },
    '_h_set': {
        'body': '''\
        def _h_set(self, var, val):
            self._scopes[-1][1][var] = val
        ''',
    },
    '_h_star': {
        'needs': ['_h_rewind', '_h_succeed'],
        'body': '''\
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
        ''',
    },
    '_h_str': {
        'needs': ['_h_fail', '_h_succeed'],
        'body': '''\
        def _h_str(self, s, l):
            p = self.pos
            if (p + l <= self.end) and self.msg[p:p + l] == s:
                self._h_succeed(s, self.pos + l)
            else:
                self._h_fail()
        ''',
    },
    '_h_succeed': {
        'body': '''\
        def _h_succeed(self, v, newpos=None):
            self.val = v
            self.failed = False
            if newpos is not None:
                self.pos = newpos
        ''',
    },
}
