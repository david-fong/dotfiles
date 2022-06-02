
set whichwrap=b,s,<,>,[,]

" save using ctrl+s: ----------------------------
noremap  <silent> <C-S> :update<CR>
vnoremap <silent> <C-S> <C-C>:update<CR>gv
inoremap <silent> <C-S> <C-O>:update<CR>

" exit using ctrl+x: ----------------------------
noremap  <silent> <C-X> :q<CR>
vnoremap <silent> <C-X> :q<CR>
inoremap <silent> <C-X> <ESC>:q<CR>

" close all using ctrl+q: -----------------------
noremap  <silent> <C-Q> :qa<CR>
vnoremap <silent> <C-Q> :qa<CR>
inoremap <silent> <C-Q> <ESC>:qa<CR>

" pause in insert mode: -------------------------
inoremap <silent> <C-Z> <ESC><C-Z>

" normal things in insert mode: -----------------
"inoremap <silent> <ESC>b <C-O>b
"inoremap <silent> <ESC>w <C-O>w
inoremap <silent> <ESC>p <C-O>p
inoremap <silent> <ESC>P <C-O>P

" control-backspace to delete word: -------------
"imap     <silent> <C-BS> <C-W>
"imap     <silent> <C-H> <C-W>
"imap     <silent> <C-Del> <C-O>diw
"inoremap     <silent> <M-[>3;5~ <C-O>diw

" Use <C-L> to clear the highlighting of :set hlsearch.
" if maparg('<C-L>', 'n') ==# ''
"   nnoremap <silent> <C-L> :nohlsearch<C-R>=has('diff')?'<Bar>diffupdate':''<CR><CR><C-L>
" endif


" text wrapping: --------------------------------
if exists('+linebreak')
    set nowrap
    augroup WrappingOptionsGroup
        autocmd!
        autocmd FileType markdown,text call SetWrappingOptions()
    augroup END
    function! SetWrappingOptions()
        setlocal wrap
        noremap <silent><buffer> <UP>   g<UP>
        noremap <silent><buffer> <DOWN> g<DOWN>
       inoremap <silent><buffer> <UP>   <C-O>g<UP>
       inoremap <silent><buffer> <DOWN> <C-O>g<DOWN>
        " noremap <silent><buffer> k      gk
        " noremap <silent><buffer> j      gj
    endfunction
    set linebreak
    set showbreak=>\ "↪↳\
    if exists('+breakindent')
        set breakindent
        set breakindentopt=shift:2
    endif
endif
