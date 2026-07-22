---
name: c-cpp-code-standards
description: Use when writing, modifying, reviewing, or generating C/C++ code for distribution-department projects that must follow local programming standards, embedded-software mandatory rules, file headers, comments, naming, layout, safety, and maintainability constraints.
---

# C/C++ Code Standards

## Overview
Follow the local software programming standards before writing or changing C/C++ code. Treat rules marked mandatory in the reference documents as hard constraints; when documents conflict, prefer the embedded mandatory standard, then the technical-center mandatory standard, then department/general recommendations.

## Source References
- `reference/embedded-software-mandatory-standard/配电部嵌入式软件强制要求规范-1-20220922.md`
- `reference/1-technical-center-software-standard/1技术中心软件编程规范1.1-2021.md`
- `reference/0-software-programming-standard-pd/0软件编程规范1.2-2021配电部.md`

## Required Checks Before Coding
- Use existing project conventions if they are stricter; do not introduce unrelated style churn.
- For new C/C++ files, include a Chinese file header comment with file name, author, version, generation date, overview, and modification log.
- Use GBK for C/C++ only when the target project already requires it; otherwise preserve existing file encoding.
- Keep source files under 3000 lines, preferably under 2000 lines; keep functions under 400 lines and focused on one responsibility.
- Keep include paths relative; never include headers by full absolute path.

## Formatting
- Indent with 4 spaces; do not use tabs.
- Keep lines preferably within 80 columns and never above 120 columns unless preserving existing generated/legacy content.
- Put binary and ternary operators with one space on both sides; put one space after `if`, `for`, `do`, `while`, `switch`, and `case`.
- Separate functions, local variable groups, and distinct logical blocks with blank lines; do not use two or more consecutive blank lines.
- Keep comments aligned with the code they describe.
- Avoid nesting loops/branches deeply; loop nesting over 4 levels or branch nesting over 5 levels requires redesign.

## Comments
- Use simplified Chinese for required comments.
- Use `/** ... */` for file headers, function interface comments, global variables, constants, macros, and comments expected to be extracted by documentation tools.
- Use `//` for local variables, structure fields, and local code-block comments.
- Keep effective comments above 20 percent where practical, but avoid noisy comments that restate obvious code.
- Public interface functions need detailed declaration comments; internal functions may use simpler comments.
- Function comments describe function name, purpose, input parameters, output parameters, return value, extra usage notes, and modification log.
- Data structures, arrays, classes, enums, and every structure field/class field need comments; include value ranges when relevant.
- Global variables require detailed comments covering purpose, value range, accessors/modifiers, and access notes.

## Naming
- File basic names use lowercase letters and digits only, start with a letter, are no longer than 64 characters, use `_` between words, and must not use Chinese characters.
- Header/source pairs use the same basic name; suffix length is no more than 5 characters, such as `.h`, `.cpp`, `.inc`, `.def`, `.cfg`.
- Identifiers must be meaningful, clear, and consistent; avoid pinyin, unexplained abbreviations, arbitrary letters, and names that differ only by case.
- Macro names and constants use all uppercase plus underscores; variables and functions must not be all uppercase.
- Global variables use `g_`; static globals use `s_`; class members use `m_`; pointer variables use `p` when following existing project style.
- Local loop variables may use `i`, `j`, `k`, `m`, `n`; avoid `l` because it resembles `1`; other variables should not be single-character names.
- Non-class functions follow module-verb-noun intent; class methods follow verb-noun intent.

## C/C++ Safety Rules
- Initialize every variable before use, including class members in constructors and local variables in functions.
- Validate all function inputs at function entry, especially pointers, ranges, indexes, buffer lengths, and externally supplied values.
- Validate values introduced through globals, class members, return values, and output parameters before use.
- Check function return values before use, especially pointers, resource handles, allocation results, file handles, database results, and environment values.
- Do not rely only on `assert` for parameter legality because release builds may disable it.
- If a pointer parameter is input-only, declare it `const`.
- Do not use function parameters as work variables; copy to locals when mutation is needed.
- Do not return pointers or references to stack memory.
- Reentrant functions must avoid static locals; protect any necessary global access with appropriate synchronization.

## Memory, Strings, Files
- Release or close every acquired resource on every return path; use RAII in C++ where possible.
- Match allocation and release forms: `new` with `delete`, `new[]` with `delete[]`, `malloc` with `free`; never delete a `void *`.
- Before overwriting a pointer that owns memory, free/release the previous resource when appropriate.
- Never copy more bytes than a destination buffer can hold; every string operation must preserve a terminating `\0`.
- Do not use unsafe string functions `strcpy`, `sprintf`, `strcat`, or `gets`; use bounded alternatives such as `strncpy`, `snprintf`, `strncat`, or `gets_s` where supported.
- Limit string input widths, for example use bounded `fscanf` formats instead of unbounded `%s`.
- Do not compute buffer length with `sizeof(pointer)` after an array decays to a pointer; pass explicit buffer length.
- For file operations, check file state/handle before use and restrict filenames to application directories; forbid `./` and `../` path operations.
- Do not hard-code passwords, keys, or sensitive values; never log secrets. Mask unavoidable sensitive logs with `*`.

## Expressions and Data
- Make expression evaluation order explicit; avoid side effects such as `i++` inside another function argument expression.
- Do not write overly complex compound expressions; split them into named intermediate steps.
- Avoid off-by-one errors: array indexes must be `>= 0` and `< length`.
- Do not use negative values as array indexes.
- Do not compare floating-point values for equality or inequality; compare with a tolerance or ordering checks.
- Compare integer values directly with `0`, boolean values by boolean meaning, and pointer values with `NULL`/`nullptr` according to project language level.
- Do not modify a `for` loop variable inside the loop body.
- Avoid implicit signed/unsigned conversions that can overflow or become huge values.
- Check division denominators, square-root operands, numeric boundaries, time/day/month/year/leap-year boundaries, and timezone assumptions.
- Do not use raw numeric constants repeatedly; use existing platform macros/constants first, otherwise define a named constant.

## Header and File Structure
- Header files must have include guards or equivalent once-only protection.
- Standard library headers use angle brackets; project headers use quotes.
- Header names must not conflict with standard library header names.
- Header files contain declarations, macros, type definitions, data-structure declarations, extern declarations, and public function declarations; do not place definitions there unless the project convention requires it.
- Source files should be ordered as file header comment, includes, constants/defines, typedefs/enums/declarations, global data, then function modules.
- Group related functions together, each preceded by its required function comment.

## Review Checklist
- File header, function comments, structure/field comments, and global comments are present and in Chinese where required.
- Naming prefixes, macro capitalization, file names, and include paths follow the standards.
- Parameters, return values, pointers, indexes, buffer sizes, strings, files, and resources are validated.
- No unsafe string functions, unchecked file handles, hard-coded secrets, `delete`/`delete[]` mismatch, stack pointer return, or uninitialized variable remains.
- Formatting uses 4-space indentation, one-space operators, reasonable blank lines, and no excessive line length.
- Full details and examples are available in the three Markdown reference documents under `reference/`.
