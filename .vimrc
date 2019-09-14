
set tabstop=4
set shiftwidth=4
set expandtab

"<save> *do 'type vim' to view the overriding function.
noremap  <silent> <C-S>      :update<CR>
vnoremap <silent> <C-S> <C-C>:update<CR>gv
inoremap <silent> <C-S> <C-O>:update<CR>

"<exit>
noremap  <silent> <C-X>      :q<CR>
vnoremap <silent> <C-X>      :q<CR>
inoremap <silent> <C-X> <ESC>:q<CR>

set nu
set rnu
if exists('+breakindent')
    set breakindent
endif
let &showbreak = '↳ '
set mouse=a

"no seizures, please T^T
set vb t_vb=

if &diff
    map ] ]c
    map [ [c
endif

