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
        self._cache = {}

    def parse(self):
        self._r_grammar()
        if self.failed:
            return self._h_err()
        return self.val, None, self.pos

    def _r_grammar(self):
        self._h_memo(lambda: self._h_scope('grammar', [lambda: self._h_bind(lambda: self._h_star(self._s_grammar_s0_l_s), '_1'),
                                                       lambda: self._h_re('( |\t|(\r\n|\r|\n)|(//(?!(\r\n|\r|\n)).*|/\\*(?!\\*/).*\\*/))*'),
                                                       self._r_end,
                                                       lambda: self._h_succeed(['rules', self._h_get('_1')])]), '_r_grammar')

    def _s_grammar_s0_l_s(self):
        self._h_seq([self._r_sp,
                     self._r_rule])

    def _r_sp(self):
        self._h_memo(lambda: self._h_re('( |\t|(\r\n|\r|\n)|(//(?!(\r\n|\r|\n)).*|/\\*(?!\\*/).*\\*/))*'), '_r_sp')

    def _r_ws(self):
        self._h_memo(lambda: self._h_re('( |\t|(\r\n|\r|\n)|(//(?!(\r\n|\r|\n)).*|/\\*(?!\\*/).*\\*/))'), '_r_ws')

    def _r_eol(self):
        self._h_memo(lambda: self._h_re('(\r\n|\r|\n)'), '_r_eol')

    def _r_comment(self):
        self._h_memo(lambda: self._h_re('(//(?!(\r\n|\r|\n)).*|/\\*(?!\\*/).*\\*/)'), '_r_comment')

    def _r_rule(self):
        self._h_memo(lambda: self._h_scope('rule', [lambda: self._h_bind(self._r_ident, '_1'),
                                                    lambda: self._h_re('( |\t|(\r\n|\r|\n)|(//(?!(\r\n|\r|\n)).*|/\\*(?!\\*/).*\\*/))*=( |\t|(\r\n|\r|\n)|(//(?!(\r\n|\r|\n)).*|/\\*(?!\\*/).*\\*/))*'),
                                                    lambda: self._h_bind(self._r_choice, '_5'),
                                                    lambda: self._h_re('( |\t|(\r\n|\r|\n)|(//(?!(\r\n|\r|\n)).*|/\\*(?!\\*/).*\\*/))*,?'),
                                                    lambda: self._h_succeed(['rule', self._h_get('_1'), self._h_get('_5')])]), '_r_rule')

    def _r_ident(self):
        self._h_memo(lambda: self._h_capture(self._s_ident_c), '_r_ident')

    def _s_ident_c(self):
        self._h_seq([self._r_id_start,
                     lambda: self._h_star(self._r_id_continue)])

    def _r_id_start(self):
        self._h_memo(lambda: self._h_re('([a-z]|[A-Z]|_)'), '_r_id_start')

    def _r_id_continue(self):
        self._h_memo(lambda: self._h_re('(([a-z]|[A-Z]|_)|[0-9])'), '_r_id_continue')

    def _r_choice(self):
        self._h_memo(lambda: self._h_scope('choice', [lambda: self._h_bind(self._r_seq, '_1'),
                                                      lambda: self._h_bind(lambda: self._h_star(self._s_choice_s1_l_s), '_2'),
                                                      lambda: self._h_succeed(['choice', [self._h_get('_1')] + self._h_get('_2')])]), '_r_choice')

    def _s_choice_s1_l_s(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch('|'),
                     self._r_sp,
                     self._r_seq])

    def _r_seq(self):
        self._h_memo(lambda: self._h_choose([self._s_seq_c0,
                                             lambda: self._h_succeed(['empty'])]), '_r_seq')

    def _s_seq_c0(self):
        self._h_scope('seq', [lambda: self._h_bind(self._r_expr, '_1'),
                              lambda: self._h_bind(lambda: self._h_star(self._s_seq_c0_s1_l_s), '_2'),
                              lambda: self._h_succeed(['seq', [self._h_get('_1')] + self._h_get('_2')])])

    def _s_seq_c0_s1_l_s(self):
        self._h_seq([self._r_ws,
                     self._r_sp,
                     self._r_expr])

    def _r_expr(self):
        self._h_memo(lambda: self._h_choose([self._s_expr_c0,
                                             self._r_post_expr]), '_r_expr')

    def _s_expr_c0(self):
        self._h_scope('expr', [lambda: self._h_bind(self._r_post_expr, '_1'),
                               lambda: self._h_ch(':'),
                               lambda: self._h_bind(self._r_ident, '_3'),
                               lambda: self._h_succeed(['label', self._h_get('_1'), self._h_get('_3')])])

    def _r_post_expr(self):
        self._h_memo(lambda: self._h_choose([self._s_post_expr_c0,
                                             self._r_prim_expr]), '_r_post_expr')

    def _s_post_expr_c0(self):
        self._h_scope('post_expr', [lambda: self._h_bind(self._r_prim_expr, '_1'),
                                    lambda: self._h_bind(self._r_post_op, '_2'),
                                    lambda: self._h_succeed([self._h_get('_2'), self._h_get('_1')])])

    def _r_post_op(self):
        self._h_memo(lambda: self._h_choose([self._s_post_op_c0,
                                             self._s_post_op_c1,
                                             self._s_post_op_c2]), '_r_post_op')

    def _s_post_op_c0(self):
        self._h_seq([lambda: self._h_ch('?'),
                     lambda: self._h_succeed('opt')])

    def _s_post_op_c1(self):
        self._h_seq([lambda: self._h_ch('*'),
                     lambda: self._h_succeed('star')])

    def _s_post_op_c2(self):
        self._h_seq([lambda: self._h_ch('+'),
                     lambda: self._h_succeed('plus')])

    def _r_prim_expr(self):
        self._h_memo(lambda: self._h_choose([self._s_prim_expr_c0,
                                             self._s_prim_expr_c1,
                                             self._s_prim_expr_c2,
                                             self._s_prim_expr_c3,
                                             self._s_prim_expr_c4,
                                             self._s_prim_expr_c5,
                                             self._s_prim_expr_c6,
                                             self._s_prim_expr_c7,
                                             self._s_prim_expr_c8,
                                             self._s_prim_expr_c9]), '_r_prim_expr')

    def _s_prim_expr_c0(self):
        self._h_scope('prim_expr', [lambda: self._h_bind(self._r_lit, '_1'),
                                    self._r_sp,
                                    lambda: self._h_str('..', 2),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_lit, '_5'),
                                    lambda: self._h_succeed(['range', self._h_get('_1'), self._h_get('_5')])])

    def _s_prim_expr_c1(self):
        self._h_scope('prim_expr', [lambda: self._h_bind(self._r_lit, '_1'),
                                    lambda: self._h_succeed(self._h_get('_1'))])

    def _s_prim_expr_c2(self):
        self._h_scope('prim_expr', [lambda: self._h_bind(self._r_ident, '_1'),
                                    lambda: self._h_not(self._s_prim_expr_c2_s1_n),
                                    lambda: self._h_succeed(['apply', self._h_get('_1')])])

    def _s_prim_expr_c2_s1_n(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch('=')])

    def _s_prim_expr_c3(self):
        self._h_scope('prim_expr', [lambda: self._h_ch('('),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_choice, '_3'),
                                    self._r_sp,
                                    lambda: self._h_ch(')'),
                                    lambda: self._h_succeed(['paren', self._h_get('_3')])])

    def _s_prim_expr_c4(self):
        self._h_scope('prim_expr', [lambda: self._h_ch('~'),
                                    lambda: self._h_bind(self._r_prim_expr, '_2'),
                                    lambda: self._h_succeed(['not', self._h_get('_2')])])

    def _s_prim_expr_c5(self):
        self._h_scope('prim_expr', [lambda: self._h_str('->', 2),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_ll_expr, '_3'),
                                    lambda: self._h_succeed(['action', self._h_get('_3')])])

    def _s_prim_expr_c6(self):
        self._h_seq([lambda: self._h_str('{}', 2),
                     lambda: self._h_succeed(['pos'])])

    def _s_prim_expr_c7(self):
        self._h_scope('prim_expr', [lambda: self._h_ch('{'),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_choice, '_3'),
                                    self._r_sp,
                                    lambda: self._h_ch('}'),
                                    lambda: self._h_succeed(['capture', self._h_get('_3')])])

    def _s_prim_expr_c8(self):
        self._h_scope('prim_expr', [lambda: self._h_str('={', 2),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_ll_expr, '_3'),
                                    self._r_sp,
                                    lambda: self._h_ch('}'),
                                    lambda: self._h_succeed(['eq', self._h_get('_3')])])

    def _s_prim_expr_c9(self):
        self._h_scope('prim_expr', [lambda: self._h_str('?{', 2),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_ll_expr, '_3'),
                                    self._r_sp,
                                    lambda: self._h_ch('}'),
                                    lambda: self._h_succeed(['pred', self._h_get('_3')])])

    def _r_lit(self):
        self._h_memo(lambda: self._h_choose([self._s_lit_c0,
                                             self._s_lit_c1]), '_r_lit')

    def _s_lit_c0(self):
        self._h_scope('lit', [self._r_squote,
                              lambda: self._h_bind(lambda: self._h_star(self._r_sqchar), '_2'),
                              self._r_squote,
                              lambda: self._h_succeed(['lit', self._f_cat(self._h_get('_2'))])])

    def _s_lit_c1(self):
        self._h_scope('lit', [self._r_dquote,
                              lambda: self._h_bind(lambda: self._h_star(self._r_dqchar), '_2'),
                              self._r_dquote,
                              lambda: self._h_succeed(['lit', self._f_cat(self._h_get('_2'))])])

    def _r_sqchar(self):
        self._h_memo(lambda: self._h_choose([self._s_sqchar_c0,
                                             self._s_sqchar_c1]), '_r_sqchar')

    def _s_sqchar_c0(self):
        self._h_scope('sqchar', [self._r_bslash,
                                 lambda: self._h_bind(self._r_esc_char, '_2'),
                                 lambda: self._h_succeed(self._h_get('_2'))])

    def _s_sqchar_c1(self):
        self._h_scope('sqchar', [lambda: self._h_not(self._r_squote),
                                 lambda: self._h_bind(self._r_anything, '_2'),
                                 lambda: self._h_succeed(self._h_get('_2'))])

    def _r_dqchar(self):
        self._h_memo(lambda: self._h_choose([self._s_dqchar_c0,
                                             self._s_dqchar_c1]), '_r_dqchar')

    def _s_dqchar_c0(self):
        self._h_scope('dqchar', [self._r_bslash,
                                 lambda: self._h_bind(self._r_esc_char, '_2'),
                                 lambda: self._h_succeed(self._h_get('_2'))])

    def _s_dqchar_c1(self):
        self._h_scope('dqchar', [lambda: self._h_not(self._r_dquote),
                                 lambda: self._h_bind(self._r_anything, '_2'),
                                 lambda: self._h_succeed(self._h_get('_2'))])

    def _r_bslash(self):
        self._h_memo(lambda: self._h_ch('\\'), '_r_bslash')

    def _r_squote(self):
        self._h_memo(lambda: self._h_ch("'"), '_r_squote')

    def _r_dquote(self):
        self._h_memo(lambda: self._h_ch('"'), '_r_dquote')

    def _r_esc_char(self):
        self._h_memo(lambda: self._h_choose([self._s_esc_char_c0,
                                             self._s_esc_char_c1,
                                             self._s_esc_char_c2,
                                             self._s_esc_char_c3,
                                             self._s_esc_char_c4,
                                             self._s_esc_char_c5,
                                             self._s_esc_char_c6,
                                             self._s_esc_char_c7,
                                             self._s_esc_char_c8,
                                             self._s_esc_char_c9,
                                             self._s_esc_char_c10]), '_r_esc_char')

    def _s_esc_char_c0(self):
        self._h_seq([lambda: self._h_ch('b'),
                     lambda: self._h_succeed('\b')])

    def _s_esc_char_c1(self):
        self._h_seq([lambda: self._h_ch('f'),
                     lambda: self._h_succeed('\f')])

    def _s_esc_char_c2(self):
        self._h_seq([lambda: self._h_ch('n'),
                     lambda: self._h_succeed('\n')])

    def _s_esc_char_c3(self):
        self._h_seq([lambda: self._h_ch('r'),
                     lambda: self._h_succeed('\r')])

    def _s_esc_char_c4(self):
        self._h_seq([lambda: self._h_ch('t'),
                     lambda: self._h_succeed('\t')])

    def _s_esc_char_c5(self):
        self._h_seq([lambda: self._h_ch('v'),
                     lambda: self._h_succeed('\v')])

    def _s_esc_char_c6(self):
        self._h_seq([self._r_squote,
                     lambda: self._h_succeed("'")])

    def _s_esc_char_c7(self):
        self._h_seq([self._r_dquote,
                     lambda: self._h_succeed('"')])

    def _s_esc_char_c8(self):
        self._h_seq([self._r_bslash,
                     lambda: self._h_succeed('\\')])

    def _s_esc_char_c9(self):
        self._h_scope('esc_char', [lambda: self._h_bind(self._r_hex_esc, '_1'),
                                   lambda: self._h_succeed(self._h_get('_1'))])

    def _s_esc_char_c10(self):
        self._h_scope('esc_char', [lambda: self._h_bind(self._r_unicode_esc, '_1'),
                                   lambda: self._h_succeed(self._h_get('_1'))])

    def _r_hex_esc(self):
        self._h_memo(lambda: self._h_scope('hex_esc', [lambda: self._h_re('x'),
                                                       lambda: self._h_bind(lambda: self._h_capture(self._s_hex_esc_s1_l_c), '_2'),
                                                       lambda: self._h_succeed(self._f_xtou(self._h_get('_2')))]), '_r_hex_esc')

    def _s_hex_esc_s1_l_c(self):
        self._h_seq([self._r_hex,
                     self._r_hex])

    def _r_unicode_esc(self):
        self._h_memo(lambda: self._h_choose([self._s_unicode_esc_c0,
                                             self._s_unicode_esc_c1]), '_r_unicode_esc')

    def _s_unicode_esc_c0(self):
        self._h_scope('unicode_esc', [lambda: self._h_ch('u'),
                                      lambda: self._h_bind(lambda: self._h_capture(self._s_unicode_esc_c0_s1_l_c), '_2'),
                                      lambda: self._h_succeed(self._f_xtou(self._h_get('_2')))])

    def _s_unicode_esc_c0_s1_l_c(self):
        self._h_seq([self._r_hex,
                     self._r_hex,
                     self._r_hex,
                     self._r_hex])

    def _s_unicode_esc_c1(self):
        self._h_scope('unicode_esc', [lambda: self._h_ch('U'),
                                      lambda: self._h_bind(lambda: self._h_capture(self._s_unicode_esc_c1_s1_l_c), '_2'),
                                      lambda: self._h_succeed(self._f_xtou(self._h_get('_2')))])

    def _s_unicode_esc_c1_s1_l_c(self):
        self._h_seq([self._r_hex,
                     self._r_hex,
                     self._r_hex,
                     self._r_hex,
                     self._r_hex,
                     self._r_hex,
                     self._r_hex,
                     self._r_hex])

    def _r_ll_exprs(self):
        self._h_memo(lambda: self._h_choose([self._s_ll_exprs_c0,
                                             lambda: self._h_succeed([])]), '_r_ll_exprs')

    def _s_ll_exprs_c0(self):
        self._h_scope('ll_exprs', [lambda: self._h_bind(self._r_ll_expr, '_1'),
                                   lambda: self._h_bind(lambda: self._h_star(self._s_ll_exprs_c0_s1_l_s), '_2'),
                                   lambda: self._h_succeed([self._h_get('_1')] + self._h_get('_2'))])

    def _s_ll_exprs_c0_s1_l_s(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch(','),
                     self._r_sp,
                     self._r_ll_expr])

    def _r_ll_expr(self):
        self._h_memo(lambda: self._h_choose([self._s_ll_expr_c0,
                                             self._r_ll_qual]), '_r_ll_expr')

    def _s_ll_expr_c0(self):
        self._h_scope('ll_expr', [lambda: self._h_bind(self._r_ll_qual, '_1'),
                                  self._r_sp,
                                  lambda: self._h_ch('+'),
                                  self._r_sp,
                                  lambda: self._h_bind(self._r_ll_expr, '_5'),
                                  lambda: self._h_succeed(['ll_plus', self._h_get('_1'), self._h_get('_5')])])

    def _r_ll_qual(self):
        self._h_memo(lambda: self._h_choose([self._s_ll_qual_c0,
                                             self._r_ll_prim]), '_r_ll_qual')

    def _s_ll_qual_c0(self):
        self._h_scope('ll_qual', [lambda: self._h_bind(self._r_ll_prim, '_1'),
                                  lambda: self._h_bind(lambda: self._h_plus(self._r_ll_post_op), '_2'),
                                  lambda: self._h_succeed(['ll_qual', self._h_get('_1'), self._h_get('_2')])])

    def _r_ll_post_op(self):
        self._h_memo(lambda: self._h_choose([self._s_ll_post_op_c0,
                                             self._s_ll_post_op_c1,
                                             self._s_ll_post_op_c2]), '_r_ll_post_op')

    def _s_ll_post_op_c0(self):
        self._h_scope('ll_post_op', [lambda: self._h_ch('['),
                                     self._r_sp,
                                     lambda: self._h_bind(self._r_ll_expr, '_3'),
                                     self._r_sp,
                                     lambda: self._h_ch(']'),
                                     lambda: self._h_succeed(['ll_getitem', self._h_get('_3')])])

    def _s_ll_post_op_c1(self):
        self._h_scope('ll_post_op', [lambda: self._h_ch('('),
                                     self._r_sp,
                                     lambda: self._h_bind(self._r_ll_exprs, '_3'),
                                     self._r_sp,
                                     lambda: self._h_ch(')'),
                                     lambda: self._h_succeed(['ll_call', self._h_get('_3')])])

    def _s_ll_post_op_c2(self):
        self._h_scope('ll_post_op', [lambda: self._h_ch('.'),
                                     lambda: self._h_bind(self._r_ident, '_2'),
                                     lambda: self._h_succeed(['ll_getattr', self._h_get('_2')])])

    def _r_ll_prim(self):
        self._h_memo(lambda: self._h_choose([self._s_ll_prim_c0,
                                             self._s_ll_prim_c1,
                                             self._s_ll_prim_c2,
                                             self._s_ll_prim_c3,
                                             self._s_ll_prim_c4,
                                             self._s_ll_prim_c5]), '_r_ll_prim')

    def _s_ll_prim_c0(self):
        self._h_scope('ll_prim', [lambda: self._h_bind(self._r_ident, '_1'),
                                  lambda: self._h_succeed(['ll_var', self._h_get('_1')])])

    def _s_ll_prim_c1(self):
        self._h_scope('ll_prim', [lambda: self._h_bind(lambda: self._h_capture(lambda: self._h_plus(self._r_digit)), '_1'),
                                  lambda: self._h_succeed(['ll_dec', self._h_get('_1')])])

    def _s_ll_prim_c2(self):
        self._h_scope('ll_prim', [lambda: self._h_str('0x', 2),
                                  lambda: self._h_bind(lambda: self._h_capture(lambda: self._h_plus(self._r_hex)), '_2'),
                                  lambda: self._h_succeed(['ll_hex', self._h_get('_2')])])

    def _s_ll_prim_c3(self):
        self._h_scope('ll_prim', [lambda: self._h_bind(self._r_lit, '_1'),
                                  lambda: self._h_succeed(['ll_str', self._h_get('_1')[1]])])

    def _s_ll_prim_c4(self):
        self._h_scope('ll_prim', [lambda: self._h_ch('('),
                                  self._r_sp,
                                  lambda: self._h_bind(self._r_ll_expr, 'e'),
                                  self._r_sp,
                                  lambda: self._h_ch(')'),
                                  lambda: self._h_succeed(['ll_paren', self._h_get('e')])])

    def _s_ll_prim_c5(self):
        self._h_scope('ll_prim', [lambda: self._h_ch('['),
                                  self._r_sp,
                                  lambda: self._h_bind(self._r_ll_exprs, 'es'),
                                  self._r_sp,
                                  lambda: self._h_ch(']'),
                                  lambda: self._h_succeed(['ll_arr', self._h_get('es')])])

    def _r_hex(self):
        self._h_memo(lambda: self._h_re('[0-9a-fA-F]'), '_r_hex')

    def _r_digit(self):
        self._h_memo(lambda: self._h_range('0', '9'), '_r_digit')

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

    def _f_xtou(self, s):
        return chr(int(s, base=16))

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

    def _h_memo(self, rule, rule_name):
        r = self._cache.get((rule_name, self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        rule()
        self._cache[(rule_name, pos)] = (self.val, self.failed, self.pos)

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
