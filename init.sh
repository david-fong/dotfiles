cp ~/.config/bash/profile ~

mkdir -p ~/c
mkdir -p ~/c/m

# https://superuser.com/a/215506
mkdir -p -m700 ~/.ssh
[ -f ~/.ssh/config ] || echo 'AddKeysToAgent=yes' > ~/.ssh/config
chmod 600 ~/.ssh/*
chmod 644 ~/.ssh/*.pub
