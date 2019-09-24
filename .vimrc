
set encoding=utf-8
scriptencoding utf-8

set autoindent
set tabstop=4
set shiftwidth=4
set expandtab

set formatoptions=tcroqlj
set vb t_vb=
set mouse=a



" save using ctrl+s: ----------------------------
noremap  <silent> <C-S> :update<CR>
vnoremap <silent> <C-S> <C-C>:update<CR>gv
inoremap <silent> <C-S> <C-O>:update<CR>



" exit using ctrl+x: ----------------------------
noremap  <silent> <C-X> :q<CR>
vnoremap <silent> <C-X> :q<CR>
inoremap <silent> <C-X> <ESC>:q<CR>



" line numbers: ---------------------------------
set foldcolumn=1
set numberwidth=1
set number
hi FoldColumn ctermbg=none
hi LineNr ctermfg=gray



"text wrapping: ---------------------------------
if exists('+linebreak')
    set linebreak
    set showbreak=>>>\ "
    if exists('+breakindent')
        set breakindent
        set breakindentopt=shift:2
    endif
    noremap <UP> g<UP>
    noremap <DOWN> g<DOWN>
endif



" whitespace indicators: ------------------------
if has("patch-7.4.710")
    set listchars=tab:▸\ ,trail:·
else
    set listchars=tab:>\ ,trail:-
endif
set list



" statusline ------------------------------------
set statusline=\ [%f]%h%m%r%y[%{&ff}]
set statusline+=%=%l,%c%V\ %P\ "
set laststatus=2
hi StatusLineNC ctermfg=grey
hi StatusLineNC ctermbg=darkgrey



if &diff
    map ] ]c
    map [ [c
endif



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

