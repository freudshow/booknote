# pandoc常用命令

## 生成pdf

pandoc --pdf-engine=xelatex -V CJKmainfont="Noto Sans Mono CJK SC:style=Regular" --highlight-style zenburn  -V colorlinks -V urlcolor=NavyBlue -V geometry:"top=2cm, bottom=1.5cm, left=2cm, right=2cm" BusError.md -o BusError.pdf
