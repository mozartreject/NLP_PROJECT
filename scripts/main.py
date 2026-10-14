"""YAKE extraction demo; lower YAKE scores indicate greater relevance."""
import argparse
from pathlib import Path
import yake


def extractor(top=10):
    return yake.KeywordExtractor(lan='en', n=3, dedupLim=0.8,
                                 dedupFunc='leve', windowsSize=1, top=top)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=Path)
    parser.add_argument('--text')
    args = parser.parse_args()
    text = args.file.read_text(encoding='utf-8') if args.file else args.text
    if not text:
        text = input('Paste a paragraph and press Enter: ')
    for rank, (phrase, score) in enumerate(extractor().extract_keywords(text), 1):
        print(f'{rank:2}. {phrase:<45} {float(score):.6f}')


if __name__ == '__main__':
    main()
