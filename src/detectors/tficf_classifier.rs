use std::collections::HashMap;

include!("../codegen/tficf-model.rs");

const MAX_TOKEN_BYTES: usize = 32;

// Cap how much a single repeated token can contribute to the score. Without
// this, files padded with a fill character (e.g. obfuscated JS with
// thousands of `@` chars) let one low-ICF token dominate cosine similarity
// and bias the verdict toward whichever language's centroid happens to
// weight that token the most. With the cap, tf = 1 + log(min(freq, K)) so
// occurrences beyond K stop influencing the score. Must match the value
// used at training time in codegen.rs::train_tficf_classifier.
const TF_CAP: u32 = 100;

pub fn classify_tficf(content: &str, candidates: &[&'static str]) -> &'static str {
    let mut counts: HashMap<u32, u32> = HashMap::with_capacity(content.len() / 8);
    for token in polyglot_tokenizer::get_linguist_tokens(content) {
        if token.len() > MAX_TOKEN_BYTES {
            continue;
        }
        if let Some(&idx) = TFICF_VOCABULARY.get(&*token) {
            *counts.entry(idx).or_insert(0) += 1;
        }
    }

    let mut query: Vec<(u32, f64)> = counts
        .into_iter()
        .map(|(idx, freq)| {
            let capped = freq.min(TF_CAP);
            let tf = 1.0 + (capped as f64).ln();
            (idx, tf * TFICF_ICF[idx as usize])
        })
        .collect();
    let norm = query.iter().map(|(_, v)| v * v).sum::<f64>().sqrt();
    if norm > 0.0 {
        for (_, v) in query.iter_mut() {
            *v /= norm;
        }
    }
    query.sort_by_key(|x| x.0);

    let mut best_lang: &'static str = "";
    let mut best_score = f64::NEG_INFINITY;
    let mut score_one = |lang: &'static str| {
        if let Some(centroid) = TFICF_CENTROIDS.get(lang) {
            let score = cosine_dot(&query, centroid);
            if score > best_score {
                best_score = score;
                best_lang = lang;
            }
        }
    };
    if candidates.is_empty() {
        for &lang in TFICF_CENTROIDS.keys() {
            score_one(lang);
        }
    } else {
        for &lang in candidates {
            score_one(lang);
        }
    }

    if best_lang.is_empty() {
        if candidates.is_empty() {
            ""
        } else {
            candidates[0]
        }
    } else {
        best_lang
    }
}

fn cosine_dot(a: &[(u32, f64)], b: &[(u32, f64)]) -> f64 {
    let (mut i, mut j) = (0, 0);
    let mut sum = 0.0;
    while i < a.len() && j < b.len() {
        if a[i].0 == b[j].0 {
            sum += a[i].1 * b[j].1;
            i += 1;
            j += 1;
        } else if a[i].0 < b[j].0 {
            i += 1;
        } else {
            j += 1;
        }
    }
    sum
}
