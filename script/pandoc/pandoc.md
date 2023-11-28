# pandoc常用命令

## 生成pdf

pandoc --pdf-engine=xelatex -V CJKmainfont="Noto Sans Mono CJK SC:style=Regular" --highlight-style kate  -V colorlinks -V colorinline -V urlcolor=NavyBlue -V geometry:"top=2cm, bottom=1.5cm, left=2cm, right=2cm" -f markdown+inline_code_attributes gre.md -o gre.pdf
