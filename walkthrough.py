"""Export actual intermediate values from the installed YAKE implementation."""
import csv
import json
from pathlib import Path
from yake.datarepresentation import DataCore
from evaluate import ROOT, load_data
from main import extractor


def save_csv(path, rows):
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)


def main():
    rows, digest = load_data()
    ident, text, gold = rows[0]
    out = ROOT / 'results' / 'walkthrough'
    out.mkdir(parents=True, exist_ok=True)
    x = extractor()
    dc = DataCore(text=text, stopword_set=x.stopword_set, windowsSize=1, n=3)
    dc.build_single_terms_features()
    dc.build_mult_terms_features()
    (out / '01_document.txt').write_text(text)
    (out / '02_sentences.json').write_text(json.dumps(dc.sentences_str, indent=2))
    features = []
    for term in dc.terms.values():
        features.append(dict(word=term.unique_term, frequency=term.tf, stopword=term.stopword,
            casing=float(term.WCase), position=float(term.WPos), normalized_frequency=float(term.WFreq),
            context_relatedness=float(term.WRel), sentence_spread=float(term.WSpread), score=float(term.H)))
    save_csv(out / '03_word_features.csv', sorted(features, key=lambda r:r['score']))
    candidates = [dict(phrase=c.kw, words=c.size, frequency=c.tf, valid=bool(c.isValid()), score=float(c.H))
                  for c in dc.candidates.values()]
    save_csv(out / '04_candidates.csv', sorted(candidates, key=lambda r:r['score']))
    ranked = x.extract_keywords(text)
    save_csv(out / '05_final_keywords.csv', [dict(rank=i, phrase=p, score=float(s),
             gold_match=' '.join(p.casefold().split()) in gold) for i,(p,s) in enumerate(ranked,1)])
    (out / '06_gold_keywords.json').write_text(json.dumps(sorted(gold), indent=2))
    (out / '00_dataset_audit.json').write_text(json.dumps(dict(documents=len(rows),
        category_counts={category:sum(r[0].split('-')[0]==category for r in rows)
                         for category in sorted({r[0].split('-')[0] for r in rows})},
        sample_document=ident, archive_sha256=digest, training='None: YAKE is unsupervised'), indent=2))
    for name in sorted(out.iterdir()):
        print(name.name)
    print('Actual YAKE intermediate values saved to', out)


if __name__ == '__main__':
    main()
