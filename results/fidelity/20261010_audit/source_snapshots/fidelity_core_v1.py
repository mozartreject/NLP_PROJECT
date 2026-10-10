"""Controlled one-choice-at-a-time scorer variants; baseline matches replication.core.
Choices are sensitivity analyses, not recovered publication parameters.
"""
import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from replication.core import Config, similarity, tokenize as original_tokenize
from segtok.segmenter import split_multi
from segtok.tokenizer import web_tokenizer, split_contractions

@dataclass(frozen=True)
class Policy:
    tokenizer: str = "regex"
    casing_log: str = "base2"
    position_log: str = "base2"
    frequency_population: str = "all"
    relatedness_plpr: bool = True
    position_unique: bool = False
    casing_singleton: str = "one"
    phrase_internal_transition: bool = False
    strip_plural: bool = False
    casing_add_one: bool = False

    def __post_init__(self):
        for field, choices in {"tokenizer":("regex","segtok","special_chars"), "casing_log":("base2","natural"), "position_log":("base2","natural"), "frequency_population":("all","nonstop"), "casing_singleton":("one","log1p")}.items():
            if getattr(self,field) not in choices: raise ValueError(field)

def policy_tokenize(text, policy):
    if policy.tokenizer == "regex": return original_tokenize(text)
    if policy.tokenizer == "segtok":
        return [[t for t in split_contractions(web_tokenizer(sentence)) if t and not (t.startswith("\'") and len(t)>1)] for sentence in split_multi(text)]
    return [re.findall(r"[^\W\d_]+|[^\w\s]|\d+", " ".join(sentence)) for sentence in original_tokenize(text)]


def extract(text, config=Config(), omit=None, stopwords=None, collect_trace=True, policy=Policy()):
    stopwords = ENGLISH_STOP_WORDS if stopwords is None else stopwords
    sentences=policy_tokenize(text,policy)
    terms={}; candidates=Counter()
    for sid, sentence in enumerate(sentences, 1):
        block=[]; surface=[]; word_index=0
        def flush():
            for start in range(len(block)):
                for size in range(1,config.max_ngram+1):
                    words=surface[start:start+size]
                    if len(words)==size:
                        candidates[' '.join(words)]+=1
        for token in sentence:
            if not token[0].isalpha():
                flush(); block=[]; surface=[]; continue
            word=token.casefold()
            if policy.strip_plural and word.endswith("s") and len(word)>3: word=word[:-1]
            if word not in terms:
                terms[word]={'tf':0,'acronym':0,'capital':0,'sentences':[], 'left':Counter(),'right':Counter()}
            term=terms[word]; term['tf']+=1
            term['acronym']+=int(token.isupper() and len(token)>1)
            term['capital']+=int(token.istitle() and word_index>0)
            term['sentences'].append(sid)
            for prior in block[-config.window:]:
                term['left'][prior]+=1; terms[prior]['right'][word]+=1
            block.append(word); surface.append(token.casefold()); word_index+=1
        flush()
    if not terms: return [], {'sentences':sentences,'features':[], 'candidates':[], 'decisions':[]}
    frequencies=[t['tf'] for w,t in terms.items() if policy.frequency_population=='all' or w not in stopwords]
    if not frequencies: frequencies=[t['tf'] for t in terms.values()]
    mean=statistics.mean(frequencies); std=statistics.pstdev(frequencies); maximum=max(t["tf"] for t in terms.values())
    features=[]
    for word,t in terms.items():
        tf=t['tf']
        left=len(t['left'])/sum(t['left'].values()) if t['left'] else 0
        right=len(t['right'])/sum(t['right'].values()) if t['right'] else 0
        pl=len(t['left'])/maximum; pr=len(t['right'])/maximum
        values={
            'WCase':max(t['acronym'],t['capital'])/(1+math.log(tf) if policy.casing_add_one else ((math.log(tf) if policy.casing_log=='natural' else math.log2(tf)) if tf>1 else (math.log(1+tf) if policy.casing_singleton=='log1p' else 1))),
            'WPosition':(math.log if policy.position_log=='natural' else math.log2)((math.log if policy.position_log=='natural' else math.log2)(2+statistics.median(sorted(set(t['sentences'])) if policy.position_unique else t['sentences']))),
            'WFreq':tf/(mean+std),
            'WRel':(.5+left*tf/maximum+(pl if policy.relatedness_plpr else 0))+(.5+right*tf/maximum+(pr if policy.relatedness_plpr else 0)),
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
        words=phrase.split()
        if policy.strip_plural: words=[w[:-1] if w.endswith('s') and len(w)>3 else w for w in words]
        eligible=words[0] not in stopwords and words[-1] not in stopwords
        hs=[terms[w]['score'] for w in words]
        product=math.prod(hs);total=sum(hs)
        if policy.phrase_internal_transition and eligible:
            product=1.;total=0.
            for j,w in enumerate(words):
                if w in stopwords:
                    prev,nxt=words[j-1],words[j+1]
                    prob=terms[prev]['right'].get(w,0)/terms[prev]['tf'] * terms[w]['right'].get(nxt,0)/terms[nxt]['tf']
                    product *= 2-prob;total -= 1-prob
                else:product *= terms[w]['score'];total += terms[w]['score']
        score=product/(tf*(1+total))
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
