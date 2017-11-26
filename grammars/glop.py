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
                                     self._r_sp,
                                     self._r_end,
                                     self._s_grammar_s3])

    def _s_grammar_s0(self):
        self._h_bind(self._s_grammar_s0_l, 'vs')

    def _s_grammar_s0_l(self):
        self._h_star(self._s_grammar_s0_l_p, [])

    def _s_grammar_s0_l_p(self):
        self._h_seq([self._r_sp,
                     self._r_rule])

    def _s_grammar_s3(self):
        self._h_succeed(self._h_get('vs'))

    def _r_sp(self):
        self._h_star(self._r_ws, [])

    def _r_ws(self):
        self._h_choose([lambda: self._h_ch(' '),
                        lambda: self._h_ch('\t'),
                        self._r_eol,
                        self._r_comment])

    def _r_eol(self):
        self._h_choose([lambda: self._h_str('\r\n', 2),
                        lambda: self._h_ch('\r'),
                        lambda: self._h_ch('\n')])

    def _r_comment(self):
        self._h_choose([self._s_comment_c0,
                        self._s_comment_c1])

    def _s_comment_c0(self):
        self._h_seq([lambda: self._h_str('//', 2),
                     self._s_comment_c0_s1])

    def _s_comment_c0_s1(self):
        self._h_star(self._s_comment_c0_s1_p, [])

    def _s_comment_c0_s1_p(self):
        self._h_seq([self._s_comment_c0_s1_p_s0,
                     self._r_anything])

    def _s_comment_c0_s1_p_s0(self):
        self._h_not(self._r_eol)

    def _s_comment_c1(self):
        self._h_seq([lambda: self._h_str('/*', 2),
                     self._s_comment_c1_s1,
                     lambda: self._h_str('*/', 2)])

    def _s_comment_c1_s1(self):
        self._h_star(self._s_comment_c1_s1_p, [])

    def _s_comment_c1_s1_p(self):
        self._h_seq([self._s_comment_c1_s1_p_s0,
                     self._r_anything])

    def _s_comment_c1_s1_p_s0(self):
        self._h_not(self._s_comment_c1_s1_p_s0_n)

    def _s_comment_c1_s1_p_s0_n(self):
        self._h_str('*/', 2)

    def _r_rule(self):
        self._h_scope('_r_rule', [self._s_rule_s0,
                                  self._r_sp,
                                  lambda: self._h_ch('='),
                                  self._r_sp,
                                  self._s_rule_s4,
                                  self._r_sp,
                                  self._s_rule_s6,
                                  self._s_rule_s7])

    def _s_rule_s0(self):
        self._h_bind(self._r_ident, 'i')

    def _s_rule_s4(self):
        self._h_bind(self._r_choice, 'cs')

    def _s_rule_s6(self):
        self._h_opt(self._s_rule_s6_p)

    def _s_rule_s6_p(self):
        self._h_ch(',')

    def _s_rule_s7(self):
        self._h_succeed(['rule', self._h_get('i'), self._h_get('cs')])

    def _r_ident(self):
        self._h_scope('_r_ident', [self._s_ident_s0,
                                   self._s_ident_s1,
                                   self._s_ident_s2])

    def _s_ident_s0(self):
        self._h_bind(self._r_id_start, 'hd')

    def _s_ident_s1(self):
        self._h_bind(self._s_ident_s1_l, 'tl')

    def _s_ident_s1_l(self):
        self._h_star(self._r_id_continue, [])

    def _s_ident_s2(self):
        self._h_succeed(self._f_cat([self._h_get('hd')] + self._h_get('tl')))

    def _r_id_start(self):
        self._h_choose([self._s_id_start_c0,
                        self._s_id_start_c1,
                        lambda: self._h_ch('_')])

    def _s_id_start_c0(self):
        self._h_range('a', 'z')

    def _s_id_start_c1(self):
        self._h_range('A', 'Z')

    def _r_id_continue(self):
        self._h_choose([self._r_id_start,
                        self._r_digit])

    def _r_choice(self):
        self._h_scope('_r_choice', [self._s_choice_s0,
                                    self._s_choice_s1,
                                    self._s_choice_s2])

    def _s_choice_s0(self):
        self._h_bind(self._r_seq, 's')

    def _s_choice_s1(self):
        self._h_bind(self._s_choice_s1_l, 'ss')

    def _s_choice_s1_l(self):
        self._h_star(self._s_choice_s1_l_p, [])

    def _s_choice_s1_l_p(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch('|'),
                     self._r_sp,
                     self._r_seq])

    def _s_choice_s2(self):
        self._h_succeed(['choice', [self._h_get('s')] + self._h_get('ss')])

    def _r_seq(self):
        self._h_choose([self._s_seq_c0,
                        self._s_seq_c1])

    def _s_seq_c0(self):
        self._h_scope('_s_seq_c0', [self._s_seq_c0_s0,
                                    self._s_seq_c0_s1,
                                    self._s_seq_c0_s2])

    def _s_seq_c0_s0(self):
        self._h_bind(self._r_expr, 'e')

    def _s_seq_c0_s1(self):
        self._h_bind(self._s_seq_c0_s1_l, 'es')

    def _s_seq_c0_s1_l(self):
        self._h_star(self._s_seq_c0_s1_l_p, [])

    def _s_seq_c0_s1_l_p(self):
        self._h_seq([self._r_ws,
                     self._r_sp,
                     self._r_expr])

    def _s_seq_c0_s2(self):
        self._h_succeed(['seq', [self._h_get('e')] + self._h_get('es')])

    def _s_seq_c1(self):
        self._h_succeed(['empty'])

    def _r_expr(self):
        self._h_choose([self._s_expr_c0,
                        self._r_post_expr])

    def _s_expr_c0(self):
        self._h_scope('_s_expr_c0', [self._s_expr_c0_s0,
                                     lambda: self._h_ch(':'),
                                     self._s_expr_c0_s2,
                                     self._s_expr_c0_s3])

    def _s_expr_c0_s0(self):
        self._h_bind(self._r_post_expr, 'e')

    def _s_expr_c0_s2(self):
        self._h_bind(self._r_ident, 'l')

    def _s_expr_c0_s3(self):
        self._h_succeed(['label', self._h_get('e'), self._h_get('l')])

    def _r_post_expr(self):
        self._h_choose([self._s_post_expr_c0,
                        self._r_prim_expr])

    def _s_post_expr_c0(self):
        self._h_scope('_s_post_expr_c0', [self._s_post_expr_c0_s0,
                                          self._s_post_expr_c0_s1,
                                          self._s_post_expr_c0_s2])

    def _s_post_expr_c0_s0(self):
        self._h_bind(self._r_prim_expr, 'e')

    def _s_post_expr_c0_s1(self):
        self._h_bind(self._r_post_op, 'op')

    def _s_post_expr_c0_s2(self):
        self._h_succeed(['post', self._h_get('e'), self._h_get('op')])

    def _r_post_op(self):
        self._h_choose([lambda: self._h_ch('?'),
                        lambda: self._h_ch('*'),
                        lambda: self._h_ch('+')])

    def _r_prim_expr(self):
        self._h_choose([self._s_prim_expr_c0,
                        self._s_prim_expr_c1,
                        self._s_prim_expr_c2,
                        self._s_prim_expr_c3,
                        self._s_prim_expr_c4,
                        self._s_prim_expr_c5,
                        self._s_prim_expr_c6])

    def _s_prim_expr_c0(self):
        self._h_scope('_s_prim_expr_c0', [self._s_prim_expr_c0_s0,
                                          self._r_sp,
                                          lambda: self._h_str('..', 2),
                                          self._r_sp,
                                          self._s_prim_expr_c0_s4,
                                          self._s_prim_expr_c0_s5])

    def _s_prim_expr_c0_s0(self):
        self._h_bind(self._r_lit, 'i')

    def _s_prim_expr_c0_s4(self):
        self._h_bind(self._r_lit, 'j')

    def _s_prim_expr_c0_s5(self):
        self._h_succeed(['range', self._h_get('i'), self._h_get('j')])

    def _s_prim_expr_c1(self):
        self._h_scope('_s_prim_expr_c1', [self._s_prim_expr_c1_s0,
                                          self._s_prim_expr_c1_s1])

    def _s_prim_expr_c1_s0(self):
        self._h_bind(self._r_lit, 'l')

    def _s_prim_expr_c1_s1(self):
        self._h_succeed(self._h_get('l'))

    def _s_prim_expr_c2(self):
        self._h_scope('_s_prim_expr_c2', [self._s_prim_expr_c2_s0,
                                          self._s_prim_expr_c2_s1,
                                          self._s_prim_expr_c2_s2])

    def _s_prim_expr_c2_s0(self):
        self._h_bind(self._r_ident, 'i')

    def _s_prim_expr_c2_s1(self):
        self._h_not(self._s_prim_expr_c2_s1_n)

    def _s_prim_expr_c2_s1_n(self):
        self._s_prim_expr_c2_s1_n_p()

    def _s_prim_expr_c2_s1_n_p(self):
        self._h_choose([self._s_prim_expr_c2_s1_n_p_c0])

    def _s_prim_expr_c2_s1_n_p_c0(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch('=')])

    def _s_prim_expr_c2_s2(self):
        self._h_succeed(['apply', self._h_get('i')])

    def _s_prim_expr_c3(self):
        self._h_scope('_s_prim_expr_c3', [lambda: self._h_str('->', 2),
                                          self._r_sp,
                                          self._s_prim_expr_c3_s2,
                                          self._s_prim_expr_c3_s3])

    def _s_prim_expr_c3_s2(self):
        self._h_bind(self._r_ll_expr, 'e')

    def _s_prim_expr_c3_s3(self):
        self._h_succeed(['action', self._h_get('e')])

    def _s_prim_expr_c4(self):
        self._h_scope('_s_prim_expr_c4', [lambda: self._h_ch('~'),
                                          self._s_prim_expr_c4_s1,
                                          self._s_prim_expr_c4_s2])

    def _s_prim_expr_c4_s1(self):
        self._h_bind(self._r_prim_expr, 'e')

    def _s_prim_expr_c4_s2(self):
        self._h_succeed(['not', self._h_get('e')])

    def _s_prim_expr_c5(self):
        self._h_scope('_s_prim_expr_c5', [lambda: self._h_str('?(', 2),
                                          self._r_sp,
                                          self._s_prim_expr_c5_s2,
                                          self._r_sp,
                                          lambda: self._h_ch(')'),
                                          self._s_prim_expr_c5_s5])

    def _s_prim_expr_c5_s2(self):
        self._h_bind(self._r_ll_expr, 'e')

    def _s_prim_expr_c5_s5(self):
        self._h_succeed(['pred', self._h_get('e')])

    def _s_prim_expr_c6(self):
        self._h_scope('_s_prim_expr_c6', [lambda: self._h_ch('('),
                                          self._r_sp,
                                          self._s_prim_expr_c6_s2,
                                          self._r_sp,
                                          lambda: self._h_ch(')'),
                                          self._s_prim_expr_c6_s5])

    def _s_prim_expr_c6_s2(self):
        self._h_bind(self._r_choice, 'e')

    def _s_prim_expr_c6_s5(self):
        self._h_succeed(['paren', self._h_get('e')])

    def _r_lit(self):
        self._h_choose([self._s_lit_c0,
                        self._s_lit_c1])

    def _s_lit_c0(self):
        self._h_scope('_s_lit_c0', [self._r_squote,
                                    self._s_lit_c0_s1,
                                    self._r_squote,
                                    self._s_lit_c0_s3])

    def _s_lit_c0_s1(self):
        self._h_bind(self._s_lit_c0_s1_l, 'cs')

    def _s_lit_c0_s1_l(self):
        self._h_star(self._r_sqchar, [])

    def _s_lit_c0_s3(self):
        self._h_succeed(['lit', self._f_cat(self._h_get('cs'))])

    def _s_lit_c1(self):
        self._h_scope('_s_lit_c1', [self._r_dquote,
                                    self._s_lit_c1_s1,
                                    self._r_dquote,
                                    self._s_lit_c1_s3])

    def _s_lit_c1_s1(self):
        self._h_bind(self._s_lit_c1_s1_l, 'cs')

    def _s_lit_c1_s1_l(self):
        self._h_star(self._r_dqchar, [])

    def _s_lit_c1_s3(self):
        self._h_succeed(['lit', self._f_cat(self._h_get('cs'))])

    def _r_sqchar(self):
        self._h_choose([self._s_sqchar_c0,
                        self._s_sqchar_c1])

    def _s_sqchar_c0(self):
        self._h_scope('_s_sqchar_c0', [self._r_bslash,
                                       self._s_sqchar_c0_s1,
                                       self._s_sqchar_c0_s2])

    def _s_sqchar_c0_s1(self):
        self._h_bind(self._r_esc_char, 'c')

    def _s_sqchar_c0_s2(self):
        self._h_succeed(self._h_get('c'))

    def _s_sqchar_c1(self):
        self._h_scope('_s_sqchar_c1', [self._s_sqchar_c1_s0,
                                       self._s_sqchar_c1_s1,
                                       self._s_sqchar_c1_s2])

    def _s_sqchar_c1_s0(self):
        self._h_not(self._r_squote)

    def _s_sqchar_c1_s1(self):
        self._h_bind(self._r_anything, 'c')

    def _s_sqchar_c1_s2(self):
        self._h_succeed(self._h_get('c'))

    def _r_dqchar(self):
        self._h_choose([self._s_dqchar_c0,
                        self._s_dqchar_c1])

    def _s_dqchar_c0(self):
        self._h_scope('_s_dqchar_c0', [self._r_bslash,
                                       self._s_dqchar_c0_s1,
                                       self._s_dqchar_c0_s2])

    def _s_dqchar_c0_s1(self):
        self._h_bind(self._r_esc_char, 'c')

    def _s_dqchar_c0_s2(self):
        self._h_succeed(self._h_get('c'))

    def _s_dqchar_c1(self):
        self._h_scope('_s_dqchar_c1', [self._s_dqchar_c1_s0,
                                       self._s_dqchar_c1_s1,
                                       self._s_dqchar_c1_s2])

    def _s_dqchar_c1_s0(self):
        self._h_not(self._r_dquote)

    def _s_dqchar_c1_s1(self):
        self._h_bind(self._r_anything, 'c')

    def _s_dqchar_c1_s2(self):
        self._h_succeed(self._h_get('c'))

    def _r_bslash(self):
        self._h_ch('\\')

    def _r_squote(self):
        self._h_ch("'")

    def _r_dquote(self):
        self._h_ch('"')

    def _r_esc_char(self):
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

    def _s_esc_char_c0(self):
        self._h_scope('_s_esc_char_c0', [lambda: self._h_ch('b'),
                                         self._s_esc_char_c0_s1])

    def _s_esc_char_c0_s1(self):
        self._h_succeed('\b')

    def _s_esc_char_c1(self):
        self._h_scope('_s_esc_char_c1', [lambda: self._h_ch('f'),
                                         self._s_esc_char_c1_s1])

    def _s_esc_char_c10(self):
        self._h_scope('_s_esc_char_c10', [self._s_esc_char_c10_s0,
                                          self._s_esc_char_c10_s1])

    def _s_esc_char_c10_s0(self):
        self._h_bind(self._r_unicode_esc, 'c')

    def _s_esc_char_c10_s1(self):
        self._h_succeed(self._h_get('c'))

    def _s_esc_char_c1_s1(self):
        self._h_succeed('\f')

    def _s_esc_char_c2(self):
        self._h_scope('_s_esc_char_c2', [lambda: self._h_ch('n'),
                                         self._s_esc_char_c2_s1])

    def _s_esc_char_c2_s1(self):
        self._h_succeed('\n')

    def _s_esc_char_c3(self):
        self._h_scope('_s_esc_char_c3', [lambda: self._h_ch('r'),
                                         self._s_esc_char_c3_s1])

    def _s_esc_char_c3_s1(self):
        self._h_succeed('\r')

    def _s_esc_char_c4(self):
        self._h_scope('_s_esc_char_c4', [lambda: self._h_ch('t'),
                                         self._s_esc_char_c4_s1])

    def _s_esc_char_c4_s1(self):
        self._h_succeed('\t')

    def _s_esc_char_c5(self):
        self._h_scope('_s_esc_char_c5', [lambda: self._h_ch('v'),
                                         self._s_esc_char_c5_s1])

    def _s_esc_char_c5_s1(self):
        self._h_succeed('\v')

    def _s_esc_char_c6(self):
        self._h_scope('_s_esc_char_c6', [self._r_squote,
                                         self._s_esc_char_c6_s1])

    def _s_esc_char_c6_s1(self):
        self._h_succeed("'")

    def _s_esc_char_c7(self):
        self._h_scope('_s_esc_char_c7', [self._r_dquote,
                                         self._s_esc_char_c7_s1])

    def _s_esc_char_c7_s1(self):
        self._h_succeed('"')

    def _s_esc_char_c8(self):
        self._h_scope('_s_esc_char_c8', [self._r_bslash,
                                         self._s_esc_char_c8_s1])

    def _s_esc_char_c8_s1(self):
        self._h_succeed('\\')

    def _s_esc_char_c9(self):
        self._h_scope('_s_esc_char_c9', [self._s_esc_char_c9_s0,
                                         self._s_esc_char_c9_s1])

    def _s_esc_char_c9_s0(self):
        self._h_bind(self._r_hex_esc, 'c')

    def _s_esc_char_c9_s1(self):
        self._h_succeed(self._h_get('c'))

    def _r_hex_esc(self):
        self._h_scope('_r_hex_esc', [lambda: self._h_ch('x'),
                                     self._s_hex_esc_s1,
                                     self._s_hex_esc_s2,
                                     self._s_hex_esc_s3])

    def _s_hex_esc_s1(self):
        self._h_bind(self._r_hex, 'h1')

    def _s_hex_esc_s2(self):
        self._h_bind(self._r_hex, 'h2')

    def _s_hex_esc_s3(self):
        self._h_succeed(self._f_xtou(self._h_get('h1') + self._h_get('h2')))

    def _r_unicode_esc(self):
        self._h_choose([self._s_unicode_esc_c0,
                        self._s_unicode_esc_c1])

    def _s_unicode_esc_c0(self):
        self._h_scope('_s_unicode_esc_c0', [lambda: self._h_ch('u'),
                                            self._s_unicode_esc_c0_s1,
                                            self._s_unicode_esc_c0_s2,
                                            self._s_unicode_esc_c0_s3,
                                            self._s_unicode_esc_c0_s4,
                                            self._s_unicode_esc_c0_s5])

    def _s_unicode_esc_c0_s1(self):
        self._h_bind(self._r_hex, 'h1')

    def _s_unicode_esc_c0_s2(self):
        self._h_bind(self._r_hex, 'h2')

    def _s_unicode_esc_c0_s3(self):
        self._h_bind(self._r_hex, 'h3')

    def _s_unicode_esc_c0_s4(self):
        self._h_bind(self._r_hex, 'h4')

    def _s_unicode_esc_c0_s5(self):
        self._h_succeed(self._f_xtou(self._h_get('h1') + self._h_get('h2') + self._h_get('h3') + self._h_get('h4')))

    def _s_unicode_esc_c1(self):
        self._h_scope('_s_unicode_esc_c1', [lambda: self._h_ch('U'),
                                            self._s_unicode_esc_c1_s1,
                                            self._s_unicode_esc_c1_s2,
                                            self._s_unicode_esc_c1_s3,
                                            self._s_unicode_esc_c1_s4,
                                            self._s_unicode_esc_c1_s5,
                                            self._s_unicode_esc_c1_s6,
                                            self._s_unicode_esc_c1_s7,
                                            self._s_unicode_esc_c1_s8,
                                            self._s_unicode_esc_c1_s9])

    def _s_unicode_esc_c1_s1(self):
        self._h_bind(self._r_hex, 'h1')

    def _s_unicode_esc_c1_s2(self):
        self._h_bind(self._r_hex, 'h2')

    def _s_unicode_esc_c1_s3(self):
        self._h_bind(self._r_hex, 'h3')

    def _s_unicode_esc_c1_s4(self):
        self._h_bind(self._r_hex, 'h4')

    def _s_unicode_esc_c1_s5(self):
        self._h_bind(self._r_hex, 'h5')

    def _s_unicode_esc_c1_s6(self):
        self._h_bind(self._r_hex, 'h6')

    def _s_unicode_esc_c1_s7(self):
        self._h_bind(self._r_hex, 'h7')

    def _s_unicode_esc_c1_s8(self):
        self._h_bind(self._r_hex, 'h8')

    def _s_unicode_esc_c1_s9(self):
        self._h_succeed(self._f_xtou(self._h_get('h1') + self._h_get('h2') + self._h_get('h3') + self._h_get('h4') + self._h_get('h5') + self._h_get('h6') + self._h_get('h7') + self._h_get('h8')))

    def _r_ll_exprs(self):
        self._h_choose([self._s_ll_exprs_c0,
                        self._s_ll_exprs_c1])

    def _s_ll_exprs_c0(self):
        self._h_scope('_s_ll_exprs_c0', [self._s_ll_exprs_c0_s0,
                                         self._s_ll_exprs_c0_s1,
                                         self._s_ll_exprs_c0_s2])

    def _s_ll_exprs_c0_s0(self):
        self._h_bind(self._r_ll_expr, 'e')

    def _s_ll_exprs_c0_s1(self):
        self._h_bind(self._s_ll_exprs_c0_s1_l, 'es')

    def _s_ll_exprs_c0_s1_l(self):
        self._h_star(self._s_ll_exprs_c0_s1_l_p, [])

    def _s_ll_exprs_c0_s1_l_p(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch(','),
                     self._r_sp,
                     self._r_ll_expr])

    def _s_ll_exprs_c0_s2(self):
        self._h_succeed([self._h_get('e')] + self._h_get('es'))

    def _s_ll_exprs_c1(self):
        self._h_succeed([])

    def _r_ll_expr(self):
        self._h_choose([self._s_ll_expr_c0,
                        self._r_ll_qual])

    def _s_ll_expr_c0(self):
        self._h_scope('_s_ll_expr_c0', [self._s_ll_expr_c0_s0,
                                        self._r_sp,
                                        lambda: self._h_ch('+'),
                                        self._r_sp,
                                        self._s_ll_expr_c0_s4,
                                        self._s_ll_expr_c0_s5])

    def _s_ll_expr_c0_s0(self):
        self._h_bind(self._r_ll_qual, 'e1')

    def _s_ll_expr_c0_s4(self):
        self._h_bind(self._r_ll_expr, 'e2')

    def _s_ll_expr_c0_s5(self):
        self._h_succeed(['ll_plus', self._h_get('e1'), self._h_get('e2')])

    def _s_ll_exprs_c0(self):
        self._h_scope('_s_ll_exprs_c0', [self._s_ll_exprs_c0_s0,
                                         self._s_ll_exprs_c0_s1,
                                         self._s_ll_exprs_c0_s2])

    def _s_ll_exprs_c0_s0(self):
        self._h_bind(self._r_ll_expr, 'e')

    def _s_ll_exprs_c0_s1(self):
        self._h_bind(self._s_ll_exprs_c0_s1_l, 'es')

    def _s_ll_exprs_c0_s1_l(self):
        self._h_star(self._s_ll_exprs_c0_s1_l_p, [])

    def _s_ll_exprs_c0_s1_l_p(self):
        self._h_seq([self._r_sp,
                     lambda: self._h_ch(','),
                     self._r_sp,
                     self._r_ll_expr])

    def _s_ll_exprs_c0_s2(self):
        self._h_succeed([self._h_get('e')] + self._h_get('es'))

    def _s_ll_exprs_c1(self):
        self._h_succeed([])

    def _r_ll_qual(self):
        self._h_choose([self._s_ll_qual_c0,
                        self._r_ll_prim])

    def _s_ll_qual_c0(self):
        self._h_scope('_s_ll_qual_c0', [self._s_ll_qual_c0_s0,
                                        self._s_ll_qual_c0_s1,
                                        self._s_ll_qual_c0_s2])

    def _s_ll_qual_c0_s0(self):
        self._h_bind(self._r_ll_prim, 'e')

    def _s_ll_qual_c0_s1(self):
        self._h_bind(self._s_ll_qual_c0_s1_l, 'ps')

    def _s_ll_qual_c0_s1_l(self):
        self._h_plus(self._r_ll_post_op)

    def _s_ll_qual_c0_s2(self):
        self._h_succeed(['ll_qual', self._h_get('e'), self._h_get('ps')])

    def _r_ll_post_op(self):
        self._h_choose([self._s_ll_post_op_c0,
                        self._s_ll_post_op_c1,
                        self._s_ll_post_op_c2])

    def _s_ll_post_op_c0(self):
        self._h_scope('_s_ll_post_op_c0', [lambda: self._h_ch('['),
                                           self._r_sp,
                                           self._s_ll_post_op_c0_s2,
                                           self._r_sp,
                                           lambda: self._h_ch(']'),
                                           self._s_ll_post_op_c0_s5])

    def _s_ll_post_op_c0_s2(self):
        self._h_bind(self._r_ll_expr, 'e')

    def _s_ll_post_op_c0_s5(self):
        self._h_succeed(['ll_getitem', self._h_get('e')])

    def _s_ll_post_op_c1(self):
        self._h_scope('_s_ll_post_op_c1', [lambda: self._h_ch('('),
                                           self._r_sp,
                                           self._s_ll_post_op_c1_s2,
                                           self._r_sp,
                                           lambda: self._h_ch(')'),
                                           self._s_ll_post_op_c1_s5])

    def _s_ll_post_op_c1_s2(self):
        self._h_bind(self._r_ll_exprs, 'es')

    def _s_ll_post_op_c1_s5(self):
        self._h_succeed(['ll_call', self._h_get('es')])

    def _s_ll_post_op_c2(self):
        self._h_scope('_s_ll_post_op_c2', [lambda: self._h_ch('.'),
                                           self._s_ll_post_op_c2_s1,
                                           self._s_ll_post_op_c2_s2])

    def _s_ll_post_op_c2_s1(self):
        self._h_bind(self._r_ident, 'i')

    def _s_ll_post_op_c2_s2(self):
        self._h_succeed(['ll_getattr', self._h_get('i')])

    def _r_ll_prim(self):
        self._h_choose([self._s_ll_prim_c0,
                        self._s_ll_prim_c1,
                        self._s_ll_prim_c2,
                        self._s_ll_prim_c3,
                        self._s_ll_prim_c4,
                        self._s_ll_prim_c5])

    def _s_ll_prim_c0(self):
        self._h_scope('_s_ll_prim_c0', [self._s_ll_prim_c0_s0,
                                        self._s_ll_prim_c0_s1])

    def _s_ll_prim_c0_s0(self):
        self._h_bind(self._r_ident, 'i')

    def _s_ll_prim_c0_s1(self):
        self._h_succeed(['ll_var', self._h_get('i')])

    def _s_ll_prim_c1(self):
        self._h_scope('_s_ll_prim_c1', [self._s_ll_prim_c1_s0,
                                        self._s_ll_prim_c1_s1])

    def _s_ll_prim_c1_s0(self):
        self._h_bind(self._r_digits, 'ds')

    def _s_ll_prim_c1_s1(self):
        self._h_succeed(['ll_num', self._h_get('ds')])

    def _s_ll_prim_c2(self):
        self._h_scope('_s_ll_prim_c2', [lambda: self._h_str('0x', 2),
                                        self._s_ll_prim_c2_s1,
                                        self._s_ll_prim_c2_s2])

    def _s_ll_prim_c2_s1(self):
        self._h_bind(self._r_hexdigits, 'hs')

    def _s_ll_prim_c2_s2(self):
        self._h_succeed(['ll_num', '0x' + self._h_get('hs')])

    def _s_ll_prim_c3(self):
        self._h_scope('_s_ll_prim_c3', [self._s_ll_prim_c3_s0,
                                        self._s_ll_prim_c3_s1])

    def _s_ll_prim_c3_s0(self):
        self._h_bind(self._r_lit, 'l')

    def _s_ll_prim_c3_s1(self):
        self._h_succeed(['ll_lit', self._h_get('l')[1]])

    def _s_ll_prim_c4(self):
        self._h_scope('_s_ll_prim_c4', [lambda: self._h_ch('('),
                                        self._r_sp,
                                        self._s_ll_prim_c4_s2,
                                        self._r_sp,
                                        lambda: self._h_ch(')'),
                                        self._s_ll_prim_c4_s5])

    def _s_ll_prim_c4_s2(self):
        self._h_bind(self._r_ll_expr, 'e')

    def _s_ll_prim_c4_s5(self):
        self._h_succeed(['ll_paren', self._h_get('e')])

    def _s_ll_prim_c5(self):
        self._h_scope('_s_ll_prim_c5', [lambda: self._h_ch('['),
                                        self._r_sp,
                                        self._s_ll_prim_c5_s2,
                                        self._r_sp,
                                        lambda: self._h_ch(']'),
                                        self._s_ll_prim_c5_s5])

    def _s_ll_prim_c5_s2(self):
        self._h_bind(self._r_ll_exprs, 'es')

    def _s_ll_prim_c5_s5(self):
        self._h_succeed(['ll_arr', self._h_get('es')])

    def _r_digits(self):
        self._h_scope('_r_digits', [self._s_digits_s0,
                                    self._s_digits_s1])

    def _s_digits_s0(self):
        self._h_bind(self._s_digits_s0_l, 'ds')

    def _s_digits_s0_l(self):
        self._h_plus(self._r_digit)

    def _s_digits_s1(self):
        self._h_succeed(self._f_cat(self._h_get('ds')))

    def _r_hexdigits(self):
        self._h_scope('_r_hexdigits', [self._s_hexdigits_s0,
                                       self._s_hexdigits_s1])

    def _s_hexdigits_s0(self):
        self._h_bind(self._s_hexdigits_s0_l, 'hs')

    def _s_hexdigits_s0_l(self):
        self._h_plus(self._r_hex)

    def _s_hexdigits_s1(self):
        self._h_succeed(self._f_cat(self._h_get('hs')))

    def _r_hex(self):
        self._h_choose([self._r_digit,
                        self._s_hex_c1,
                        self._s_hex_c2])

    def _s_hex_c1(self):
        self._h_range('a', 'f')

    def _s_hex_c2(self):
        self._h_range('A', 'F')

    def _s_hex_esc_s1(self):
        self._h_bind(self._r_hex, 'h1')

    def _s_hex_esc_s2(self):
        self._h_bind(self._r_hex, 'h2')

    def _s_hex_esc_s3(self):
        self._h_succeed(self._f_xtou(self._h_get('h1') + self._h_get('h2')))

    def _s_hexdigits_s0(self):
        self._h_bind(self._s_hexdigits_s0_l, 'hs')

    def _s_hexdigits_s0_l(self):
        self._h_plus(self._r_hex)

    def _s_hexdigits_s1(self):
        self._h_succeed(self._f_cat(self._h_get('hs')))

    def _r_digit(self):
        self._h_range('0', '9')

    def _s_digits_s0(self):
        self._h_bind(self._s_digits_s0_l, 'ds')

    def _s_digits_s0_l(self):
        self._h_plus(self._r_digit)

    def _s_digits_s1(self):
        self._h_succeed(self._f_cat(self._h_get('ds')))

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
