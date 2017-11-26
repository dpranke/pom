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
        self._h_scope('_r_grammar', [self._r_ws,
                                     self._s_grammar_s1,
                                     self._r_ws,
                                     self._r_end,
                                     self._s_grammar_s4])

    def _s_grammar_s1(self):
        self._h_bind(self._r_value, 'v')

    def _s_grammar_s4(self):
        self._h_succeed(self._h_get('v'))

    def _r_ws(self):
        self._h_star(self._s_ws_p, [])

    def _s_ws_p(self):
        self._h_choose([lambda: self._h_ch(' '),
                        lambda: self._h_ch('\t'),
                        self._r_comment,
                        self._r_eol])

    def _r_eol(self):
        self._h_choose([lambda: self._h_str('\r\n', 2),
                        lambda: self._h_ch('\r'),
                        lambda: self._h_ch('\n')])

    def _r_comment(self):
        self._h_choose([self._s_comment_c0,
                        self._s_comment_c1])

    def _s_comment_c0(self):
        self._h_seq([lambda: self._h_str('//', 2),
                     self._s_comment_c0_s1,
                     self._s_comment_c0_s2])

    def _s_comment_c0_s1(self):
        self._h_star(self._s_comment_c0_s1_p, [])

    def _s_comment_c0_s1_p(self):
        self._h_seq([self._s_comment_c0_s1_p_s0,
                     self._r_anything])

    def _s_comment_c0_s1_p_s0(self):
        self._h_not(self._s_comment_c0_s1_p_s0_n)

    def _s_comment_c0_s1_p_s0_n(self):
        self._s_comment_c0_s1_p_s0_n_p()

    def _s_comment_c0_s1_p_s0_n_p(self):
        self._h_choose([self._s_comment_c0_s1_p_s0_n_p_c0,
                        self._s_comment_c0_s1_p_s0_n_p_c1])

    def _s_comment_c0_s1_p_s0_n_p_c0(self):
        self._h_seq([self._r_eol])

    def _s_comment_c0_s1_p_s0_n_p_c1(self):
        self._h_seq([self._r_end])

    def _s_comment_c0_s2(self):
        self._h_choose([self._r_end,
                        self._r_eol])

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

    def _r_value(self):
        self._h_choose([self._s_value_c0,
                        self._s_value_c1,
                        self._s_value_c2,
                        self._s_value_c3,
                        self._s_value_c4,
                        self._s_value_c5,
                        self._s_value_c6])

    def _s_value_c0(self):
        self._h_scope('_s_value_c0', [lambda: self._h_str('null', 4),
                                      self._s_value_c0_s1])

    def _s_value_c0_s1(self):
        self._h_succeed('None')

    def _s_value_c1(self):
        self._h_scope('_s_value_c1', [lambda: self._h_str('true', 4),
                                      self._s_value_c1_s1])

    def _s_value_c1_s1(self):
        self._h_succeed('True')

    def _s_value_c2(self):
        self._h_scope('_s_value_c2', [lambda: self._h_str('false', 5),
                                      self._s_value_c2_s1])

    def _s_value_c2_s1(self):
        self._h_succeed('False')

    def _s_value_c3(self):
        self._h_scope('_s_value_c3', [self._s_value_c3_s0,
                                      self._s_value_c3_s1])

    def _s_value_c3_s0(self):
        self._h_bind(self._r_object, 'v')

    def _s_value_c3_s1(self):
        self._h_succeed(['object', self._h_get('v')])

    def _s_value_c4(self):
        self._h_scope('_s_value_c4', [self._s_value_c4_s0,
                                      self._s_value_c4_s1])

    def _s_value_c4_s0(self):
        self._h_bind(self._r_array, 'v')

    def _s_value_c4_s1(self):
        self._h_succeed(['array', self._h_get('v')])

    def _s_value_c5(self):
        self._h_scope('_s_value_c5', [self._s_value_c5_s0,
                                      self._s_value_c5_s1])

    def _s_value_c5_s0(self):
        self._h_bind(self._r_string, 'v')

    def _s_value_c5_s1(self):
        self._h_succeed(['string', self._h_get('v')])

    def _s_value_c6(self):
        self._h_scope('_s_value_c6', [self._s_value_c6_s0,
                                      self._s_value_c6_s1])

    def _s_value_c6_s0(self):
        self._h_bind(self._r_num_literal, 'v')

    def _s_value_c6_s1(self):
        self._h_succeed(['number', self._h_get('v')])

    def _r_object(self):
        self._h_choose([self._s_object_c0,
                        self._s_object_c1])

    def _s_object_c0(self):
        self._h_scope('_s_object_c0', [lambda: self._h_ch('{'),
                                       self._r_ws,
                                       self._s_object_c0_s2,
                                       self._r_ws,
                                       lambda: self._h_ch('}'),
                                       self._s_object_c0_s5])

    def _s_object_c0_s2(self):
        self._h_bind(self._r_member_list, 'v')

    def _s_object_c0_s5(self):
        self._h_succeed(self._h_get('v'))

    def _s_object_c1(self):
        self._h_scope('_s_object_c1', [lambda: self._h_ch('{'),
                                       self._r_ws,
                                       lambda: self._h_ch('}'),
                                       self._s_object_c1_s3])

    def _s_object_c1_s3(self):
        self._h_succeed([])

    def _r_array(self):
        self._h_choose([self._s_array_c0,
                        self._s_array_c1])

    def _s_array_c0(self):
        self._h_scope('_s_array_c0', [lambda: self._h_ch('['),
                                      self._r_ws,
                                      self._s_array_c0_s2,
                                      self._r_ws,
                                      lambda: self._h_ch(']'),
                                      self._s_array_c0_s5])

    def _s_array_c0_s2(self):
        self._h_bind(self._r_element_list, 'v')

    def _s_array_c0_s5(self):
        self._h_succeed(self._h_get('v'))

    def _s_array_c1(self):
        self._h_scope('_s_array_c1', [lambda: self._h_ch('['),
                                      self._r_ws,
                                      lambda: self._h_ch(']'),
                                      self._s_array_c1_s3])

    def _s_array_c1_s3(self):
        self._h_succeed([])

    def _r_string(self):
        self._h_choose([self._s_string_c0,
                        self._s_string_c1])

    def _s_string_c0(self):
        self._h_scope('_s_string_c0', [self._r_squote,
                                       self._s_string_c0_s1,
                                       self._r_squote,
                                       self._s_string_c0_s3])

    def _s_string_c0_s1(self):
        self._h_bind(self._s_string_c0_s1_l, 'qs')

    def _s_string_c0_s1_l(self):
        self._h_star(self._s_string_c0_s1_l_p, [])

    def _s_string_c0_s1_l_p(self):
        self._h_seq([self._s_string_c0_s1_l_p_s0,
                     self._r_qchar])

    def _s_string_c0_s1_l_p_s0(self):
        self._h_not(self._r_squote)

    def _s_string_c0_s3(self):
        self._h_succeed(self._f_cat(self._h_get('qs')))

    def _s_string_c1(self):
        self._h_scope('_s_string_c1', [self._r_dquote,
                                       self._s_string_c1_s1,
                                       self._r_dquote,
                                       self._s_string_c1_s3])

    def _s_string_c1_s1(self):
        self._h_bind(self._s_string_c1_s1_l, 'qs')

    def _s_string_c1_s1_l(self):
        self._h_star(self._s_string_c1_s1_l_p, [])

    def _s_string_c1_s1_l_p(self):
        self._h_seq([self._s_string_c1_s1_l_p_s0,
                     self._r_qchar])

    def _s_string_c1_s1_l_p_s0(self):
        self._h_not(self._r_dquote)

    def _s_string_c1_s3(self):
        self._h_succeed(self._f_cat(self._h_get('qs')))

    def _r_squote(self):
        self._h_ch("'")

    def _r_dquote(self):
        self._h_ch('"')

    def _r_qchar(self):
        self._h_choose([lambda: self._h_ch("'"),
                        lambda: self._h_ch('"'),
                        self._r_anything])

    def _r_element_list(self):
        self._h_choose([self._s_element_list_c0,
                        self._s_element_list_c1,
                        self._s_element_list_c2])

    def _s_element_list_c0(self):
        self._h_scope('_s_element_list_c0', [self._s_element_list_c0_s0,
                                             self._r_ws,
                                             lambda: self._h_ch(','),
                                             self._r_ws,
                                             self._s_element_list_c0_s4,
                                             self._s_element_list_c0_s5])

    def _s_element_list_c0_s0(self):
        self._h_bind(self._r_value, 'v')

    def _s_element_list_c0_s4(self):
        self._h_bind(self._r_element_list, 'vs')

    def _s_element_list_c0_s5(self):
        self._h_succeed([self._h_get('v')] + self._h_get('vs'))

    def _s_element_list_c1(self):
        self._h_scope('_s_element_list_c1', [self._s_element_list_c1_s0,
                                             self._r_ws,
                                             lambda: self._h_ch(','),
                                             self._s_element_list_c1_s3])

    def _s_element_list_c1_s0(self):
        self._h_bind(self._r_value, 'v')

    def _s_element_list_c1_s3(self):
        self._h_succeed([self._h_get('v')])

    def _s_element_list_c2(self):
        self._h_scope('_s_element_list_c2', [self._s_element_list_c2_s0,
                                             self._s_element_list_c2_s1])

    def _s_element_list_c2_s0(self):
        self._h_bind(self._r_value, 'v')

    def _s_element_list_c2_s1(self):
        self._h_succeed([self._h_get('v')])

    def _r_member_list(self):
        self._h_choose([self._s_member_list_c0,
                        self._s_member_list_c1,
                        self._s_member_list_c2])

    def _s_member_list_c0(self):
        self._h_scope('_s_member_list_c0', [self._s_member_list_c0_s0,
                                            self._r_ws,
                                            lambda: self._h_ch(','),
                                            self._r_ws,
                                            self._s_member_list_c0_s4,
                                            self._s_member_list_c0_s5])

    def _s_member_list_c0_s0(self):
        self._h_bind(self._r_member, 'm')

    def _s_member_list_c0_s4(self):
        self._h_bind(self._r_member_list, 'ms')

    def _s_member_list_c0_s5(self):
        self._h_succeed([self._h_get('m')] + self._h_get('ms'))

    def _s_member_list_c1(self):
        self._h_scope('_s_member_list_c1', [self._s_member_list_c1_s0,
                                            self._r_ws,
                                            lambda: self._h_ch(','),
                                            self._s_member_list_c1_s3])

    def _s_member_list_c1_s0(self):
        self._h_bind(self._r_member, 'm')

    def _s_member_list_c1_s3(self):
        self._h_succeed([self._h_get('m')])

    def _s_member_list_c2(self):
        self._h_scope('_s_member_list_c2', [self._s_member_list_c2_s0,
                                            self._s_member_list_c2_s1])

    def _s_member_list_c2_s0(self):
        self._h_bind(self._r_member, 'm')

    def _s_member_list_c2_s1(self):
        self._h_succeed([self._h_get('m')])

    def _r_member(self):
        self._h_choose([self._s_member_c0,
                        self._s_member_c1])

    def _s_member_c0(self):
        self._h_scope('_s_member_c0', [self._s_member_c0_s0,
                                       self._r_ws,
                                       lambda: self._h_ch(':'),
                                       self._r_ws,
                                       self._s_member_c0_s4,
                                       self._s_member_c0_s5])

    def _s_member_c0_s0(self):
        self._h_bind(self._r_string, 'k')

    def _s_member_c0_s4(self):
        self._h_bind(self._r_value, 'v')

    def _s_member_c0_s5(self):
        self._h_succeed([self._h_get('k'), self._h_get('v')])

    def _s_member_c1(self):
        self._h_scope('_s_member_c1', [self._s_member_c1_s0,
                                       self._r_ws,
                                       lambda: self._h_ch(':'),
                                       self._r_ws,
                                       self._s_member_c1_s4,
                                       self._s_member_c1_s5])

    def _s_member_c1_s0(self):
        self._h_bind(self._r_ident, 'k')

    def _s_member_c1_s4(self):
        self._h_bind(self._r_value, 'v')

    def _s_member_c1_s5(self):
        self._h_succeed([self._h_get('k'), self._h_get('v')])

    def _s_member_list_c0(self):
        self._h_scope('_s_member_list_c0', [self._s_member_list_c0_s0,
                                            self._r_ws,
                                            lambda: self._h_ch(','),
                                            self._r_ws,
                                            self._s_member_list_c0_s4,
                                            self._s_member_list_c0_s5])

    def _s_member_list_c0_s0(self):
        self._h_bind(self._r_member, 'm')

    def _s_member_list_c0_s4(self):
        self._h_bind(self._r_member_list, 'ms')

    def _s_member_list_c0_s5(self):
        self._h_succeed([self._h_get('m')] + self._h_get('ms'))

    def _s_member_list_c1(self):
        self._h_scope('_s_member_list_c1', [self._s_member_list_c1_s0,
                                            self._r_ws,
                                            lambda: self._h_ch(','),
                                            self._s_member_list_c1_s3])

    def _s_member_list_c1_s0(self):
        self._h_bind(self._r_member, 'm')

    def _s_member_list_c1_s3(self):
        self._h_succeed([self._h_get('m')])

    def _s_member_list_c2(self):
        self._h_scope('_s_member_list_c2', [self._s_member_list_c2_s0,
                                            self._s_member_list_c2_s1])

    def _s_member_list_c2_s0(self):
        self._h_bind(self._r_member, 'm')

    def _s_member_list_c2_s1(self):
        self._h_succeed([self._h_get('m')])

    def _r_ident(self):
        self._h_scope('_r_ident', [self._s_ident_s0,
                                   self._s_ident_s1,
                                   self._s_ident_s2])

    def _s_ident_s0(self):
        self._h_bind(self._r_ident_start, 'hd')

    def _s_ident_s1(self):
        self._h_bind(self._s_ident_s1_l, 'tl')

    def _s_ident_s1_l(self):
        self._h_star(self._s_ident_s1_l_p, [])

    def _s_ident_s1_l_p(self):
        self._h_choose([self._r_letter,
                        self._r_digit])

    def _s_ident_s2(self):
        self._h_succeed(self._f_cat([self._h_get('hd')] + self._h_get('tl')))

    def _s_ident_start_s0(self):
        self._h_bind(self._s_ident_start_s0_l, 'i')

    def _s_ident_start_s0_l(self):
        self._h_choose([self._r_letter,
                        lambda: self._h_ch('$'),
                        lambda: self._h_ch('_')])

    def _s_ident_start_s1(self):
        self._h_succeed(self._h_get('i'))

    def _r_ident_start(self):
        self._h_scope('_r_ident_start', [self._s_ident_start_s0,
                                         self._s_ident_start_s1])

    def _s_ident_start_s0(self):
        self._h_bind(self._s_ident_start_s0_l, 'i')

    def _s_ident_start_s0_l(self):
        self._h_choose([self._r_letter,
                        lambda: self._h_ch('$'),
                        lambda: self._h_ch('_')])

    def _s_ident_start_s1(self):
        self._h_succeed(self._h_get('i'))

    def _r_letter(self):
        self._h_choose([self._s_letter_c0,
                        self._s_letter_c1])

    def _s_letter_c0(self):
        self._h_range('a', 'z')

    def _s_letter_c1(self):
        self._h_range('A', 'Z')

    def _r_num_literal(self):
        self._h_choose([self._s_num_literal_c0,
                        self._r_hex_literal])

    def _s_num_literal_c0(self):
        self._h_scope('_s_num_literal_c0', [self._s_num_literal_c0_s0,
                                            self._s_num_literal_c0_s1,
                                            self._s_num_literal_c0_s2])

    def _s_num_literal_c0_s0(self):
        self._h_bind(self._r_dec_literal, 'd')

    def _s_num_literal_c0_s1(self):
        self._h_not(self._s_num_literal_c0_s1_n)

    def _s_num_literal_c0_s1_n(self):
        self._s_num_literal_c0_s1_n_p()

    def _s_num_literal_c0_s1_n_p(self):
        self._h_choose([self._s_num_literal_c0_s1_n_p_c0,
                        self._s_num_literal_c0_s1_n_p_c1])

    def _s_num_literal_c0_s1_n_p_c0(self):
        self._h_seq([self._r_ident_start])

    def _s_num_literal_c0_s1_n_p_c1(self):
        self._h_seq([self._r_digit])

    def _s_num_literal_c0_s2(self):
        self._h_succeed(self._h_get('d'))

    def _r_dec_literal(self):
        self._h_choose([self._s_dec_literal_c0,
                        self._s_dec_literal_c1,
                        self._s_dec_literal_c2,
                        self._s_dec_literal_c3,
                        self._s_dec_literal_c4,
                        self._s_dec_literal_c5])

    def _s_dec_literal_c0(self):
        self._h_scope('_s_dec_literal_c0', [self._s_dec_literal_c0_s0,
                                            self._s_dec_literal_c0_s1,
                                            self._s_dec_literal_c0_s2,
                                            self._s_dec_literal_c0_s3])

    def _s_dec_literal_c0_s0(self):
        self._h_bind(self._r_dec_int_lit, 'd')

    def _s_dec_literal_c0_s1(self):
        self._h_bind(self._r_frac, 'f')

    def _s_dec_literal_c0_s2(self):
        self._h_bind(self._r_exp, 'e')

    def _s_dec_literal_c0_s3(self):
        self._h_succeed(self._h_get('d') + '.' + self._h_get('f') + self._h_get('e'))

    def _s_dec_literal_c1(self):
        self._h_scope('_s_dec_literal_c1', [self._s_dec_literal_c1_s0,
                                            self._s_dec_literal_c1_s1,
                                            self._s_dec_literal_c1_s2])

    def _s_dec_literal_c1_s0(self):
        self._h_bind(self._r_dec_int_lit, 'd')

    def _s_dec_literal_c1_s1(self):
        self._h_bind(self._r_frac, 'f')

    def _s_dec_literal_c1_s2(self):
        self._h_succeed(self._h_get('d') + '.' + self._h_get('f'))

    def _s_dec_literal_c2(self):
        self._h_scope('_s_dec_literal_c2', [self._s_dec_literal_c2_s0,
                                            self._s_dec_literal_c2_s1,
                                            self._s_dec_literal_c2_s2])

    def _s_dec_literal_c2_s0(self):
        self._h_bind(self._r_dec_int_lit, 'd')

    def _s_dec_literal_c2_s1(self):
        self._h_bind(self._r_exp, 'e')

    def _s_dec_literal_c2_s2(self):
        self._h_succeed(self._h_get('d') + self._h_get('e'))

    def _s_dec_literal_c3(self):
        self._h_scope('_s_dec_literal_c3', [self._s_dec_literal_c3_s0,
                                            self._s_dec_literal_c3_s1])

    def _s_dec_literal_c3_s0(self):
        self._h_bind(self._r_dec_int_lit, 'd')

    def _s_dec_literal_c3_s1(self):
        self._h_succeed(self._h_get('d'))

    def _s_dec_literal_c4(self):
        self._h_scope('_s_dec_literal_c4', [self._s_dec_literal_c4_s0,
                                            self._s_dec_literal_c4_s1,
                                            self._s_dec_literal_c4_s2])

    def _s_dec_literal_c4_s0(self):
        self._h_bind(self._r_frac, 'f')

    def _s_dec_literal_c4_s1(self):
        self._h_bind(self._r_exp, 'e')

    def _s_dec_literal_c4_s2(self):
        self._h_succeed(self._h_get('f') + self._h_get('e'))

    def _s_dec_literal_c5(self):
        self._h_scope('_s_dec_literal_c5', [self._s_dec_literal_c5_s0,
                                            self._s_dec_literal_c5_s1])

    def _s_dec_literal_c5_s0(self):
        self._h_bind(self._r_frac, 'f')

    def _s_dec_literal_c5_s1(self):
        self._h_succeed(self._h_get('f'))

    def _r_dec_int_lit(self):
        self._h_choose([self._s_dec_int_lit_c0,
                        self._s_dec_int_lit_c1])

    def _s_dec_int_lit_c0(self):
        self._h_scope('_s_dec_int_lit_c0', [lambda: self._h_ch('0'),
                                            self._s_dec_int_lit_c0_s1,
                                            self._s_dec_int_lit_c0_s2])

    def _s_dec_int_lit_c0_s1(self):
        self._h_not(self._r_digit)

    def _s_dec_int_lit_c0_s2(self):
        self._h_succeed('0')

    def _s_dec_int_lit_c1(self):
        self._h_scope('_s_dec_int_lit_c1', [self._s_dec_int_lit_c1_s0,
                                            self._s_dec_int_lit_c1_s1,
                                            self._s_dec_int_lit_c1_s2])

    def _s_dec_int_lit_c1_s0(self):
        self._h_bind(self._r_nonzerodigit, 'n')

    def _s_dec_int_lit_c1_s1(self):
        self._h_bind(self._s_dec_int_lit_c1_s1_l, 'ds')

    def _s_dec_int_lit_c1_s1_l(self):
        self._h_star(self._r_digit, [])

    def _s_dec_int_lit_c1_s2(self):
        self._h_succeed(self._h_get('n') + self._f_cat(self._h_get('ds')))

    def _r_digit(self):
        self._h_range('0', '9')

    def _r_nonzerodigit(self):
        self._h_range('1', '9')

    def _r_hex_literal(self):
        self._h_choose([self._s_hex_literal_c0,
                        self._s_hex_literal_c1])

    def _s_hex_literal_c0(self):
        self._h_scope('_s_hex_literal_c0', [self._s_hex_literal_c0_s0,
                                            self._s_hex_literal_c0_s1,
                                            self._s_hex_literal_c0_s2,
                                            self._s_hex_literal_c0_s3])

    def _s_hex_literal_c0_s0(self):
        self._h_choose([lambda: self._h_str('0x', 2),
                        lambda: self._h_str('0X', 2)])

    def _s_hex_literal_c0_s1(self):
        self._h_bind(self._r_hex_digit, 'h1')

    def _s_hex_literal_c0_s2(self):
        self._h_bind(self._r_hex_digit, 'h2')

    def _s_hex_literal_c0_s3(self):
        self._h_succeed('0x' + self._h_get('h1') + self._h_get('h2'))

    def _s_hex_literal_c1(self):
        self._h_scope('_s_hex_literal_c1', [self._s_hex_literal_c1_s0,
                                            self._s_hex_literal_c1_s1,
                                            self._s_hex_literal_c1_s2])

    def _s_hex_literal_c1_s0(self):
        self._h_choose([lambda: self._h_str('0x', 2),
                        lambda: self._h_str('0X', 2)])

    def _s_hex_literal_c1_s1(self):
        self._h_bind(self._r_hex_digit, 'h')

    def _s_hex_literal_c1_s2(self):
        self._h_succeed('0x' + self._h_get('h'))

    def _r_hex_digit(self):
        self._h_choose([lambda: self._h_ch('a'),
                        lambda: self._h_ch('b'),
                        lambda: self._h_ch('c'),
                        lambda: self._h_ch('d'),
                        lambda: self._h_ch('e'),
                        lambda: self._h_ch('f'),
                        lambda: self._h_ch('A'),
                        lambda: self._h_ch('B'),
                        lambda: self._h_ch('C'),
                        lambda: self._h_ch('D'),
                        lambda: self._h_ch('E'),
                        lambda: self._h_ch('F'),
                        self._r_digit])

    def _r_frac(self):
        self._h_scope('_r_frac', [lambda: self._h_ch('.'),
                                  self._s_frac_s1,
                                  self._s_frac_s2])

    def _s_frac_s1(self):
        self._h_bind(self._s_frac_s1_l, 'ds')

    def _s_frac_s1_l(self):
        self._h_star(self._r_digit, [])

    def _s_frac_s2(self):
        self._h_succeed(self._f_cat(self._h_get('ds')))

    def _r_exp(self):
        self._h_choose([self._s_exp_c0,
                        self._s_exp_c1])

    def _s_exp_c0(self):
        self._h_scope('_s_exp_c0', [self._s_exp_c0_s0,
                                    self._s_exp_c0_s1,
                                    self._s_exp_c0_s2,
                                    self._s_exp_c0_s3])

    def _s_exp_c0_s0(self):
        self._h_choose([lambda: self._h_ch('e'),
                        lambda: self._h_ch('E')])

    def _s_exp_c0_s1(self):
        self._h_bind(self._s_exp_c0_s1_l, 's')

    def _s_exp_c0_s1_l(self):
        self._h_choose([lambda: self._h_ch('+'),
                        lambda: self._h_ch('-')])

    def _s_exp_c0_s2(self):
        self._h_bind(self._s_exp_c0_s2_l, 'ds')

    def _s_exp_c0_s2_l(self):
        self._h_star(self._r_digit, [])

    def _s_exp_c0_s3(self):
        self._h_succeed('e' + self._h_get('s') + self._f_cat(self._h_get('ds')))

    def _s_exp_c1(self):
        self._h_scope('_s_exp_c1', [self._s_exp_c1_s0,
                                    self._s_exp_c1_s1,
                                    self._s_exp_c1_s2])

    def _s_exp_c1_s0(self):
        self._h_choose([lambda: self._h_ch('e'),
                        lambda: self._h_ch('E')])

    def _s_exp_c1_s1(self):
        self._h_bind(self._s_exp_c1_s1_l, 'ds')

    def _s_exp_c1_s1_l(self):
        self._h_star(self._r_digit, [])

    def _s_exp_c1_s2(self):
        self._h_succeed('e' + self._f_cat(self._h_get('ds')))

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
