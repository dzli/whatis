use std::collections::HashMap;
use std::env;
use std::fs;

fn main() {
    let path = env::args().nth(1).expect("usage: debug_tokens <file>");
    let content = fs::read_to_string(&path).expect("read");
    let tokens: Vec<_> = polyglot_tokenizer::get_linguist_tokens(&content);

    let mut counts: HashMap<String, u32> = HashMap::new();
    for tok in &tokens {
        *counts.entry(tok.to_string()).or_insert(0) += 1;
    }

    let mut sorted: Vec<(&String, &u32)> = counts.iter().collect();
    sorted.sort_by(|a, b| b.1.cmp(a.1));

    println!("total tokens (after cap):  {}", tokens.len());
    println!("unique tokens:             {}", counts.len());
    println!("\ntop 30 tokens by frequency:");
    for (tok, n) in sorted.iter().take(30) {
        println!("  {:>6}  {}", n, tok);
    }
}
