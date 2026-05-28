use crate::tokenizer::{Token, Tokenizer};
use std::borrow::Cow;

/// Emit Linguist-style tokens for classifier training/inference.
///
/// Returns `Vec<Cow<'a, str>>` to avoid allocating for the common case where
/// the output token is a slice of the input (raw idents, single-char symbols,
/// coalesced operator runs). Synthesized tokens (`SHEBANG#!…`, sigil idents)
/// and rare comment openers are owned `String`s.
///
/// Differences from `get_key_tokens`:
/// * Line and block comments become typed tokens like `COMMENT#`, `COMMENT//`,
///   `COMMENT/*`, `COMMENT<!--` etc., preserving the comment style without
///   leaking comment content.
/// * A `#!` line at the start of the file becomes `SHEBANG#!<interpreter>`,
///   where `<interpreter>` is the basename of the path or the binary after
///   `env`.
/// * Identifiers preceded immediately by `@`, `$`, or `.` are combined with
///   the sigil (`@var`, `.foo`). `#var` is not supported because the base
///   tokenizer treats `#` as a line-comment opener.
/// * Adjacent symbol characters with no intervening whitespace/token are
///   combined into a single token (`==`, `!=`, `->`, `=>`, `<<=`, etc.).
///   Brackets `()[]{}` are intentionally never coalesced; without this carve-
///   out, bracket-heavy inputs (e.g. JSFuck) collapse into one mega-token
///   that the classifier's per-token length cap then discards.
///
/// Numbers and string literals are dropped, same as `get_key_tokens`.
///
/// Known limitation: the base tokenizer in this crate has bugs around
/// multi-character block-comment delimiters (`/* */`, `<!-- -->`, `{- -}`,
/// `(* *)`) that cause them to leak through as individual symbol tokens
/// rather than `Token::BlockComment`. As a result, `COMMENT/*` and friends
/// are rarely emitted in practice; line-comment typing (`COMMENT#`,
/// `COMMENT//`, `COMMENT--`, `COMMENT%`) works as expected.
pub fn get_linguist_tokens<'a>(content: &'a str) -> Vec<Cow<'a, str>> {
    let content_base = content.as_ptr() as usize;
    let token_pos = |s: &str| -> usize { s.as_ptr() as usize - content_base };

    let raw: Vec<(Token<'a>, usize)> = Tokenizer::new(content)
        .tokens()
        .map(|t| {
            let pos = match &t {
                Token::Ident(s) | Token::Symbol(s) | Token::Number(s) => token_pos(s),
                Token::String(open, _, _)
                | Token::BlockComment(open, _, _)
                | Token::LineComment(open, _) => token_pos(open),
            };
            (t, pos)
        })
        .collect();

    let first_newline = content.find('\n').unwrap_or(content.len());

    let mut out: Vec<Cow<'a, str>> = Vec::with_capacity(raw.len());
    let mut i = 0;
    while i < raw.len() {
        let (t, pos) = (&raw[i].0, raw[i].1);
        match t {
            Token::Number(_) => {
                i += 1;
            }
            Token::String(_, body, _) => {
                if let Some(shape) = string_shape(body) {
                    out.push(Cow::Borrowed(shape));
                }
                i += 1;
            }
            Token::LineComment(opener, body) => {
                let starts_with_bang = body.starts_with('!');
                if *opener == "#" && starts_with_bang && pos < first_newline {
                    let interp = extract_interpreter(&body[1..]);
                    let mut s = String::with_capacity(9 + interp.len());
                    s.push_str("SHEBANG#!");
                    s.push_str(&interp);
                    out.push(Cow::Owned(s));
                } else {
                    out.push(line_comment_token(opener, starts_with_bang));
                }
                i += 1;
            }
            Token::BlockComment(opener, _, _) => {
                out.push(block_comment_token(opener));
                i += 1;
            }
            Token::Ident(s) => {
                out.push(Cow::Borrowed(*s));
                i += 1;
            }
            Token::Symbol(s) => {
                // Sigil + adjacent ident → combine into one owned token.
                if matches!(*s, "@" | "$" | ".") && i + 1 < raw.len() {
                    let next = &raw[i + 1];
                    if pos + s.len() == next.1 {
                        if let Token::Ident(ident_s) = &next.0 {
                            let mut owned = String::with_capacity(s.len() + ident_s.len());
                            owned.push_str(s);
                            owned.push_str(ident_s);
                            out.push(Cow::Owned(owned));
                            i += 2;
                            continue;
                        }
                    }
                }
                // Brackets emit individually so bracket-heavy inputs stay
                // tokenizable.
                if is_bracket(s) {
                    out.push(Cow::Borrowed(*s));
                    i += 1;
                    continue;
                }
                // Maximal-munch adjacent non-bracket operator-class chars.
                // Because the run is contiguous in source, we borrow a slice
                // of `content` rather than allocating.
                let mut end_pos = pos + s.len();
                let mut j = i + 1;
                while j < raw.len() {
                    if let Token::Symbol(next_s) = &raw[j].0 {
                        if raw[j].1 == end_pos && !is_bracket(next_s) {
                            end_pos += next_s.len();
                            j += 1;
                            continue;
                        }
                    }
                    break;
                }
                out.push(Cow::Borrowed(&content[pos..end_pos]));
                i = j;
            }
        }
    }

    out
}

fn line_comment_token(opener: &str, starts_with_bang: bool) -> Cow<'static, str> {
    if opener == "#" && starts_with_bang {
        return Cow::Borrowed("COMMENT#!");
    }
    match opener {
        "//" => Cow::Borrowed("COMMENT//"),
        "///" => Cow::Borrowed("COMMENT///"),
        "#" => Cow::Borrowed("COMMENT#"),
        "##" => Cow::Borrowed("COMMENT##"),
        "--" => Cow::Borrowed("COMMENT--"),
        "%" => Cow::Borrowed("COMMENT%"),
        _ => {
            let mut s = String::with_capacity(7 + opener.len());
            s.push_str("COMMENT");
            s.push_str(opener);
            Cow::Owned(s)
        }
    }
}

fn block_comment_token(opener: &str) -> Cow<'static, str> {
    match opener {
        "/*" => Cow::Borrowed("COMMENT/*"),
        "/**" => Cow::Borrowed("COMMENT/**"),
        "<!--" => Cow::Borrowed("COMMENT<!--"),
        "{-" => Cow::Borrowed("COMMENT{-"),
        "(*" => Cow::Borrowed("COMMENT(*"),
        "\"\"\"" => Cow::Borrowed("COMMENT\"\"\""),
        "'''" => Cow::Borrowed("COMMENT'''"),
        _ => {
            let mut s = String::with_capacity(7 + opener.len());
            s.push_str("COMMENT");
            s.push_str(opener);
            Cow::Owned(s)
        }
    }
}

fn is_bracket(s: &str) -> bool {
    matches!(s, "(" | ")" | "[" | "]" | "{" | "}")
}

/// Classify a string literal body by simple character-class statistics and
/// return a synthetic pseudo-token name when the shape is distinctive
/// enough to be useful as a classifier feature. The body must already
/// have most strings (short, mixed) classified out via the `< 40` short-
/// circuit so we don't bloat the vocabulary with noise.
///
/// Costs O(len) and avoids allocation. Length cap matches MAX_TOKEN_BYTES
/// in classifier (32) since these names are short.
fn string_shape(body: &str) -> Option<&'static str> {
    const MIN_LEN: usize = 40;
    const LONG_LEN: usize = 256;
    if body.len() < MIN_LEN {
        return None;
    }

    let mut percent = 0u32;
    let mut hex = 0u32;
    let mut b64 = 0u32;
    let mut total = 0u32;
    for b in body.bytes() {
        total += 1;
        if b == b'%' {
            percent += 1;
        }
        let is_hex = (b'0'..=b'9').contains(&b)
            || (b'a'..=b'f').contains(&b)
            || (b'A'..=b'F').contains(&b);
        if is_hex {
            hex += 1;
        }
        let is_b64 = (b'a'..=b'z').contains(&b)
            || (b'A'..=b'Z').contains(&b)
            || (b'0'..=b'9').contains(&b)
            || b == b'+'
            || b == b'/'
            || b == b'=';
        if is_b64 {
            b64 += 1;
        }
    }

    // URI-encoded payloads are the dominant case the classifier needs to
    // identify (document.write(unescape("%3C..."))-style).
    if percent * 10 >= total {
        return Some("STRING:URI-ENCODED");
    }
    // >=95% hex digits → likely \x-escape body or hex-encoded payload
    if hex * 100 >= total * 95 {
        return Some("STRING:HEX");
    }
    // >=95% base64 alphabet → likely base64-encoded blob
    if b64 * 100 >= total * 95 {
        return Some("STRING:BASE64");
    }
    // Long but nothing distinctive — still useful as "this language tends
    // to contain very long strings"
    if body.len() >= LONG_LEN {
        return Some("STRING:LONG");
    }
    None
}

fn extract_interpreter(after_bang: &str) -> String {
    let line = after_bang.split(['\r', '\n']).next().unwrap_or("");
    let trimmed = line.trim();
    if trimmed.is_empty() {
        return String::new();
    }

    let first_word: &str = trimmed.split_whitespace().next().unwrap_or("");
    let first_basename = first_word.rsplit('/').next().unwrap_or(first_word);

    if first_basename == "env" {
        for word in trimmed.split_whitespace().skip(1) {
            if word.contains('=') {
                continue;
            }
            if word.starts_with('-') {
                continue;
            }
            return word.rsplit('/').next().unwrap_or(word).to_string();
        }
        return String::new();
    }

    first_basename.to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn contains(toks: &[Cow<'_, str>], needle: &str) -> bool {
        toks.iter().any(|t| t == needle)
    }

    #[test]
    fn shebang_simple() {
        let toks = get_linguist_tokens("#!/usr/bin/python\nprint(1)\n");
        assert_eq!(&*toks[0], "SHEBANG#!python");
    }

    #[test]
    fn shebang_env() {
        let toks = get_linguist_tokens("#!/usr/bin/env python\nx = 1\n");
        assert_eq!(&*toks[0], "SHEBANG#!python");
    }

    #[test]
    fn shebang_env_with_flags() {
        let toks = get_linguist_tokens("#!/usr/bin/env -S python3 -u\n");
        assert!(toks[0].starts_with("SHEBANG#!"));
    }

    #[test]
    fn line_comments_typed() {
        let toks = get_linguist_tokens("// a\n# b\n-- c\n% d\n");
        assert!(contains(&toks, "COMMENT//"));
        assert!(contains(&toks, "COMMENT#"));
        assert!(contains(&toks, "COMMENT--"));
        assert!(contains(&toks, "COMMENT%"));
    }

    #[test]
    fn sigil_combines() {
        let toks = get_linguist_tokens("@foo $bar .baz");
        assert!(contains(&toks, "@foo"));
        assert!(contains(&toks, "$bar"));
        assert!(contains(&toks, ".baz"));
    }

    #[test]
    fn dot_sigil_combines_after_ident() {
        let toks = get_linguist_tokens("foo.bar");
        assert!(contains(&toks, "foo"));
        assert!(contains(&toks, ".bar"));
    }

    #[test]
    fn multi_char_symbols() {
        let toks = get_linguist_tokens("a -> b => c != d <= e :: f");
        assert!(contains(&toks, "->"));
        assert!(contains(&toks, "=>"));
        assert!(contains(&toks, "!="));
        assert!(contains(&toks, "<="));
        assert!(contains(&toks, "::"));
    }

    #[test]
    fn numbers_and_short_strings_dropped() {
        let toks = get_linguist_tokens(r#"let x = 5; let s = "hi";"#);
        assert!(!contains(&toks, "5"));
        assert!(!contains(&toks, "hi"));
        assert!(contains(&toks, "let"));
    }

    #[test]
    fn uri_encoded_string_pseudo_token() {
        // Lots of `%xx` patterns → URI-ENCODED label
        let s = "%3Cscript%3E%3Cdocument%3E%3Cwrite%3E%3Cunescape%3E%3Calert%3E";
        let src = format!("x(\"{}\")", s);
        let toks = get_linguist_tokens(&src);
        assert!(contains(&toks, "STRING:URI-ENCODED"), "got {:?}", toks);
    }

    #[test]
    fn long_string_pseudo_token() {
        // Use prose-like content with spaces and punctuation so it doesn't
        // match BASE64/HEX/URI-ENCODED shapes — only LONG should fire.
        let body = "hello world this is a long prose-like string. ".repeat(10);
        let src = format!("y(\"{}\")", body);
        let toks = get_linguist_tokens(&src);
        assert!(contains(&toks, "STRING:LONG"), "got {:?}", toks);
    }

    #[test]
    fn base64_string_pseudo_token() {
        let body = "U29mdHdhcmUgaXMgZWF0aW5nIHRoZSB3b3JsZC4gQWxsIHRoaXMgaXMganVzdCB0ZXh0Lg==";
        let src = format!("decode(\"{}\")", body);
        let toks = get_linguist_tokens(&src);
        assert!(contains(&toks, "STRING:BASE64"), "got {:?}", toks);
    }

    #[test]
    fn short_string_no_pseudo_token() {
        let toks = get_linguist_tokens(r#"y("hello world")"#);
        assert!(!toks.iter().any(|t| t.starts_with("STRING:")));
    }

    #[test]
    fn separated_symbols_dont_combine() {
        let toks = get_linguist_tokens("a ! = b");
        assert!(!contains(&toks, "!="));
        assert!(contains(&toks, "!"));
        assert!(contains(&toks, "="));
    }

    #[test]
    fn coalesced_operator_is_borrowed() {
        // For a contiguous operator run like `->`, the output should be a
        // Borrowed slice into the input (no heap allocation).
        let content = "a->b";
        let toks = get_linguist_tokens(content);
        let arrow = toks.iter().find(|t| t == &"->").unwrap();
        assert!(matches!(arrow, Cow::Borrowed(_)));
    }

    #[test]
    fn ident_is_borrowed() {
        let toks = get_linguist_tokens("foo bar");
        for t in &toks {
            assert!(matches!(t, Cow::Borrowed(_)), "unexpected owned: {:?}", t);
        }
    }
}
