grammar = sp expr sp end       -> _2

expr    = expr sp '+' sp {num} -> [_1, '+', _5]
        | expr sp '-' sp {num} -> [_1, '-', _5]
        | {num}                -> _1

num     = ('0'..'9')+

sp      = (' ' | '\n')*
