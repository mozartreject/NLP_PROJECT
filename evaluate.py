"""Partial experimental reproduction: YAKE vs documented baseline adaptations."""
import argparse
import csv
import hashlib
import importlib.metadata
import json
import platform
import re
import time
import zipfile
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from main import extractor

ROOT = Path(__file__).resolve().parent


def normalize(text):
    # Case-insensitive exact phrase matching; no stemming or partial matching.
    return ' '.join(text.casefold().split())


def load_data():
    archive = ROOT / 'data' / '500N-KPCrowd-v1.1.zip'
    with zipfile.ZipFile(archive) as z:
        docs = sorted(n for n in z.namelist() if '/docsutf8/' in n and n.endswith('.txt'))
        rows = []
        for name in docs:
            ident = Path(name).stem
            key = '500N-KPCrowd-v1.1/keys/' + ident + '.key'
            gold = {normalize(k) for k in z.read(key).decode('utf-8-sig').splitlines() if k.strip()}
            if not gold:
                raise ValueError('No gold labels: ' + ident)
            rows.append((ident, z.read(name).decode('utf-8-sig'), gold))
    if len(rows) != 500 or len({r[0] for r in rows}) != 500:
        raise ValueError('Expected 500 unique documents')
    return rows, hashlib.sha256(archive.read_bytes()).hexdigest()


def rake(text, top):
    # Transparent RAKE-style adaptation: English sklearn stoplist, 1-3 word candidates.
    chunks = []
    for sentence in re.split(r'[^\w\s\'-]+', text.casefold()):
        chunk = []
        for word in sentence.split():
            if word in ENGLISH_STOP_WORDS or not any(c.isalpha() for c in word):
                if chunk:
                    chunks.append(chunk)
                chunk = []
            else:
                chunk.append(word)
        if chunk:
            chunks.append(chunk)
    freq, degree = Counter(), Counter()
    for chunk in chunks:
        for word in chunk:
            freq[word] += 1
            degree[word] += len(chunk)
    scores = {}
    for chunk in chunks:
        if 1 <= len(chunk) <= 3:
            phrase = ' '.join(chunk)
            scores[phrase] = sum(degree[w] / freq[w] for w in chunk)
    return sorted(scores, key=lambda p: (-scores[p], p))[:top]


def metrics(predictions, gold, k):
    pred = {normalize(p) for p in predictions}
    hits = len(pred & gold)
    p = hits / k  # P@k: unfilled slots count as misses.
    r = hits / len(gold)
    return p, r, 2*p*r/(p+r) if p+r else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=0, help='0 = all 500; positive = smoke run')
    args = parser.parse_args()
    if args.limit < 0:
        parser.error('--limit must be nonnegative')
    rows, digest = load_data()
    rows = rows[:args.limit] if args.limit else rows
    texts = [row[1] for row in rows]
    # Transductive corpus statistics for this unsupervised baseline, not a trained classifier.
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), stop_words='english', lowercase=True)
    matrix = vectorizer.fit_transform(texts)
    names = vectorizer.get_feature_names_out()
    y = extractor()
    records, outputs = [], []
    for i, (ident, text, gold) in enumerate(rows):
        for method in ['YAKE', 'RAKE-adapted', 'TF-IDF-adapted']:
            start = time.perf_counter()
            if method == 'YAKE':
                phrases = [p for p, _ in y.extract_keywords(text)]
            elif method == 'RAKE-adapted':
                phrases = rake(text, 10)
            else:
                row = matrix.getrow(i)
                order = np.argsort(-row.data, kind='stable')[:10]
                phrases = [names[row.indices[j]] for j in order]
            elapsed = time.perf_counter() - start
            p, r, f = metrics(phrases, gold, 10)
            records.append(dict(document=ident, method=method, precision_at_10=p, recall_at_10=r,
                                f1_at_10=f, extraction_seconds=elapsed))
            outputs.append(dict(document=ident, method=method, predicted=phrases, gold=sorted(gold)))
        if (i+1) % 50 == 0:
            print(f'Processed {i+1}/{len(rows)} documents', flush=True)
    out = ROOT / 'results' / ('smoke' if args.limit else 'full')
    out.mkdir(parents=True, exist_ok=True)
    with (out / 'per_document.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader(); writer.writerows(records)
    summary = []
    for method in ['YAKE', 'RAKE-adapted', 'TF-IDF-adapted']:
        subset = [r for r in records if r['method'] == method]
        summary.append(dict(method=method, documents=len(subset), **{
            key: float(np.mean([r[key] for r in subset]))
            for key in ['precision_at_10', 'recall_at_10', 'f1_at_10', 'extraction_seconds']}))
    (out / 'summary.json').write_text(json.dumps(summary, indent=2))
    (out / 'predictions.json').write_text(json.dumps(outputs, indent=2, ensure_ascii=False))
    metadata = dict(python=platform.python_version(), packages={p: importlib.metadata.version(p)
                    for p in ['yake', 'numpy', 'scikit-learn']}, archive_sha256=digest,
                    documents=len(rows), top=10, ngram_max=3, dedup_function='leve', dedup_threshold=0.8,
                    context_window=1, matching='casefold + whitespace normalization; no stemming',
                    aggregation='mean per-document P@10, recall and F1',
                    timing='extraction only; TF-IDF fitting excluded',
                    source='https://github.com/INESCTEC/KeywordExtractor-Datasets',
                    scope='partial replication using current YAKE; baseline implementations adapted')
    (out / 'metadata.json').write_text(json.dumps(metadata, indent=2))
    for row in summary:
        print(f"{row['method']:18} P@10={row['precision_at_10']:.4f} R={row['recall_at_10']:.4f} F1={row['f1_at_10']:.4f}")
    print('Results:', out)


if __name__ == '__main__':
    main()
