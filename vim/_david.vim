
" systemverilog module signal param list --------
"   search back for <module_name>"(",
"   then search forward for semicolon.
" substitute flags:
" - no error message
" - replace all occurances in each line
" -
function! VerilogParamFormat()
    sil! +?^[^.]*(? ,    s/(/(
/e          " insert newline after '('
    sil! +?^[^.]*(? ;/;/ s/);$/
);/eg      " put ');' on new line
    sil!  ?^[^.]*(? ;/;/ s/,\s*/,
\1/eg    " put all signals on single lines
    sil!  ?^[^.]*(? ;/;/ g/^\s*$/d          " delete empty lines
    sil!  ?^[^.]*(?+;/;/-s/^\s*/    /eg     " use four leading spaces
    sil!  ?^[^.]*(? ;/;/ s/input\s*/input  /eg  " use four leading spaces
endfunction


hi typescriptString         ctermfg=cyan
hi typescriptTemplate       ctermfg=cyan
hi typescriptTemplateSB     ctermfg=cyan
hi typescriptDocComment     ctermfg=white

hi typescriptExport         ctermfg=green
hi typescriptModule         ctermfg=white

hi typescriptTypeReference  ctermfg=Red
hi typescriptTypeAnnotation ctermfg=green
hi typescriptStatementKeyword ctermfg=green

hi typescriptObjectLabel    ctermfg=blue
hi typescriptMember         ctermfg=blue
hi typescriptFuncName       ctermfg=blue
hi typescriptVariableDeclaration ctermfg=blue

hi typescriptVariable       ctermfg=white
hi typescriptAccessibilityModifier ctermfg=white
hi typescriptReadonly       ctermfg=white

hi typescriptArrayMethod    ctermfg=blue