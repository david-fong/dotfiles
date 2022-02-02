" some ideas taken from https://github.com/tpope/vim-sensible/blob/master/plugin/sensible.vim

set encoding=utf-8
scriptencoding utf-8
source ${XDG_CONFIG_HOME}/vim/_xdg_compat.vim
source ${XDG_CONFIG_HOME}/vim/_basic.vim
source ${XDG_CONFIG_HOME}/vim/_display.vim
source ${XDG_CONFIG_HOME}/vim/_keys_modern.vim
source ${XDG_CONFIG_HOME}/vim/_keys_iokl.vim
source ${XDG_CONFIG_HOME}/vim/_david.vim

"autocmd BufRead,BufNewFile *.c,*.h set cindent
"retab


" try to start cursorline at top of screen ------
augroup VimrcGroup
    autocmd!
    autocmd BufRead,BufNewFile * call OnOpenFile()
augroup END
function! OnOpenFile()
    set hlsearch
    execute "normal zt"
    if &readonly
        set nomodifiable
    endif
endfunction


" smoother scrolling: ---------------------------
set scrolloff=5
set sidescroll=1
set sidescrolloff=7
noremap  <silent> <ScrollWheelUp>   <C-Y>
noremap  <silent> <ScrollWheelDown> <C-E>
inoremap <silent> <ScrollWheelUp>   <C-O><C-Y>
inoremap <silent> <ScrollWheelDown> <C-O><C-E>



" readline-style bindings: ----------------------
cnoremap          <C-A>  <C-B>
inoremap <silent> <C-A>  <C-O>^
inoremap <silent> <C-E>  <C-O>$
inoremap <silent> <ESC>f <C-O>w
"inoremap <silent> <C-D>  <DEL>



" set autoread
" check for external changes (from u/weisenzahm on reddit)
" check for file modifications automatically (current buffer only).
" use :NoAutoChecktime to disable it (uses b:autochecktime)
function! MyAutoCheckTime()
    " only check timestamp for normal files
    if &buftype != '' | return | endif
    if ! exists('b:autochecktime') || b:autochecktime
        checktime %
        let b:autochecktime = 1
    endif
endfunction
augroup MyAutoChecktime
    au!
    au FocusGained,BufEnter,CursorHold,CursorHoldI * call MyAutoCheckTime()
augroup END
command! NoAutoChecktime let b:autochecktime=0


" spelling is hard: -----------------------------
iabbrev teh the
inoremap {<CR> {<CR>}<ESC>O
function! FixMyLowerCaseSentances()
    sil! %s/\([.]\s\+\)\([a-z]\)/\1\u\2/g
endfunction


" for hex editing: ------------------------------
augroup Binary
    au!
    au BufReadPre  *.bin let &bin=1
    au BufReadPost *.bin if &bin | %!xxd
    au BufReadPost *.bin set ft=xxd | endif
    au BufWritePre *.bin if &bin | %!xxd -r
    au BufWritePre *.bin endif
    au BufWritePost *.bin if &bin | %!xxd
    au BufWritePost *.bin set nomod | endif
augroup END


function! SynGroup()
    let l:s = synID(line('.'), col('.'), 1)
    echo synIDattr(l:s, 'name') . ' -> ' . synIDattr(synIDtrans(l:s), 'name')
endfun
