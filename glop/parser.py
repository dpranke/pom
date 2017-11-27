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
        self._cache = {}

    def parse(self):
        self._r_grammar()
        if self.failed:
            return self._h_err()
        return self.val, None, self.pos

    def _r_grammar(self):
        r = self._cache.get(("_r_grammar", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_scope('grammar', [lambda: self._h_bind(lambda: self._h_star(self._s_grammar_s0_l_p, []), 'vs'),
                                  self._r_sp,
                                  self._r_end,
                                  lambda: self._h_succeed(['rules', self._h_get('vs')])])
        self._cache[("_r_grammar", pos)] = (
            self.val, self.failed, self.pos)

    def _s_grammar_s0_l_p(self):
        self._h_seq([self._r_sp,
                     self._r_rule])

    def _r_sp(self):
        r = self._cache.get(("_r_sp", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_star(self._r_ws, [])
        self._cache[("_r_sp", pos)] = (
            self.val, self.failed, self.pos)

    def _r_ws(self):
        r = self._cache.get(("_r_ws", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([lambda: self._h_ch(' '),
                        lambda: self._h_ch('\t'),
                        self._r_eol,
                        self._r_comment])
        self._cache[("_r_ws", pos)] = (
            self.val, self.failed, self.pos)

    def _r_eol(self):
        r = self._cache.get(("_r_eol", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([lambda: self._h_str('\r\n', 2),
                        lambda: self._h_ch('\r'),
                        lambda: self._h_ch('\n')])
        self._cache[("_r_eol", pos)] = (
            self.val, self.failed, self.pos)

    def _r_comment(self):
        r = self._cache.get(("_r_comment", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_comment_c0,
                        self._s_comment_c1])
        self._cache[("_r_comment", pos)] = (
            self.val, self.failed, self.pos)

    def _s_comment_c0(self):
        self._h_seq([lambda: self._h_str('//', 2),
                     lambda: self._h_star(self._s_comment_c0_s1_p, [])])

    def _s_comment_c0_s1_p(self):
        self._h_seq([lambda: self._h_not(self._r_eol),
                     self._r_anything])

    def _s_comment_c1(self):
        self._h_seq([lambda: self._h_str('/*', 2),
                     lambda: self._h_star(self._s_comment_c1_s1_p, []),
                     lambda: self._h_str('*/', 2)])

    def _s_comment_c1_s1_p(self):
        self._h_seq([lambda: self._h_not(lambda: self._h_str('*/', 2)),
                     self._r_anything])

    def _r_rule(self):
        r = self._cache.get(("_r_rule", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_scope('rule', [lambda: self._h_bind(self._r_ident, 'i'),
                               self._r_sp,
                               lambda: self._h_ch('='),
                               self._r_sp,
                               lambda: self._h_bind(self._r_choice, 'cs'),
                               self._r_sp,
                               lambda: self._h_opt(lambda: self._h_ch(',')),
                               lambda: self._h_succeed(['rule', self._h_get('i'), self._h_get('cs')])])
        self._cache[("_r_rule", pos)] = (
            self.val, self.failed, self.pos)

    def _r_ident(self):
        r = self._cache.get(("_r_ident", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_scope('ident', [lambda: self._h_bind(self._r_id_start, 'hd'),
                                lambda: self._h_bind(lambda: self._h_star(self._r_id_continue, []), 'tl'),
                                lambda: self._h_succeed(self._f_cat([self._h_get('hd')] + self._h_get('tl')))])
        self._cache[("_r_ident", pos)] = (
            self.val, self.failed, self.pos)

    def _r_id_start(self):
        r = self._cache.get(("_r_id_start", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([lambda: self._h_range('a', 'z'),
                        lambda: self._h_range('A', 'Z'),
                        lambda: self._h_ch('_')])
        self._cache[("_r_id_start", pos)] = (
            self.val, self.failed, self.pos)

    def _r_id_continue(self):
        r = self._cache.get(("_r_id_continue", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._r_id_start,
                        self._r_digit])
        self._cache[("_r_id_continue", pos)] = (
            self.val, self.failed, self.pos)

    def _r_choice(self):
        r = self._cache.get(("_r_choice", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_scope('choice', [lambda: self._h_bind(self._r_seq, 's'),
                                 lambda: self._h_bind(lambda: self._h_star(self._s_choice_s1_l_p, []), 'ss'),
                                 lambda: self._h_succeed(['choice', [self._h_get('s')] + self._h_get('ss')])])
        self._cache[("_r_choice", pos)] = (
            self.val, self.failed, self.pos)

    def _s_choice_s1_l_p(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch('|'),
                     self._r_sp,
                     self._r_seq])

    def _r_seq(self):
        r = self._cache.get(("_r_seq", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_seq_c0,
                        lambda: self._h_succeed(['empty'])])
        self._cache[("_r_seq", pos)] = (
            self.val, self.failed, self.pos)

    def _s_seq_c0(self):
        self._h_scope('seq', [lambda: self._h_bind(self._r_expr, 'e'),
                              lambda: self._h_bind(lambda: self._h_star(self._s_seq_c0_s1_l_p, []), 'es'),
                              lambda: self._h_succeed(['seq', [self._h_get('e')] + self._h_get('es')])])

    def _s_seq_c0_s1_l_p(self):
        self._h_seq([self._r_ws,
                     self._r_sp,
                     self._r_expr])

    def _r_expr(self):
        r = self._cache.get(("_r_expr", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_expr_c0,
                        self._r_post_expr])
        self._cache[("_r_expr", pos)] = (
            self.val, self.failed, self.pos)

    def _s_expr_c0(self):
        self._h_scope('expr', [lambda: self._h_bind(self._r_post_expr, 'e'),
                               lambda: self._h_ch(':'),
                               lambda: self._h_bind(self._r_ident, 'l'),
                               lambda: self._h_succeed(['label', self._h_get('e'), self._h_get('l')])])

    def _r_post_expr(self):
        r = self._cache.get(("_r_post_expr", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_post_expr_c0,
                        self._r_prim_expr])
        self._cache[("_r_post_expr", pos)] = (
            self.val, self.failed, self.pos)

    def _s_post_expr_c0(self):
        self._h_scope('post_expr', [lambda: self._h_bind(self._r_prim_expr, 'e'),
                                    lambda: self._h_bind(self._r_post_op, 'op'),
                                    lambda: self._h_succeed([self._h_get('op'), self._h_get('e')])])

    def _r_post_op(self):
        r = self._cache.get(("_r_post_op", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_post_op_c0,
                        self._s_post_op_c1,
                        self._s_post_op_c2])
        self._cache[("_r_post_op", pos)] = (
            self.val, self.failed, self.pos)

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
        r = self._cache.get(("_r_prim_expr", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_prim_expr_c0,
                        self._s_prim_expr_c1,
                        self._s_prim_expr_c2,
                        self._s_prim_expr_c3,
                        self._s_prim_expr_c4,
                        self._s_prim_expr_c5,
                        self._s_prim_expr_c6])
        self._cache[("_r_prim_expr", pos)] = (
            self.val, self.failed, self.pos)

    def _s_prim_expr_c0(self):
        self._h_scope('prim_expr', [lambda: self._h_bind(self._r_lit, 'i'),
                                    self._r_sp,
                                    lambda: self._h_str('..', 2),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_lit, 'j'),
                                    lambda: self._h_succeed(['range', self._h_get('i'), self._h_get('j')])])

    def _s_prim_expr_c1(self):
        self._h_scope('prim_expr', [lambda: self._h_bind(self._r_lit, 'l'),
                                    lambda: self._h_succeed(self._h_get('l'))])

    def _s_prim_expr_c2(self):
        self._h_scope('prim_expr', [lambda: self._h_bind(self._r_ident, 'i'),
                                    lambda: self._h_not(self._s_prim_expr_c2_s1_n),
                                    lambda: self._h_succeed(['apply', self._h_get('i')])])

    def _s_prim_expr_c2_s1_n(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch('=')])

    def _s_prim_expr_c3(self):
        self._h_scope('prim_expr', [lambda: self._h_str('->', 2),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_ll_expr, 'e'),
                                    lambda: self._h_succeed(['action', self._h_get('e')])])

    def _s_prim_expr_c4(self):
        self._h_scope('prim_expr', [lambda: self._h_ch('~'),
                                    lambda: self._h_bind(self._r_prim_expr, 'e'),
                                    lambda: self._h_succeed(['not', self._h_get('e')])])

    def _s_prim_expr_c5(self):
        self._h_scope('prim_expr', [lambda: self._h_str('?(', 2),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_ll_expr, 'e'),
                                    self._r_sp,
                                    lambda: self._h_ch(')'),
                                    lambda: self._h_succeed(['pred', self._h_get('e')])])

    def _s_prim_expr_c6(self):
        self._h_scope('prim_expr', [lambda: self._h_ch('('),
                                    self._r_sp,
                                    lambda: self._h_bind(self._r_choice, 'e'),
                                    self._r_sp,
                                    lambda: self._h_ch(')'),
                                    lambda: self._h_succeed(['paren', self._h_get('e')])])

    def _r_lit(self):
        r = self._cache.get(("_r_lit", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_lit_c0,
                        self._s_lit_c1])
        self._cache[("_r_lit", pos)] = (
            self.val, self.failed, self.pos)

    def _s_lit_c0(self):
        self._h_scope('lit', [self._r_squote,
                              lambda: self._h_bind(lambda: self._h_star(self._r_sqchar, []), 'cs'),
                              self._r_squote,
                              lambda: self._h_succeed(['lit', self._f_cat(self._h_get('cs'))])])

    def _s_lit_c1(self):
        self._h_scope('lit', [self._r_dquote,
                              lambda: self._h_bind(lambda: self._h_star(self._r_dqchar, []), 'cs'),
                              self._r_dquote,
                              lambda: self._h_succeed(['lit', self._f_cat(self._h_get('cs'))])])

    def _r_sqchar(self):
        r = self._cache.get(("_r_sqchar", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_sqchar_c0,
                        self._s_sqchar_c1])
        self._cache[("_r_sqchar", pos)] = (
            self.val, self.failed, self.pos)

    def _s_sqchar_c0(self):
        self._h_scope('sqchar', [self._r_bslash,
                                 lambda: self._h_bind(self._r_esc_char, 'c'),
                                 lambda: self._h_succeed(self._h_get('c'))])

    def _s_sqchar_c1(self):
        self._h_scope('sqchar', [lambda: self._h_not(self._r_squote),
                                 lambda: self._h_bind(self._r_anything, 'c'),
                                 lambda: self._h_succeed(self._h_get('c'))])

    def _r_dqchar(self):
        r = self._cache.get(("_r_dqchar", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_dqchar_c0,
                        self._s_dqchar_c1])
        self._cache[("_r_dqchar", pos)] = (
            self.val, self.failed, self.pos)

    def _s_dqchar_c0(self):
        self._h_scope('dqchar', [self._r_bslash,
                                 lambda: self._h_bind(self._r_esc_char, 'c'),
                                 lambda: self._h_succeed(self._h_get('c'))])

    def _s_dqchar_c1(self):
        self._h_scope('dqchar', [lambda: self._h_not(self._r_dquote),
                                 lambda: self._h_bind(self._r_anything, 'c'),
                                 lambda: self._h_succeed(self._h_get('c'))])

    def _r_bslash(self):
        r = self._cache.get(("_r_bslash", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_ch('\\')
        self._cache[("_r_bslash", pos)] = (
            self.val, self.failed, self.pos)

    def _r_squote(self):
        r = self._cache.get(("_r_squote", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_ch("'")
        self._cache[("_r_squote", pos)] = (
            self.val, self.failed, self.pos)

    def _r_dquote(self):
        r = self._cache.get(("_r_dquote", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_ch('"')
        self._cache[("_r_dquote", pos)] = (
            self.val, self.failed, self.pos)

    def _r_esc_char(self):
        r = self._cache.get(("_r_esc_char", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_esc_char_c0,
                        self._s_esc_char_c1,
                        self._s_esc_char_c2,
                        self._s_esc_char_c3,
                        self._s_esc_char_c4,
                        self._s_esc_char_c5,
                        self._s_esc_char_c6,
                        self._s_esc_char_c7,
                        self._s_esc_char_c8,
                        self._s_esc_char_c9,
                        self._s_esc_char_c10])
        self._cache[("_r_esc_char", pos)] = (
            self.val, self.failed, self.pos)

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
        self._h_scope('esc_char', [lambda: self._h_bind(self._r_hex_esc, 'c'),
                                   lambda: self._h_succeed(self._h_get('c'))])

    def _s_esc_char_c10(self):
        self._h_scope('esc_char', [lambda: self._h_bind(self._r_unicode_esc, 'c'),
                                   lambda: self._h_succeed(self._h_get('c'))])

    def _r_hex_esc(self):
        r = self._cache.get(("_r_hex_esc", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_scope('hex_esc', [lambda: self._h_ch('x'),
                                  lambda: self._h_bind(self._r_hex, 'h1'),
                                  lambda: self._h_bind(self._r_hex, 'h2'),
                                  lambda: self._h_succeed(self._f_xtou(self._h_get('h1') + self._h_get('h2')))])
        self._cache[("_r_hex_esc", pos)] = (
            self.val, self.failed, self.pos)

    def _r_unicode_esc(self):
        r = self._cache.get(("_r_unicode_esc", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_unicode_esc_c0,
                        self._s_unicode_esc_c1])
        self._cache[("_r_unicode_esc", pos)] = (
            self.val, self.failed, self.pos)

    def _s_unicode_esc_c0(self):
        self._h_scope('unicode_esc', [lambda: self._h_ch('u'),
                                      lambda: self._h_bind(self._r_hex, 'h1'),
                                      lambda: self._h_bind(self._r_hex, 'h2'),
                                      lambda: self._h_bind(self._r_hex, 'h3'),
                                      lambda: self._h_bind(self._r_hex, 'h4'),
                                      lambda: self._h_succeed(self._f_xtou(self._h_get('h1') + self._h_get('h2') + self._h_get('h3') + self._h_get('h4')))])

    def _s_unicode_esc_c1(self):
        self._h_scope('unicode_esc', [lambda: self._h_ch('U'),
                                      lambda: self._h_bind(self._r_hex, 'h1'),
                                      lambda: self._h_bind(self._r_hex, 'h2'),
                                      lambda: self._h_bind(self._r_hex, 'h3'),
                                      lambda: self._h_bind(self._r_hex, 'h4'),
                                      lambda: self._h_bind(self._r_hex, 'h5'),
                                      lambda: self._h_bind(self._r_hex, 'h6'),
                                      lambda: self._h_bind(self._r_hex, 'h7'),
                                      lambda: self._h_bind(self._r_hex, 'h8'),
                                      lambda: self._h_succeed(self._f_xtou(self._h_get('h1') + self._h_get('h2') + self._h_get('h3') + self._h_get('h4') + self._h_get('h5') + self._h_get('h6') + self._h_get('h7') + self._h_get('h8')))])

    def _r_ll_exprs(self):
        r = self._cache.get(("_r_ll_exprs", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_ll_exprs_c0,
                        lambda: self._h_succeed([])])
        self._cache[("_r_ll_exprs", pos)] = (
            self.val, self.failed, self.pos)

    def _s_ll_exprs_c0(self):
        self._h_scope('ll_exprs', [lambda: self._h_bind(self._r_ll_expr, 'e'),
                                   lambda: self._h_bind(lambda: self._h_star(self._s_ll_exprs_c0_s1_l_p, []), 'es'),
                                   lambda: self._h_succeed([self._h_get('e')] + self._h_get('es'))])

    def _s_ll_exprs_c0_s1_l_p(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch(','),
                     self._r_sp,
                     self._r_ll_expr])

    def _r_ll_expr(self):
        r = self._cache.get(("_r_ll_expr", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_ll_expr_c0,
                        self._r_ll_qual])
        self._cache[("_r_ll_expr", pos)] = (
            self.val, self.failed, self.pos)

    def _s_ll_expr_c0(self):
        self._h_scope('ll_expr', [lambda: self._h_bind(self._r_ll_qual, 'e1'),
                                  self._r_sp,
                                  lambda: self._h_ch('+'),
                                  self._r_sp,
                                  lambda: self._h_bind(self._r_ll_expr, 'e2'),
                                  lambda: self._h_succeed(['ll_plus', self._h_get('e1'), self._h_get('e2')])])

    def _r_ll_qual(self):
        r = self._cache.get(("_r_ll_qual", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_ll_qual_c0,
                        self._r_ll_prim])
        self._cache[("_r_ll_qual", pos)] = (
            self.val, self.failed, self.pos)

    def _s_ll_qual_c0(self):
        self._h_scope('ll_qual', [lambda: self._h_bind(self._r_ll_prim, 'e'),
                                  lambda: self._h_bind(lambda: self._h_plus(self._r_ll_post_op), 'ps'),
                                  lambda: self._h_succeed(['ll_qual', self._h_get('e'), self._h_get('ps')])])

    def _r_ll_post_op(self):
        r = self._cache.get(("_r_ll_post_op", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_ll_post_op_c0,
                        self._s_ll_post_op_c1,
                        self._s_ll_post_op_c2])
        self._cache[("_r_ll_post_op", pos)] = (
            self.val, self.failed, self.pos)

    def _s_ll_post_op_c0(self):
        self._h_scope('ll_post_op', [lambda: self._h_ch('['),
                                     self._r_sp,
                                     lambda: self._h_bind(self._r_ll_expr, 'e'),
                                     self._r_sp,
                                     lambda: self._h_ch(']'),
                                     lambda: self._h_succeed(['ll_getitem', self._h_get('e')])])

    def _s_ll_post_op_c1(self):
        self._h_scope('ll_post_op', [lambda: self._h_ch('('),
                                     self._r_sp,
                                     lambda: self._h_bind(self._r_ll_exprs, 'es'),
                                     self._r_sp,
                                     lambda: self._h_ch(')'),
                                     lambda: self._h_succeed(['ll_call', self._h_get('es')])])

    def _s_ll_post_op_c2(self):
        self._h_scope('ll_post_op', [lambda: self._h_ch('.'),
                                     lambda: self._h_bind(self._r_ident, 'i'),
                                     lambda: self._h_succeed(['ll_getattr', self._h_get('i')])])

    def _r_ll_prim(self):
        r = self._cache.get(("_r_ll_prim", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._s_ll_prim_c0,
                        self._s_ll_prim_c1,
                        self._s_ll_prim_c2,
                        self._s_ll_prim_c3,
                        self._s_ll_prim_c4,
                        self._s_ll_prim_c5])
        self._cache[("_r_ll_prim", pos)] = (
            self.val, self.failed, self.pos)

    def _s_ll_prim_c0(self):
        self._h_scope('ll_prim', [lambda: self._h_bind(self._r_ident, 'i'),
                                  lambda: self._h_succeed(['ll_var', self._h_get('i')])])

    def _s_ll_prim_c1(self):
        self._h_scope('ll_prim', [lambda: self._h_bind(self._r_digits, 'ds'),
                                  lambda: self._h_succeed(['ll_num', self._h_get('ds')])])

    def _s_ll_prim_c2(self):
        self._h_scope('ll_prim', [lambda: self._h_str('0x', 2),
                                  lambda: self._h_bind(self._r_hexdigits, 'hs'),
                                  lambda: self._h_succeed(['ll_num', '0x' + self._h_get('hs')])])

    def _s_ll_prim_c3(self):
        self._h_scope('ll_prim', [lambda: self._h_bind(self._r_lit, 'l'),
                                  lambda: self._h_succeed(['ll_lit', self._h_get('l')[1]])])

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

    def _r_digits(self):
        r = self._cache.get(("_r_digits", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_scope('digits', [lambda: self._h_bind(lambda: self._h_plus(self._r_digit), 'ds'),
                                 lambda: self._h_succeed(self._f_cat(self._h_get('ds')))])
        self._cache[("_r_digits", pos)] = (
            self.val, self.failed, self.pos)

    def _r_hexdigits(self):
        r = self._cache.get(("_r_hexdigits", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_scope('hexdigits', [lambda: self._h_bind(lambda: self._h_plus(self._r_hex), 'hs'),
                                    lambda: self._h_succeed(self._f_cat(self._h_get('hs')))])
        self._cache[("_r_hexdigits", pos)] = (
            self.val, self.failed, self.pos)

    def _r_hex(self):
        r = self._cache.get(("_r_hex", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_choose([self._r_digit,
                        lambda: self._h_range('a', 'f'),
                        lambda: self._h_range('A', 'F')])
        self._cache[("_r_hex", pos)] = (
            self.val, self.failed, self.pos)

    def _r_digit(self):
        r = self._cache.get(("_r_digit", self.pos))
        if r is not None:
            self.val, self.failed, self.pos = r
            return
        pos = self.pos
        self._h_range('0', '9')
        self._cache[("_r_digit", pos)] = (
            self.val, self.failed, self.pos)

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
