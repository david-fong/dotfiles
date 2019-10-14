
set encoding=utf-8
scriptencoding utf-8

"autocmd BufRead,BufNewFile *.c,*.h set cindent
"retab

set smartindent
set tabstop=4
set softtabstop=4 "use &tabstop
set shiftwidth=0  "use &tabstop
set shiftround    "round when shifting
set expandtab

set formatoptions=tcroqlj
set vb t_vb=
set mouse=a
set clipboard=unnamed

set title
set fillchars=vert:\ "
set wildmenu
set wildmode=list:longest,longest:full
set showcmd

if &diff
syntax off
endif


" try to start cursorline at top of screen ------
augroup VimrcGroup
    autocmd!
    autocmd BufRead,BufNewFile * call OnOpenFile()
augroup END
function! OnOpenFile()
    exe "normal zz0"
    if &readonly
        set nomodifiable
    endif
endfunction


" smoother scrolling: ---------------------------
set scrolloff=5
set sidescroll=1
set sidescrolloff=10
map  <silent> <ScrollWheelUp> <C-Y>
map  <silent> <ScrollWheelDown> <C-E>
imap <silent> <ScrollWheelUp> <C-O><C-Y>
imap <silent> <ScrollWheelDown> <C-O><C-E>


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


" pause in normal mode: -------------------------
inoremap <silent> <C-Z> <ESC><C-Z>


" line numbers: ---------------------------------
set foldcolumn=1
set numberwidth=1
set number
set cursorline "'show' the cursor line
hi FoldColumn   ctermbg=none
hi CursorLine   cterm=none
hi CursorLineNr ctermfg=white cterm=bold
hi LineNr       ctermfg=blue


" text wrapping: --------------------------------
if exists('+linebreak')
    set nowrap
    augroup WrappingOptionsGroup
        autocmd!
        autocmd FileType markdown,text call SetWrappingOptions()
    augroup END
    function! SetWrappingOptions()
        setlocal wrap
        noremap <silent><buffer> <UP> g<UP>
        noremap <silent><buffer> <DOWN> g<DOWN>
    endfunction
    set linebreak
    set showbreak=>\ "↪↳\ 
    if exists('+breakindent')
        set breakindent
        set breakindentopt=shift:2
    endif
endif


" whitespace indicators: ------------------------
set list
if has("patch-7.4.710")
    set listchars=tab:▸\ ,trail:·,extends:»,precedes:«
else
    set listchars=tab:\|\ ,trail:-
endif
"hi SpecialKey ctermfg=grey
set list


" statusline ------------------------------------
set statusline=\ [%f]%h%m%r%y[%{&ff}]
set statusline+=%=%l,%c%V\ %P\ "
set laststatus=2
hi StatusLineNC ctermfg=grey ctermbg=darkgrey


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



" for hex editing -------------------------------
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


" systemverilog module signal param list --------
function! VerilogParamFormat()
    sil! exe "0/^module /;/;$/substitute/(/(/"
    sil! exe "0/^module /;/;$/substitute/,\\s\\s*/,    /"
    sil! exe "0/^module /;/;$/substitute/,\\s\\s*/,    /"
    sil! exe "0/^module /;/;$/substitute/,\\s\\s*/,    /"
    sil! exe "0/^module /;/;$/substitute/,\\s\\s*/,    /"
    sil! exe "0/^module /+1;/;$/substitute/^\\s*/    /"
    sil! exe "0/^module /;/;$/+1substitute/);$/);/"
endfunction

