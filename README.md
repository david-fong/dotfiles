
# David's Dotfiles

This is a collection of configuration files made for a Git For Windows + MinTTY environment.

```sh
# If you don't have XDG environment variables set up, you can do this:
# echo 'declare -rx XDG_CONFIG_HOME="$(cygpath "${XDG_CONFIG_HOME:-"${HOME}/.config"}")"' >> "$HOME/.bash_profile"
# echo 'declare -rx XDG_CACHE_HOME="$(cygpath "${XDG_CACHE_HOME:-"${HOME}/.cache"}")"' >> "$HOME/.bash_profile"
# echo 'declare -rx XDG_DATA_HOME="$(cygpath "${XDG_DATA_HOME:-"${HOME}/.local/share"}")"' >> "$HOME/.bash_profile"
# echo '[[ -f "${XDG_CONFIG_HOME}/bash/profile" ]] && source "${XDG_CONFIG_HOME}/bash/profile"' >> "$HOME/.bash_profile"

git clone https://github.com/david-fong/dotfiles.git "$XDG_CONFIG_HOME"
echo '[[ -f "${XDG_CONFIG_HOME}/bash/main.sh" ]] && source "${XDG_CONFIG_HOME}/bash/main.sh"' >> "$HOME/.bash_profile"

# If not done already, add `AddKeysToAgent=yes` to `~/.ssh/config` and `chmod 600 ~/.ssh/config`
```

