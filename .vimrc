
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
    set showbreak=>>
    set breakindent
    set breakindentopt=shift:2
    noremap <UP> g<UP>
    noremap <DOWN> g<DOWN>
endif



" whitespace indicators: ------------------------
set listchars=tab:▸\ ,trail:·
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

