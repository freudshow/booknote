# `GNU bc`

## References

- [GNU bc](https://www.gnu.org/software/bc/)
- [GNU bc Manual](https://www.gnu.org/software/bc/manual/)
- [GNU bc Source Code](https://www.gnu.org/software/bc/download.html)

## Installation

1. install `bc` package:

```bash
sudo apt install bc      # Ubuntu/Debian
sudo yum install bc      # CentOS/RHEL
sudo pacman -S bc        # Arch Linux
sudo dnf install bc      # Fedora
```

1. install `bc` from source code:

```bash
./configure --prefix=/usr/local/bc
make
make install
```

## Usage

```bash
bc -l # load math library
bc -q # quiet mode, no banner, no prompt, no error messages
bc -i # interactive mode, prompt for input, no error messages
bc -w # warn about non-standard bc constructs
bc -s # standard mode, non-standard features give errors
bc -v # print version information and exit
bc -h # print help information and exit
```

## grammar

- `1+2`: add two numbers
- `1-2`: subtract two numbers
- `1*2`: multiply two numbers

```bash
bc <<EOF
1+2
EOF
```

```bash
bc <<EOF
define square(x) {
    return x*x;
}

square(5) #output 25
EOF
```

## cross-compile

```bash
export CC=arm-linux-gnueabihf-gcc
export AR=arm-linux-gnueabihf-ar
export RANLIB=arm-linux-gnueabihf-ranlib
export PREFIX=/home/floyd/bcinstall/

./configure \
    --host=arm-linux-gnueabihf \
    --prefix=$PREFIX

make -j$(nproc)
make install
```

## `flex and bison`

### `flex`

```bash
flex -o lex.yy.c lex.l
bison -d -o parser.tab.c parser.y
```

```bash
flex -o lex.yy.c lex.l
bison -d -o parser.tab.c parser.y
```

```bash
flex -o lex.yy.c lex.l
bison -d -o parser.tab.c parser.y
```
### `bison`

## Recursive Descent Parser

## left Recursive
