"""Independent reconstruction of ECIR 2018 printed equations; see protocol.
No training, no use of gold labels, no calls to YAKE scoring internals.
"""
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

@dataclass(frozen=True)
class Config:
    top_k: int = 10
    max_ngram: int = 3
    window: int = 1
    dedup_threshold: float = .8
    def __post_init__(self):
        if self.top_k < 1 or self.max_ngram < 1 or self.window < 1:
            raise ValueError('Counts must be positive')
        if not 0 <= self.dedup_threshold <= 1:
            raise ValueError('Invalid dedup threshold')

def similarity(a, b):
    """1 - edit distance / max string length, including spaces."""
    if not a and not b: return 1.
    previous = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(current[-1]+1, previous[j]+1, previous[j-1]+(ca != cb)))
        previous = current
    return 1-previous[-1]/max(len(a), len(b))

def tokenize(text):
    # Explicit engineering tokenizer: punctuation is a hard phrase boundary.
    sentences=[]
    for sentence in re.split(r'(?<=[.!?])\s+|\n+', text):
        tokens=re.findall(r"[^\W\d_]+(?:['’-][^\W\d_]+)*|[^\w\s]|\d+", sentence, re.UNICODE)
        if tokens: sentences.append(tokens)
    return sentences

def extract(text, config=Config(), omit=None, stopwords=None, collect_trace=True):
    stopwords = ENGLISH_STOP_WORDS if stopwords is None else stopwords
    sentences=tokenize(text)
    terms={}; candidates=Counter()
    for sid, sentence in enumerate(sentences, 1):
        block=[]; word_index=0
        def flush():
            for start in range(len(block)):
                for size in range(1,config.max_ngram+1):
                    words=block[start:start+size]
                    if len(words)==size:
                        candidates[' '.join(words)]+=1
        for token in sentence:
            if not token[0].isalpha():
                flush(); block=[]; continue
            word=token.casefold()
            if word not in terms:
                terms[word]={'tf':0,'acronym':0,'capital':0,'sentences':[], 'left':Counter(),'right':Counter()}
            term=terms[word]; term['tf']+=1
            term['acronym']+=int(token.isupper() and len(token)>1)
            term['capital']+=int(token.istitle() and word_index>0)
            term['sentences'].append(sid)
            for prior in block[-config.window:]:
                term['left'][prior]+=1; terms[prior]['right'][word]+=1
            block.append(word); word_index+=1
        flush()
    if not terms: return [], {'sentences':sentences,'features':[], 'candidates':[], 'decisions':[]}
    frequencies=[t['tf'] for t in terms.values()]
    mean=statistics.mean(frequencies); std=statistics.pstdev(frequencies); maximum=max(frequencies)
    features=[]
    for word,t in terms.items():
        tf=t['tf']
        left=len(t['left'])/sum(t['left'].values()) if t['left'] else 0
        right=len(t['right'])/sum(t['right'].values()) if t['right'] else 0
        pl=len(t['left'])/maximum; pr=len(t['right'])/maximum
        values={
            'WCase':max(t['acronym'],t['capital'])/(math.log2(tf) if tf>1 else 1),
            'WPosition':math.log2(math.log2(2+statistics.median(t['sentences']))),
            'WFreq':tf/(mean+std),
            'WRel':(.5+left*tf/maximum+pl)+(.5+right*tf/maximum+pr),
            'WSpread':len(set(t['sentences']))/len(sentences)
        }
        if omit:
            # Defined interventions: remove numerator effects with 1, denominator additions with 0.
            values[omit]=1. if omit in ('WPosition','WRel') else 0.
        score=values['WRel']*values['WPosition']/(values['WCase']+values['WFreq']/values['WRel']+values['WSpread']/values['WRel'])
        t['score']=score
        features.append(dict(word=word,tf=tf,acronym=t['acronym'],capital=t['capital'],sentence_ids=t['sentences'],PL=pl,PR=pr,H=score,**values))
    scored=[]
    for phrase,tf in candidates.items():
        words=phrase.split(); eligible=words[0] not in stopwords and words[-1] not in stopwords
        hs=[terms[w]['score'] for w in words]
        score=math.prod(hs)/(tf*(1+sum(hs)))
        scored.append({'phrase':phrase,'tf':tf,'size':len(words),'H':score,'eligible':eligible})
    scored.sort(key=lambda row:(row['H'],row['phrase']))
    selected=[]; decisions=[]
    for row in scored:
        if not collect_trace and len(selected) >= config.top_k:
            break
        reason='selected'; matched=None
        if not row['eligible']: reason='stopword_boundary'
        else:
            matched=next((p for p,s in selected if similarity(row['phrase'],p)>config.dedup_threshold),None)
            if matched: reason='near_duplicate'
            elif len(selected)>=config.top_k: reason='outside_top_k'
            else: selected.append((row['phrase'],row['H']))
        decisions.append(dict(phrase=row['phrase'],reason=reason,matched=matched))
    return selected, {'sentences':sentences,'features':features,'candidates':scored,'decisions':decisions,
                      'statistics':{'mean_tf':mean,'std_tf':std,'max_tf':maximum,'sentence_count':len(sentences)}}
