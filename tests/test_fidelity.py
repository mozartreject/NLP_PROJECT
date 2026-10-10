import math,unittest
from replication.core import extract as original
from replication.fidelity_core import Policy,extract
from fidelity_experiments import holm,load_rows,CORE_POLICIES
class FidelityTests(unittest.TestCase):
 def test_baseline_matches_original_with_trace_and_ranking(self):
  for text in ['', 'the and of', 'NASA studies stars. Bright stars reveal galaxies.', 'áreas de datos. Datos importantes.', 'apple apple apple. banana. apple!']:
   self.assertEqual(original(text),extract(text))
 def test_relatedness_intervention_hand_calculation(self):
  _,a=extract('apple banana apple',stopwords=set());_,b=extract('apple banana apple',stopwords=set(),policy=Policy(relatedness_plpr=False))
  for x,y in zip(a['features'],b['features']):self.assertAlmostEqual(x['WRel']-y['WRel'],x['PL']+x['PR'])
 def test_unique_sentence_positions(self):
  _,a=extract('apple apple apple. banana. apple',stopwords=set());_,b=extract('apple apple apple. banana. apple',stopwords=set(),policy=Policy(position_unique=True))
  self.assertNotEqual(a['features'][0]['WPosition'],b['features'][0]['WPosition'])
 def test_native_frequency_does_not_remove_term_inventory(self):
  _,t=extract('the the the apple',stopwords={'the'},policy=Policy(frequency_population='nonstop'))
  self.assertEqual(t['statistics']['mean_tf'],1);self.assertEqual(len(t['features']),2)
 def test_surface_forms_preserved_when_merging_plural_statistics(self):
  _,t=extract('stars star stars',stopwords=set(),policy=Policy(strip_plural=True))
  self.assertEqual(t['features'][0]['tf'],3);self.assertIn('stars',{c['phrase'] for c in t['candidates']})
 def test_every_declared_policy_finite(self):
  for c in CORE_POLICIES.values():
   pred,_=extract('NASA observes stars in the sky. Bright stars reveal galaxies.',omit=c.get('omit'),policy=Policy(**c.get('policy',{})))
   self.assertTrue(all(math.isfinite(v) for p,v in pred))
 def test_holm_known_example(self):self.assertEqual(holm([.01,.04,.03]),[.03,.06,.06])
 def test_empty_recovered_gold_is_not_fabricated(self):
  rows,_,_=load_rows('SemEval2010');self.assertEqual(len(rows),243);self.assertNotIn('C-86',{i for i,t,g in rows});self.assertTrue(all(g for i,t,g in rows))
 def test_invalid_policy(self):
  with self.assertRaises(ValueError):Policy(tokenizer='unknown')
if __name__=='__main__':unittest.main()

class StatisticalAndSourceTests(unittest.TestCase):
 def test_holm_preserves_input_order_and_caps_probability(self):
  self.assertEqual(holm([.5,.001,.9]),[1.,.003,1.])
 def test_historical_output_order_adapter(self):
  from replication.historical import load_yake
  e=load_yake('0.3.0')(lan='en',n=3,top=10,dedupLim=.8,windowsSize=1)
  rows=e.extract_keywords('Natural language processing extracts important keywords. Important keywords describe documents.')
  self.assertTrue(all(isinstance(score,float) and isinstance(phrase,str) for score,phrase in rows))
  self.assertEqual([s for s,p in rows],sorted(s for s,p in rows))
 def test_missing_maui_gold_and_official_gold_are_different_cases(self):
  import zipfile
  from replication.historical import CACHE
  with zipfile.ZipFile(CACHE/'SemEval2010-Maui.zip') as z:self.assertEqual(z.read('maui-semeval2010-test/C-86.key'),b'')
 def test_internal_stopword_transition_hand_calculation(self):
  _,t=extract('apple of banana',stopwords={'of'},policy=Policy(phrase_internal_transition=True))
  features={r['word']:r for r in t['features']};candidate=next(c for c in t['candidates'] if c['phrase']=='apple of banana')
  # Each neighboring transition has probability one; the internal stopword adds factor one and sum zero.
  a,b=features['apple']['H'],features['banana']['H'];self.assertAlmostEqual(candidate['H'],a*b/(1+a+b))

class TokenizerRegressionTests(unittest.TestCase):
 def test_segtok_embedded_whitespace_url_is_split_before_candidate_scoring(self):
  from replication.fidelity_core import policy_tokenize
  text='See http://en.wikipedia.org/wiki/TCP/IP_o\ntros_sobre_TCP/IP for more details.'
  sentences=policy_tokenize(text,Policy(tokenizer='segtok'))
  self.assertTrue(all(not any(c.isspace() for c in token) for sentence in sentences for token in sentence))
  predictions,trace=extract(text,policy=Policy(tokenizer='segtok'))
  self.assertTrue(all(math.isfinite(score) for phrase,score in predictions))

class EvidenceReaderRegressionTests(unittest.TestCase):
 def test_jsonl_unicode_separators_are_not_record_boundaries(self):
  import json,tempfile
  from pathlib import Path
  from fidelity_experiments import read_jsonl
  rows=[{'phrase':'datos\u0085de\u2028redes\u2029'}, {'phrase':'segunda línea'}]
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder)/'predictions.jsonl';p.write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n')
   self.assertEqual(read_jsonl(p),rows)
