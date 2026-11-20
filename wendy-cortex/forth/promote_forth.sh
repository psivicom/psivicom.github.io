#!/bin/bash
# WENDY FORTH Mutation Promotion
# SPDX-License-Identifier: EUPL-1.2
# Appends the fast-mean word to the dictionary file

DICT_FILE="wendy_dictionary.fth"

cat >> "$DICT_FILE" << 'PROMOTE_EOF'

\ WENDY invented this optimized word at runtime
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
PROMOTE_EOF

echo "✅ fast-mean appended to $DICT_FILE"
