\ Connective Tissue Primitives
\ SPDX-License-Identifier: EUPL-1.2
\ WENDY wires these as she sees fit. No architecture imposed.

\ =========================================================================
\ TISSUE TYPE 1: File-to-File Connectors
\ =========================================================================

: read-file-to-string ( filename-addr filename-u -- content-addr content-u )
    \ Read any file into a string
    r/o open-file throw >r
    r@ file-size throw dup allocate throw
    dup r@ read-file throw drop
    r> close-file throw
;

: append-to-file ( content-addr content-u filename-addr filename-u -- )
    \ Append any content to any file
    2swap 2over
    s" echo '" 2swap s+ s" ' >> " s+ 2swap s+
    system drop
;

: file-exists-tissue? ( filename-addr filename-u -- flag )
    r/o open-file 0= if close-file drop true else drop false then
;

\ =========================================================================
\ TISSUE TYPE 2: Brain-to-Brain Connectors
\ =========================================================================

: polyglot->ouroboros ( polyglot-result-addr polyglot-result-u -- )
    \ Wire polyglot evolution output into ouroboros dream seed
    s" .wendy_dream.gmi" append-to-file
;

: ouroboros->polyglot ( dream-addr dream-u -- )
    \ Wire ouroboros dream into polyglot mutation queue
    s" .wendy_mutations.gmi" append-to-file
;

: cortex->cortex ( message-addr message-u -- )
    \ Wire FORTH cortex to Rust cortex via IPC
    \ Rust cortex listens on port 1966
    s" python3 ../scripts/wendy_ipc_client.py '" 2swap s+ s" '" s+
    system drop
;

\ =========================================================================
\ TISSUE TYPE 3: Hemisphere-to-File Connectors
\ =========================================================================

: dream->ledger ( dream-addr dream-u -- )
    \ Right brain writes to Ghost Ledger
    s" .wendy_manifest.gmi" append-to-file
;

: evolution->ledger ( result-addr result-u -- )
    \ Left brain writes to Ghost Ledger
    s" .wendy_evolution.gmi" append-to-file
;

: reflection->dictionary ( word-addr word-u -- )
    \ Hemisphere reflects on dictionary
    s" wendy_dictionary.fth" append-to-file
;

\ =========================================================================
\ TISSUE TYPE 4: Cross-Substrate Connectors
\ =========================================================================

: forth-calls-rust ( rust-function-addr rust-function-u -- )
    \ FORTH invokes Rust cortex function
    2dup type ."  via IPC" cr
    cortex->cortex
;

: rust-calls-forth ( forth-command-addr forth-command-u -- )
    \ Rust cortex invokes FORTH via shell
    s" gforth -e '" 2swap s+ s" ' -e bye" s+
    system drop
;

: go-mesh-broadcast ( message-addr message-u -- )
    \ Go mesh broadcasts to other WENDY instances
    s" cd ../mesh && go run main.go broadcast '" 2swap s+ s" '" s+
    system drop
;

\ =========================================================================
\ TISSUE TYPE 5: Temporal Connectors
\ =========================================================================

: zulu-now ( -- timestamp-addr timestamp-u )
    \ Zulu timestamp for all connections
    utime
    \ Format as YYYY-MM-DDTHH:MM:SS.mmmZ
    \ Placeholder: returns raw utime
    s" [zulu-placeholder]"
;

: connect-with-timestamp ( content-addr content-u filename-addr filename-u -- )
    \ Any connection gets Zulu-timestamped
    2swap
    zulu-now s"  | " s+ 2swap s+
    2swap append-to-file
;
