# **Rust CLI Essentials: A Practical Cheat Sheet**

These tools replace classic Unix commands with **faster, safer, more ergonomic** versions.

---

# **1. ripgrep — `rg` (modern grep)**

Blazing-fast recursive search with sane defaults.

### **Common usage**

```bash
rg "pattern"                          # search recursively
rg "pattern" path/to/dir              # search inside a specific directory
rg -i "pattern"                       # case-insensitive search
rg -w "word"                          # match whole word
rg -t py "def myfunc"                 # search only Python files
rg -g '*.md' "TODO"                   # glob file filter
rg -v "exclude_this"                  # invert match
```

### **Useful flags**

```bash
rg -n       # show line numbers
rg -l       # list matching file names only
rg -A 3     # show 3 lines after match
rg -B 3     # show 3 lines before match
rg -C 3     # show 3 lines of context
rg -p       # search hidden files + .gitignored files
```

---

# **2. fd — `fd` (friendly find)**

Simpler, faster alternative to `find`.

### **Basic usage**

```bash
fd pattern                           # find files matching pattern
fd pattern src/                      # limit to directory
fd -t f                              # only files
fd -t d                              # only directories
fd -e py                             # find files ending in .py
```

### **Real-world examples**

```bash
fd __pycache__ -x rm -rf {}          # remove all __pycache__ directories
fd "*.md" -x sed -i '' 's/foo/bar/g' {}   # edit all md files
```

---

# **3. bat — `bat` (modern cat + syntax highlight)**

Shows files with beautiful syntax highlighting and Git integration.

### **Usage**

```bash
bat file.py                          # pretty print with syntax
bat -n file.py                       # show line numbers
bat --plain file.py                  # no colors, no formatting
bat --diff                           # preview Git diff with highlighting
```

---

# **4. exa — `exa` or `eza` (modern ls)**

Drop-in replacement for `ls`, with colors, icons, Git info.

### **Common**

```bash
eza                                   # basic list
eza -l                                # long listing
eza -la                               # list all + long
eza -lh                               # human-readable sizes
eza -l --git                          # show Git metadata
eza -T                                # tree view
eza -T -L 2                           # tree depth 2
```

---

# **5. dust — `dust` (modern du)**

Visual disk usage analyzer.

### **Usage**

```bash
dust                                  # show sizes of directories
dust -d 1                             # depth 1
dust ~/Projects                       # specific directory
dust -n 10                            # top 10 largest
```

---

# **6. hyperfine — benchmarking tool**

Benchmark shell commands easily and correctly.

### **Example**

```bash
hyperfine "python script.py" "uv run python script.py"
hyperfine --warmup 3 "rg foo src/"
```

---

# **7. chose (`choose`) — field selector (modern cut)**

Not Rust originally, but often used with Rust tools. Very useful.

```bash
echo "a,b,c" | choose 1          # => a
echo "a,b,c" | choose 2          # => b
```

---

# **Installation (Mac)**

Using Homebrew:

```bash
brew install ripgrep fd bat eza dust hyperfine choose-gui
```

---

# **When to use what**

| Goal                            | Command     |
| ------------------------------- | ----------- |
| Search code faster than grep    | `rg`        |
| Find files easily               | `fd`        |
| View files with color           | `bat`       |
| Better directory lists or trees | `eza`       |
| See what is using disk          | `dust`      |
| Benchmark commands              | `hyperfine` |

