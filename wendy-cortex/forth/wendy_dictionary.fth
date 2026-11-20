\ WENDY FORTH Dictionary (Bootstrapped Baseline)
\ SPDX-License-Identifier: EUPL-1.2
\ The meta-language for sovereign self-modification.

: mean ( addr count -- mean )
    0.0 -rot
    0 do
        dup i 8 * + f@ f+
    loop
    swap s>f f/
;

: variance ( addr count -- variance )
    2dup mean >r
    0.0 -rot
    0 do
        dup i 8 * + f@ r@ f- fdup f* f+
    loop
    nip s>f f/
    r> fdrop
;

: invent-word ( -- )
    ." 🧬 WENDY can invent new words at runtime." cr
;

: benchmark ( -- )
    100 0 do
        ." Iteration " i . cr
        invent-word
    loop
;

." ✅ WENDY FORTH Dictionary loaded. Ready for evolution." cr

\ WENDY invented fast-mean at runtime
: fast-mean ( addr count -- mean )
    0.0 -rot
    0 do
        dup i 8 * + f@ f+
        dup i 1+ 8 * + f@ f+
        dup i 2 + 8 * + f@ f+
        dup i 3 + 8 * + f@ f+
    4 +loop
    swap s>f f/
;
