import argparse
import sys
from pathlib import Path
import re


# Matches a single-line control statement whose body is a single statement
# (no braces).  Used to expand them into Allman-style blocks.
CONTROL_PATTERN = re.compile(
    r"^(?P<indent>\s*)(?P<keyword>if|foreach|for|while)\s*(?P<condition>\(.*\))\s+(?P<body>.+;)$"
)
CONTROL_START_PATTERN = re.compile(r"^\s*(if|foreach|for|while|switch|try)\b")
# Continuations that must not be separated from the preceding closing brace by
# a blank line.
POST_CONTROL_PATTERN = re.compile(r"^\s*(else\b|catch\b|finally\b)")
COMMENT_LINE_PATTERN = re.compile(r"^\s*(//|/\*|\*)")

# Tokeniser used to skip string literals and comments when applying spacing
# fixes.  Order matters: multi-line strings / verbatim strings first, then
# single-line strings, then line comments, then block comments.
_TOKEN_RE = re.compile(
    r'(@"(?:[^"]|"")*")'          # verbatim string
    r'|("(?:[^"\\]|\\.)*")'       # regular string literal
    r"|('(?:[^'\\]|\\.)*')"       # char literal
    r"|(//[^\n]*)"                # line comment
    r"|(/\*.*?\*/)"               # block comment (non-greedy, single line)
    r"|([\s\S])",                 # everything else, one char at a time
    re.DOTALL,
)


def _apply_outside_strings(line, transform):
    """Apply *transform* only to the code parts of a line, leaving string
    literals and comments untouched."""
    code_buf = []
    result = []

    for m in _TOKEN_RE.finditer(line):
        char = m.group(6)
        if char is not None:
            # Accumulate plain code characters.
            code_buf.append(char)
        else:
            # Flush accumulated code through the transform, then emit the
            # string/comment token verbatim.
            if code_buf:
                result.append(transform("".join(code_buf)))
                code_buf = []
            result.append(m.group(0))

    # Flush any remaining code.
    if code_buf:
        result.append(transform("".join(code_buf)))

    return "".join(result)


def _fix_spacing(code_fragment):
    """Fix keyword-parenthesis spacing and control-statement brace spacing in
    a pure-code fragment (no strings or comments)."""
    # Ensure a space between control keywords and '('.
    code_fragment = re.sub(r"\b(if|foreach|for|while|switch|catch|using|lock|fixed|unsafe)\(", r"\1 (", code_fragment)
    # Remove spaces immediately inside parentheses: ( x ) -> (x).
    # Only targets single-level parens; complex expressions are left to the
    # developer.
    code_fragment = re.sub(r"\(\s+", "(", code_fragment)
    code_fragment = re.sub(r"\s+\)", ")", code_fragment)
    # Ensure a space after commas (but not inside verbatim strings — those are
    # already excluded by the caller).
    code_fragment = re.sub(r",(?! |$|\n)", ", ", code_fragment)
    return code_fragment


def expand_single_line_controls(lines):
    """Expand single-line control statements into Allman-style blocks."""
    result = []

    for line in lines:
        match = CONTROL_PATTERN.match(line)
        if match is None or "{" in match.group("body"):
            result.append(line)
            continue

        indent = match.group("indent")
        result.extend(
            [
                indent + match.group("keyword") + " " + match.group("condition"),
                indent + "{",
                indent + "    " + match.group("body"),
                indent + "}",
            ]
        )

    return result


def _last_non_blank(result):
    """Return the last non-blank line already in *result*, or None."""
    for line in reversed(result):
        if line.strip():
            return line
    return None


def add_blank_lines_before_statements(lines):
    """Insert a blank line before control statements and return statements
    according to SKILL.md rules:
    - Control statement: blank line before, unless the preceding non-blank line
      is a comment.
    - return: blank line before, unless it is the first statement after '{'.
    """
    result = []

    for line in lines:
        stripped = line.strip()
        is_control = CONTROL_START_PATTERN.match(line) is not None
        is_return = stripped.startswith("return ") or stripped == "return;"

        if is_return:
            prev_non_blank = _last_non_blank(result)
            if prev_non_blank is not None and prev_non_blank.strip() != "{":
                if result and result[-1].strip():
                    result.append("")
        elif is_control:
            prev_non_blank = _last_non_blank(result)
            if (
                prev_non_blank is not None
                and prev_non_blank.strip()
                and not COMMENT_LINE_PATTERN.match(prev_non_blank)
            ):
                if result and result[-1].strip():
                    result.append("")

        result.append(line)

    return result


def remove_blank_lines_before_post_controls(lines):
    """Remove blank lines immediately before else/catch/finally so that the
    closing brace and its continuation stay together."""
    result = []

    for index, line in enumerate(lines):
        if not line.strip():
            # Look ahead to the next non-blank line.
            next_index = index + 1
            while next_index < len(lines) and not lines[next_index].strip():
                next_index += 1
            if next_index < len(lines) and POST_CONTROL_PATTERN.match(lines[next_index]):
                continue  # drop this blank line

        result.append(line)

    return result


def control_block_closures(lines):
    """Return the set of line indices that are the closing '}' of a control
    block."""
    stack = []
    closures = set()

    for index, line in enumerate(lines):
        opening_count = line.count("{")
        closing_count = line.count("}")

        if CONTROL_START_PATTERN.match(line) is not None:
            stack.append([index, None])

        for _ in range(opening_count):
            if stack and stack[-1][1] is None:
                stack[-1][1] = index

        for _ in range(closing_count):
            if stack and stack[-1][1] is not None:
                stack.pop()
                closures.add(index)

    return closures


def add_blank_lines_after_controls(lines):
    """Add a blank line after a control block's closing '}', unless the next
    non-blank line is another '}', or an else/catch/finally continuation."""
    closures = control_block_closures(lines)
    result = []

    for index, line in enumerate(lines):
        result.append(line)
        if index not in closures:
            continue

        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1

        if next_index >= len(lines):
            continue

        next_stripped = lines[next_index].strip()
        if next_stripped == "}" or POST_CONTROL_PATTERN.match(lines[next_index]):
            continue

        if next_index == index + 1:
            result.append("")

    return result


def collapse_blank_lines(lines):
    """Collapse consecutive blank lines to a single blank line and apply
    keyword/spacing fixes to code lines."""
    result = []

    for line in lines:
        if not line.strip() and result and not result[-1].strip():
            continue

        line = _apply_outside_strings(line.rstrip(), _fix_spacing)
        result.append(line)

    return result


def remove_brace_adjacent_blank_lines(lines):
    """Remove blank lines immediately after '{' (except before return) and
    immediately before '}'."""
    result = []

    for index, line in enumerate(lines):
        if not line.strip():
            previous = lines[index - 1].strip() if index > 0 else ""
            following = lines[index + 1].strip() if index + 1 < len(lines) else ""
            if (
                previous == "{"
                and following != "return;"
                and not following.startswith("return ")
            ) or following == "}":
                continue

        result.append(line)

    return result


def format_file(path: Path):
    text = path.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    # Normalise to LF for all processing steps.
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    lines = expand_single_line_controls(lines)
    lines = remove_brace_adjacent_blank_lines(lines)
    lines = add_blank_lines_before_statements(lines)
    lines = add_blank_lines_after_controls(lines)
    lines = remove_blank_lines_before_post_controls(lines)
    lines = remove_brace_adjacent_blank_lines(lines)
    lines = collapse_blank_lines(lines)
    new_normalized = "\n".join(lines)
    # Skip writing if nothing changed — avoids spurious line-ending-only diffs.
    if new_normalized == normalized:
        return
    path.write_text(new_normalized, encoding="utf-8", newline="")
    # Restore CRLF if the original file used it.
    if newline == "\r\n":
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))


def main():
    parser = argparse.ArgumentParser(
        description="Format C# source files under a given directory."
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default="LogicEngineConfigTool/",
        help="Root directory to search recursively for .cs files "
             "(default: LogicEngineConfigTool/)",
    )
    args = parser.parse_args()

    root = Path(args.directory)
    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    cs_files = list(root.rglob("*.cs"))
    if not cs_files:
        print(f"No .cs files found under '{root}'.")
        return

    for path in cs_files:
        print(f"Formatting {path}")
        format_file(path)

    print(f"Done. Formatted {len(cs_files)} file(s).")


if __name__ == "__main__":
    main()
