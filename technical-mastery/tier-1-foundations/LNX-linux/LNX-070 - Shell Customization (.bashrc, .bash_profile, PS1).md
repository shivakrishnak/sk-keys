---
id: LNX-070
title: "Shell Customization (.bashrc, .bash_profile, PS1)"
category: Linux
tier: tier-1-foundations
folder: LNX-linux
difficulty: ★★☆
depends_on: LNX-004, LNX-066
used_by: LNX-099
related: LNX-004, LNX-066, LNX-003
tags: [bashrc, bash_profile, PS1, PROMPT_COMMAND, aliases, PATH, shell-customization, environment, direnv, nvm]
status: complete
version: 4
layout: default
parent: "Linux"
grand_parent: "Technical Mastery"
nav_order: 70
permalink: /technical-mastery/lnx/shell-customization/
---

## TL;DR

`.bash_profile` loads once at **login** (SSH, console): set PATH, environment
variables. `.bashrc` loads for each **interactive non-login shell** (terminal
emulators): aliases, functions, prompt. Canonical pattern: `.bash_profile`
sources `.bashrc`. `PS1` customizes the prompt (colors, git branch, user,
host, path). `PROMPT_COMMAND` runs before each prompt (dynamic updates).
`export` makes variables available to child processes. `alias ll='ls -la'`.
`$HOME/.local/bin` for user-local scripts. Common tools: `direnv` (per-
directory env vars), `nvm`/`rbenv` (language version managers).

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | LNX-070 |
| **Difficulty** | ★★☆ Intermediate |
| **Category** | Linux |
| **Tags** | bashrc, bash_profile, PS1, PROMPT_COMMAND, aliases, PATH, shell customization, direnv |
| **Prerequisites** | LNX-004 (Shell basics), LNX-066 (Bash advanced) |

---

### The Problem This Solves

**Problem 1**: A developer sets up `alias k='kubectl'` in their terminal
and uses it all day. They SSH into a remote server and the alias is gone.
Understanding when `.bashrc` vs `.bash_profile` loads explains why aliases
need to be in `.bashrc` (which loads for interactive shells), and why
`.bash_profile` must source `.bashrc` so that login shell sessions (SSH)
also get the aliases.

**Problem 2**: A teammate's PATH includes personal Python environments that
conflict with system tools. Understanding `export`, PATH ordering, and
`direnv` for project-specific environments prevents "works on my machine"
issues and environment pollution between projects.

---

### Textbook Definition

**Shell startup files**: Scripts that bash executes automatically when
starting. Which file loads depends on how bash is invoked:

| Shell type | Reads |
|-----------|-------|
| Login shell (SSH, console `bash --login`) | `/etc/profile`, then first found: `~/.bash_profile`, `~/.bash_login`, or `~/.profile` |
| Interactive non-login (terminal emulator) | `~/.bashrc` |
| Non-interactive (scripts, cron) | Neither (except `$BASH_ENV`) |

**PS1 (Prompt String 1)**: The primary prompt string. Displayed before each
command. Special escapes: `\u` (user), `\h` (hostname), `\w` (working dir),
`\$` (`$` for normal user, `#` for root), `\n` (newline).

**`export`**: Makes a variable visible to child processes (processes launched
from this shell). Variables without `export` are local to the current shell.

**`source` / `.`**: Execute a file in the CURRENT shell (not a subshell).
Changes to variables, functions, and cd commands persist after sourcing.

---

### Understand It in 30 Seconds

```bash
# === Where to put what ===
# ~/.bash_profile: one-time login environment setup
cat >> ~/.bash_profile << 'EOF'
# Load .bashrc (so SSH sessions also get aliases/functions):
[[ -f ~/.bashrc ]] && source ~/.bashrc

# One-time environment variables (persist to all child processes):
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export EDITOR=vim
export PAGER=less
EOF

# ~/.bashrc: interactive shell setup (loaded every new terminal)
cat >> ~/.bashrc << 'EOF'
# === Aliases ===
alias ll='ls -la --color=auto'
alias la='ls -A'
alias l='ls -CF'
alias grep='grep --color=auto'
alias k='kubectl'
alias dk='docker'
alias tf='terraform'
alias ..='cd ..'
alias ...='cd ../..'

# === Environment ===
# User-local binaries (no sudo needed):
export PATH="$HOME/.local/bin:$PATH"
# Node/npm global without sudo:
export PATH="$HOME/.npm-global/bin:$PATH"
# Go binaries:
export GOPATH="$HOME/go"
export PATH="$GOPATH/bin:$PATH"

# === History settings ===
HISTSIZE=10000
HISTFILESIZE=20000
HISTCONTROL=ignoredups:erasedups   # no duplicates in history
shopt -s histappend                # append to history, don't overwrite
# Save and reload history before each prompt:
PROMPT_COMMAND="history -a; history -c; history -r; $PROMPT_COMMAND"

# === Functions ===
# mkcd: make directory and cd into it:
mkcd() { mkdir -p "$1" && cd "$1"; }
# extract: universal archive extractor:
extract() {
    case "$1" in
        *.tar.bz2) tar xjf "$1" ;;
        *.tar.gz)  tar xzf "$1" ;;
        *.tar.xz)  tar xJf "$1" ;;
        *.zip)     unzip "$1" ;;
        *.gz)      gunzip "$1" ;;
        *)         echo "Unknown archive format: $1" ;;
    esac
}
EOF

# === PS1: Prompt customization ===
# Colors: \[\e[color_codemi]\] (start), \[\e[0m\] (reset)
# Color codes: 30-37 (standard), 1;30-1;37 (bold), 32m=green, 34m=blue, etc.

# Simple colored prompt: [user@host dir]$
PS1='\[\e[1;32m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ '
# Renders as: user@hostname:/current/path$

# Professional prompt with git branch and exit code:
parse_git_branch() {
    git branch 2>/dev/null | sed -n 's/* \(.*\)/(\1)/p'
}
set_ps1() {
    local exit_code=$?
    local green='\[\e[1;32m\]'
    local blue='\[\e[1;34m\]'
    local yellow='\[\e[1;33m\]'
    local red='\[\e[0;31m\]'
    local reset='\[\e[0m\]'
    
    local status_color=$green
    [[ $exit_code -ne 0 ]] && status_color=$red   # red on error
    
    local git_branch
    git_branch=$(parse_git_branch)
    
    PS1="${green}\u@\h${reset}:${blue}\w${reset} ${yellow}${git_branch}${reset}${status_color}\$${reset} "
}
PROMPT_COMMAND="set_ps1; ${PROMPT_COMMAND:-}"
# Note: PROMPT_COMMAND runs before each prompt is displayed

# === PROMPT_COMMAND: run before each prompt ===
# Update terminal title to current directory:
PROMPT_COMMAND='echo -ne "\033]0;${USER}@${HOSTNAME}: ${PWD}\007"; '

# === source: load files in current shell ===
source ~/.bashrc          # reload .bashrc after editing
. ~/.bashrc               # same thing (POSIX compatible)
source /etc/profile.d/nvm.sh  # load nvm into current shell

# === direnv: per-directory environments ===
# Install: sudo apt install direnv
# Add to .bashrc:
eval "$(direnv hook bash)"

# Per-project: create .envrc in project directory:
# echo 'export DATABASE_URL=postgresql://localhost/myapp_dev' > .envrc
# direnv allow .     <- approve the .envrc file (security)
# cd project/ -> env vars automatically set
# cd .. -> env vars automatically unset
```

---

### First Principles

**Login shell vs interactive shell - when each file loads:**
```
Scenario 1: SSH into a server
  ssh user@server
  -> bash starts as: LOGIN + INTERACTIVE shell
  -> Reads: /etc/profile -> ~/.bash_profile (or .bash_login or .profile)
  -> Does NOT automatically read ~/.bashrc
  -> That's why ~/.bash_profile must contain: [[ -f ~/.bashrc ]] && source ~/.bashrc
  -> After sourcing: both login (PATH, JAVA_HOME) and interactive (.aliases, .functions) setup complete

Scenario 2: Open terminal emulator (gnome-terminal, iTerm)
  -> bash starts as: INTERACTIVE, NON-LOGIN shell
  -> Reads: ~/.bashrc only
  -> Does NOT read ~/.bash_profile
  -> Aliases defined in .bashrc: AVAILABLE
  -> Variables only in .bash_profile: NOT available!
  
  This is why duplicating PATH settings in both files is a common mistake:
  Set PATH in .bash_profile AND have .bash_profile source .bashrc
  OR: set PATH in .bashrc and have .bash_profile source .bashrc
  The canonical approach: .bash_profile is a thin file that sources .bashrc

Scenario 3: Run a script: ./myscript.sh
  -> bash starts as: NON-INTERACTIVE, NON-LOGIN shell
  -> Reads: NEITHER .bashrc NOR .bash_profile
  -> Aliases defined interactively: NOT available
  -> This is a common surprise: alias 'll' defined in .bashrc = works in terminal,
     FAILS in a script (aliases are not inherited)
  -> Scripts must use full commands (ls -la, not ll)

Scenario 4: bash -c "command"
  -> Non-interactive, non-login
  -> Same as scripts: no .bashrc or .bash_profile loaded

Scenario 5: su - username (login shell switch):
  -> login shell for new user
  -> Reads new user's .bash_profile
  
Scenario 6: su username (without dash):
  -> Interactive, non-login shell for new user
  -> Reads new user's .bashrc

Test which type you have:
  [[ -o login ]] && echo "login shell" || echo "non-login shell"
  [[ -o interactive ]] && echo "interactive" || echo "non-interactive"
```

**export: variable scope:**
```bash
# Without export: variable is local to current shell
VAR=hello
bash -c 'echo $VAR'    # empty! child process doesn't see it

# With export: variable is inherited by child processes
export VAR=hello
bash -c 'echo $VAR'    # hello

# Check: env | grep VAR   (shows exported variables only)
# Check: set | grep VAR   (shows all shell variables including non-exported)

# PATH inheritance:
# PATH is exported by default in login shells (/etc/profile exports it)
# Modifications: must preserve existing value:
export PATH="$HOME/.local/bin:$PATH"   # GOOD: prepend (takes priority)
PATH="$HOME/.local/bin:$PATH"          # Also OK: PATH is already exported
PATH="/new/path"                        # BAD: overwrites all system paths!

# Order matters in PATH:
# First match wins: "which python" returns first python in PATH
export PATH="/home/dev/.pyenv/shims:$PATH"   # pyenv python takes priority
```

---

### Thought Experiment

Setting up a developer environment from scratch:

```bash
#!/bin/bash
# setup-dev-env.sh: Configure a development shell environment

echo "=== Setting up developer shell environment ==="

# Backup existing files:
for f in ~/.bashrc ~/.bash_profile ~/.gitconfig; do
    [[ -f "$f" ]] && cp "$f" "$f.backup.$(date +%Y%m%d)"
done

# Create ~/.bash_profile (login shell - thin, sources .bashrc):
cat > ~/.bash_profile << 'BASH_PROFILE'
# ~/.bash_profile: Login shell startup
# Source .bashrc for interactive setup (aliases, functions, prompt):
[[ -f ~/.bashrc ]] && source ~/.bashrc
# Login-only settings:
umask 022
BASH_PROFILE

# Create ~/.bashrc (interactive shell - all the good stuff):
cat > ~/.bashrc << 'BASHRC'
# ~/.bashrc: Interactive shell startup
# Don't run for non-interactive shells:
[[ $- != *i* ]] && return

# === PATH ===
export PATH="$HOME/.local/bin:$HOME/bin:$PATH"

# === Editor/Pager ===
export EDITOR=vim
export VISUAL=vim
export PAGER=less
export LESS='-R --quit-if-one-screen --ignore-case'

# === Aliases ===
alias ll='ls -la --color=auto'
alias grep='grep --color=auto'
alias k='kubectl'
alias tf='terraform'
alias ..='cd ..'
alias ...='cd ../..'
alias ports='ss -tuln'     # show listening ports
alias myip='curl -s ifconfig.me'

# === Functions ===
mkcd() { mkdir -p "$1" && cd "$1"; }
up() { cd $(python3 -c "import os; print(os.path.abspath('$(printf "%${1:-1}s" | tr " " "/")'))"); }

# === History ===
HISTSIZE=50000
HISTFILESIZE=100000
HISTCONTROL=ignoredups:erasedups
shopt -s histappend
shopt -s cmdhist  # save multi-line commands as one history entry

# === Prompt ===
# Simple, readable: [user@host dir (git-branch)]$
parse_git_branch() {
    git branch 2>/dev/null | sed -n 's/* \(.*\)/ (\1)/p'
}
set_prompt() {
    local code=$?
    local green='\[\e[0;32m\]'
    local yellow='\[\e[0;33m\]'
    local reset='\[\e[0m\]'
    local mark_color=$([[ $code -eq 0 ]] && echo "$green" || echo '\[\e[0;31m\]')
    PS1="${green}\u@\h${reset}:${yellow}\w${green}$(parse_git_branch)${reset}${mark_color}\$${reset} "
}
PROMPT_COMMAND="set_prompt"

# === Tools (if installed) ===
# direnv (per-directory environments):
command -v direnv &>/dev/null && eval "$(direnv hook bash)"
# nvm (Node version manager):
[[ -s "$HOME/.nvm/nvm.sh" ]] && source "$HOME/.nvm/nvm.sh"
# pyenv (Python version manager):
[[ -d "$HOME/.pyenv" ]] && {
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
}
BASHRC

echo "Setup complete. Run: source ~/.bashrc"
```

---

### Mental Model / Analogy

```
Shell startup files = getting dressed in the morning

.bash_profile = putting on your work clothes (happens once at login)
  Done when you first arrive at the office (SSH/console login)
  Sets your fundamental identity for the day:
    JAVA_HOME = which tools you carry
    PATH = which tool shops you can access
    
  This only happens ONCE per login session

.bashrc = personal desk setup (happens each time you open a terminal window)
  Every time you open a new terminal = new workspace
  Sets up your working preferences:
    aliases = keyboard shortcuts on your desk
    functions = custom tools in your desk drawer
    PS1 = how your nameplate looks
    
  Happens every time you start a new shell

Why .bash_profile should source .bashrc:
  When you SSH in (login shell), you want BOTH:
    - Your clothes (.bash_profile: PATH, JAVA_HOME)
    - Your desk setup (.bashrc: aliases, prompt, functions)
  Without .bash_profile sourcing .bashrc:
    SSH sessions = work clothes (PATH set) but no desk setup (no aliases)
    Terminal sessions = desk setup (aliases) but no work clothes (PATH from .bash_profile missing)

export = megaphone for variables:
  VAR=value: only YOU can hear it (current shell only)
  export VAR=value: broadcast to everyone in the room (child processes)
  
  PATH without export: child processes don't know about your directories
  PATH with export (already done by /etc/profile): child processes inherit it
  
direnv = automatic context switching:
  cd project-a/ -> automatically puts on Project A hat (env vars loaded)
  cd project-b/ -> takes off Project A hat, puts on Project B hat
  cd ~          -> no hat (clean environment)
```

---

### Gradual Depth - Five Levels

**Level 1:**
Login vs non-login shell and which file loads when. `.bash_profile` sources
`.bashrc`. `alias` for shortcuts. `export` for environment variables. Basic
`PS1` with `\u`, `\h`, `\w`. `PATH` ordering.

**Level 2:**
`PROMPT_COMMAND` for dynamic prompts (git branch, last exit code, timer).
`HISTSIZE`/`HISTFILESIZE`/`HISTCONTROL`. `shopt -s histappend`. `shopt`
options: `cdspell`, `globstar`, `extglob`. `direnv` for per-project envs.
`~/.local/bin` for user binaries. `nvm`/`pyenv`/`rbenv` PATH initialization.

**Level 3:**
PS1 ANSI color codes and escape sequences. `tput` for terminal-independent
colors (`tput setaf 2` for green). Dynamic PS1: show virtualenv, k8s context,
AWS profile. `bind` for keyboard shortcuts. `complete` for custom tab completion.
`shopt -s autocd`. `~/.inputrc` for readline configuration.

**Level 4:**
`BASH_ENV` for non-interactive scripts. `~/.profile` vs `.bash_profile` for
POSIX sh compatibility (macOS uses `.zshrc`/`.zprofile`). Cross-shell portability:
zsh (`.zshrc`, `.zprofile`), fish (config.fish). `starship` prompt (cross-shell,
written in Rust). Per-machine vs per-user configurations: `/etc/profile.d/` for
system-wide additions. Dotfile management: `chezmoi`, `stow`, git bare repo.

**Level 5:**
Shell startup performance: measure with `time bash -i -c exit`. Heavy
PROMPT_COMMAND (git status check on slow filesystems) = perceptible latency
per prompt. Async prompt updates (update after keypress, not before). `bash-preexec`
for pre-execution hooks. Secure dotfiles: never store secrets in `.bashrc`
(use `~/.env.local` with restricted permissions, sourced from `.bashrc`).
Container environments: dotfiles in Docker base images, Kubernetes devcontainer.

---

### Code Example

**BAD - common .bashrc/.bash_profile mistakes:**
```bash
# BAD 1: Setting everything in .bash_profile, not sourcing .bashrc:
# ~/.bash_profile:
export JAVA_HOME=/usr/lib/jvm/java-17
alias ll='ls -la'    # BAD LOCATION!
PS1='\u@\h:\w\$ '    # BAD LOCATION!

# Result: SSH logins get aliases. Terminal emulators: NO ALIASES
# (terminal opens non-login shell -> reads .bashrc -> no aliases there)

# GOOD: Split correctly:
# ~/.bash_profile:
export JAVA_HOME=/usr/lib/jvm/java-17    # env var: in .bash_profile OK
[[ -f ~/.bashrc ]] && source ~/.bashrc   # load aliases from .bashrc

# ~/.bashrc:
alias ll='ls -la'    # CORRECT LOCATION
PS1='\u@\h:\w\$ '    # CORRECT LOCATION

# BAD 2: Running code that has side effects in .bashrc:
# ~/.bashrc:
clear             # clears screen every time a terminal opens
ls               # lists current dir in every new terminal
ssh-add ~/.ssh/id_rsa  # BAD: may prompt for password every terminal start

# GOOD: .bashrc should only set up functions/aliases/vars, not execute commands
# If you want to run a startup command: put it in ~/.bash_profile behind a check:
if [[ -z "$SSH_AUTH_SOCK" ]]; then
    eval "$(ssh-agent -s)"
    ssh-add ~/.ssh/id_rsa 2>/dev/null
fi

# BAD 3: Storing secrets in .bashrc:
# ~/.bashrc:
export AWS_SECRET_ACCESS_KEY="AKIA_YOUR_KEY_EXAMPLE/..."  # NEVER DO THIS!
export DB_PASSWORD="mysecret123"  # NEVER DO THIS!
# .bashrc goes into git dotfiles repo = secret exposed!

# GOOD: Use a separate, not-in-git file:
# ~/.bashrc:
[[ -f ~/.env.local ]] && source ~/.env.local
# ~/.env.local (chmod 600, not in git):
export AWS_SECRET_ACCESS_KEY="actual-secret"
```

**GOOD - minimal, well-structured .bashrc:**
```bash
# ~/.bashrc - interactive shell setup

# Guard: don't run for non-interactive shells
[[ $- != *i* ]] && return

# === Core PATH ===
export PATH="$HOME/.local/bin:$PATH"

# === Essentials ===
export EDITOR=vim
alias ll='ls -la --color=auto'
alias grep='grep --color=auto'

# === History ===
HISTSIZE=10000
HISTCONTROL=ignoredups:erasedups
shopt -s histappend

# === Prompt: show git branch, red $ on error ===
__ps1_git() { git branch 2>/dev/null | sed -n 's/* \(.*\)/ (\1)/p'; }
PROMPT_COMMAND='PS1="\[\e[0;32m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0;33m\]$(__ps1_git)\[\e[0m\]\$([[ $? -eq 0 ]] && echo \"\\[\e[0;32m\]\" || echo \"\\[\e[0;31m\]\")\\$\[\e[0m\] "'
# Note: the above is complex; for production: pre-compute in a function

# === Load local overrides (secrets, machine-specific) ===
[[ -f ~/.env.local ]] && source ~/.env.local

# === Tool initialization ===
command -v direnv &>/dev/null && eval "$(direnv hook bash)"
```

---

### Common Misconceptions

| Misconception | Reality |
|--------------|---------|
| "`.bash_profile` and `.bashrc` are both loaded at startup" | They are loaded in DIFFERENT scenarios. `.bash_profile` (or `.profile`): login shells only (SSH, `bash --login`, console login). `.bashrc`: interactive non-login shells only (terminal emulators, `bash` without `--login`). Neither is loaded for non-interactive scripts. The confusion is so common that the canonical pattern is: put everything in `.bashrc` and have `.bash_profile` source `.bashrc`. macOS Terminal prior to Catalina opened login shells by default (so `.bash_profile` was the main config), while Linux terminal emulators open non-login shells (so `.bashrc` is the main config). This is a source of many "works on Mac, not on Linux" issues. |
| "`source script.sh` is the same as `bash script.sh`" | `bash script.sh` runs in a SUBSHELL - a new bash process. Any variable assignments, cd commands, or function definitions in the script exist only in that subshell and disappear when it exits. `source script.sh` (or `. script.sh`) runs the script in the CURRENT shell - all changes persist. This is why: `source ~/.bashrc` reloads your configuration (changes persist), while `bash ~/.bashrc` does nothing useful (changes disappear). For scripts that set environment variables: they MUST be sourced to have effect. For scripts that just run commands: either works, but subshell is safer (won't pollute the current environment). |
| "aliases are available in shell scripts" | Aliases are shell builtin features, not environment variables, and they're NOT exported to child processes. A script run with `bash myscript.sh` is a NEW bash process that does NOT read `.bashrc` (non-interactive scripts don't read startup files), so aliases are not available. This is a common issue: developer has `alias python=python3` in `.bashrc`, but scripts using `python` fail because the script sees the original `python` (or nothing if Python 2 is gone). Fix: use the full command (`python3`) in scripts, not aliases. Or use `#!/usr/bin/env python3` shebang. |
| "All environment variables in `.bashrc` are available system-wide" | Environment variables set in `.bashrc` are available ONLY to the current bash session and its child processes. They are NOT: system-wide (other users don't see them), persistent across reboots without re-reading `.bashrc`, or available to GUI applications launched from a desktop manager (which doesn't read `.bashrc`). System-wide variables go in `/etc/environment` (not a script, key=value format) or `/etc/profile.d/*.sh`. GUI application environment (for apps launched from taskbar, not terminal): `/etc/environment` or `~/.pam_environment`. systemd services get environment from `Environment=` in unit files, not from `.bashrc`. |
| "PROMPT_COMMAND should only contain one command" | `PROMPT_COMMAND` can contain multiple statements (semicolons or newlines). It's evaluated as a shell statement before each primary prompt. Best practice: accumulate commands: `PROMPT_COMMAND="cmd1; ${PROMPT_COMMAND:-}"` - append to existing value, don't overwrite. If you just assign `PROMPT_COMMAND=newcmd`, you lose any previous PROMPT_COMMAND (which tools like `history -a` or terminal multiplexers may have set). The pattern `${PROMPT_COMMAND:-}` (use existing value or empty string) prevents errors from an empty initial value. PROMPT_COMMAND runs in the current shell, so it CAN modify PS1, which is why the pattern `PROMPT_COMMAND="set_ps1"` (calling a function that sets PS1) is common for complex prompts. |

---

### Failure Modes & Diagnosis

**Environment not loading:**
```bash
# Symptom: alias 'll' works in terminal, but not in SSH session

# Diagnosis 1: check which shell type you have:
ssh user@server 'echo "Login: $([[ -o login ]] && echo yes || echo no)"'
ssh user@server 'echo "Interactive: $([[ -o interactive ]] && echo yes || echo no)"'
# Shows: Login: yes, Interactive: yes (login + interactive)

# Diagnosis 2: Check if .bash_profile sources .bashrc:
ssh user@server 'cat ~/.bash_profile'
# Should contain: [[ -f ~/.bashrc ]] && source ~/.bashrc

# Fix: add sourcing to .bash_profile:
ssh user@server 'echo "[[ -f ~/.bashrc ]] && source ~/.bashrc" >> ~/.bash_profile'

# Symptom: 'k' alias (for kubectl) works after 'source ~/.bashrc'
# but not in a new terminal

# Check: is the alias in .bashrc?
grep "alias k=" ~/.bashrc ~/.bash_profile 2>/dev/null
# If only in .bash_profile: move to .bashrc

# Check: is .bashrc being read?
# Add to .bashrc: echo "Loading .bashrc" (temporarily)
# Open new terminal: if you see "Loading .bashrc", it's being read

# Symptom: changes to PATH in .bashrc don't take effect for cron jobs

# Cron doesn't read .bashrc! Cron jobs get a minimal environment.
# Fix: set PATH explicitly in the cron script:
crontab -e
# 0 * * * * PATH=/usr/local/bin:/usr/bin:/bin /path/to/script.sh
# Or source the environment at the top of the script:
# source /etc/profile
# source ~/.bashrc 2>/dev/null || true
```

---

### Related Keywords

**Foundational:**
LNX-004 (Shell basics), LNX-066 (Bash advanced)

**Builds on this:**
LNX-099 (Fleet management - configuration at scale)

**Related:**
LNX-003 (Terminal basics), LNX-004 (Basic shell)

---

### Quick Reference Card

| File | Loads when |
|------|-----------|
| `~/.bash_profile` | Login shell (SSH, console) |
| `~/.bashrc` | Interactive non-login shell (terminal emulator) |
| `/etc/profile` | System-wide login shell |
| `/etc/profile.d/*.sh` | System-wide modular additions |
| `~/.bash_logout` | When login shell exits |

| Concept | Example |
|---------|---------|
| Export variable | `export VAR=value` |
| Prepend to PATH | `export PATH="$HOME/.local/bin:$PATH"` |
| Alias | `alias ll='ls -la'` |
| Source file | `source ~/.bashrc` or `. ~/.bashrc` |
| Dynamic prompt | `PROMPT_COMMAND="update_ps1"` |

**3 things to remember:**
1. `.bash_profile` = login shells (SSH); `.bashrc` = interactive non-login (terminals). Have `.bash_profile` source `.bashrc` to unify
2. Aliases and functions are NOT inherited by child processes or scripts - always use full commands in scripts
3. Never store secrets in `.bashrc` - use `~/.env.local` (chmod 600, not in git), sourced from `.bashrc`

---

### Transferable Wisdom

Shell startup file concepts appear in: Docker `ENV` instructions set
environment variables in container images (available to all processes in
that container, like exported vars). Kubernetes Pod `env:` and `envFrom:`
directives: same "environment inheritance" pattern. Python virtual environments
(`source .venv/bin/activate`): modifies PATH and prompt, like `.bashrc`.
`direnv` (per-directory environment) = the shell equivalent of Kubernetes
ConfigMaps or Helm values: context-specific configuration. GitHub Actions
`$GITHUB_ENV`: write to this file to set env vars for subsequent steps
(same concept: exported variables persist to child processes). The `export`
concept (make a variable available to child processes) maps directly to:
Java System properties (`-D` flags), Docker `--env` flags, Kubernetes
environment injection. Understanding shell startup order helps debug any
"environment variable not found" issue across ALL contexts (shells, CI,
containers, cron).

---

### The Surprising Truth

The `.bash_profile` vs `.bashrc` split was designed for a technical reason
that has largely become irrelevant: in the 1980s and 1990s, "login shells"
ran on remote terminals or consoles and needed to set up the environment
carefully (PATH, umask, ulimits) because the environment came from scratch.
"Interactive shells" were child shells started from within an existing session
and inherited their environment. Running all the setup code AGAIN in each
interactive shell was wasteful and could cause issues. Today, most users
have ONE terminal application per session, and the distinction creates only
confusion. Modern shells addressed this: zsh uses `.zprofile` (login) and
`.zshrc` (interactive), with the convention that you put everything in
`.zshrc` and it works. Fish shell has a single `config.fish`. The bash
community's canonical workaround (put everything in `.bashrc`, have
`.bash_profile` source it) is essentially treating the design as irrelevant
and unifying the two. The deeper lesson: "correct" historical design can
become "accidental complexity" as the use cases it was designed for
disappear. The two-file split made sense when terminal sessions were
expensive resources to set up. For a developer opening 5 terminal windows
on a modern laptop, it's just confusion.

---

### Mastery Checklist

- [ ] Understands when .bash_profile vs .bashrc is loaded
- [ ] Can configure .bash_profile to source .bashrc correctly
- [ ] Can write a useful PS1 with colors and PROMPT_COMMAND
- [ ] Knows the difference between aliased shortcuts and script-safe commands
- [ ] Can use export and PATH ordering for user-local binaries

---

### Think About This

1. A teammate reports that the `k` alias (for `kubectl`) works fine in
   their terminal but disappears when they SSH into a server. Diagnose
   the exact cause (using the login vs non-login shell model) and explain
   the complete fix in terms of which file should contain the alias and
   what change the .bash_profile needs.

2. A CI/CD pipeline script fails because `python` isn't found (the developer
   set `alias python=python3` in `.bashrc`). Explain why the alias doesn't
   work in the CI script, the correct fix (shebang line), and why you should
   NEVER rely on aliases in shell scripts.

3. Your team is building a developer machine setup script that needs to:
   (a) add `$HOME/.local/bin` to PATH, (b) set `JAVA_HOME`, (c) set up
   an alias for kubectl, (d) configure the git-branch-showing prompt. For
   each item, decide whether it belongs in `.bash_profile` or `.bashrc`
   and explain why. Then write the 2-3 lines needed in `.bash_profile`
   to ensure these settings work for BOTH SSH sessions and terminal emulators.

---

### Interview Deep-Dive

**Foundational:**
Q: What is the difference between `.bashrc` and `.bash_profile`, and when is each loaded?
A: They serve different purposes based on when bash starts: `.bash_profile` (or `.bash_login` or `.profile`): loaded by LOGIN shells - when you SSH into a machine, open a console, or run `bash --login`. A login shell is the first shell of a user session that "logs you in." It sets up the fundamental environment: PATH from `/etc/profile`, `JAVA_HOME`, `EDITOR`, `umask`, etc. Loaded ONCE per login session. `.bashrc`: loaded by INTERACTIVE NON-LOGIN shells - every time you open a new terminal window or tab in a graphical environment (gnome-terminal, iTerm, etc.). Also for `bash` started by running `bash` from another shell. Loaded for EACH new terminal. Contains: aliases, functions, prompt configuration, history settings. The common confusion: in macOS Terminal (until Catalina), each terminal window opened a LOGIN shell, so `.bash_profile` was the config file. In Linux desktop environments (GNOME, KDE), terminal emulators open INTERACTIVE NON-LOGIN shells, so `.bashrc` is the config file. SSH always creates a LOGIN shell. Canonical solution: put ALL configuration in `.bashrc`. Add to `.bash_profile`: `[[ -f ~/.bashrc ]] && source ~/.bashrc`. This ensures SSH sessions (login shells) also get all your aliases and functions from `.bashrc`. PRACTICAL RULE: unless you have a specific reason to separate "login-time" from "interactive-time" setup, put everything in `.bashrc` and have `.bash_profile` just source it.

**Expert:**
Q: How would you set up project-specific environment variables that don't leak between projects?
A: The canonical tool for per-project environment management is `direnv`. How it works: (1) Install: `apt install direnv` or `brew install direnv`. (2) Hook into bash: add `eval "$(direnv hook bash)"` to `~/.bashrc`. (3) Per project: create `.envrc` in the project root: `export DATABASE_URL="postgresql://localhost/myproject_dev"`, `export AWS_PROFILE=my-project-staging`. (4) Approve: run `direnv allow .` in the project directory (security - prevents auto-executing random .envrc files). (5) Usage: `cd ~/projects/myproject` -> direnv automatically loads `.envrc`. `cd ~/projects/other` -> direnv unloads myproject's vars, loads other's. `cd ~` -> all project vars unloaded. Key features: no manual `source` needed. Variables are unset when you leave the directory. `.envrc` can be in git (without secrets) - secrets via `~/.envrc` (global) or by sourcing from `.envrc`: `source_env .env.local` (direnv extension, reads a non-committed file). Alternative without direnv: shell functions: `function activate-project() { export DB_URL=...; }` called manually. OR: per-project activate scripts: `source ./env.sh`. direnv's advantage: automatic and reversible. The anti-patterns to avoid: setting project-specific vars in `~/.bashrc` directly (they leak to all projects), using the same AWS_PROFILE for all projects (accidental prod access from dev context), storing secrets in `.envrc` committed to git.
