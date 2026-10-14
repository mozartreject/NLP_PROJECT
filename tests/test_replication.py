import math
import unittest
from replication.core import Config, extract, similarity
from scripts.full_comparison import score as metrics

class ReplicationTests(unittest.TestCase):
    def test_hand_computed_single_term(self):
        predictions,trace=extract('apple')
        term=trace['features'][0]
        position=math.log2(math.log2(3))
        self.assertAlmostEqual(term['H'],position/2)
        self.assertAlmostEqual(predictions[0][1],term['H']/(1+term['H']))
    def test_counts_and_boundaries(self):
        _,trace=extract('apple banana. apple banana!')
        counts={r['phrase']:r['tf'] for r in trace['candidates']}
        self.assertEqual(counts['apple banana'],2)
        self.assertNotIn('banana apple',counts)
        self.assertEqual(trace['features'][0]['sentence_ids'],[1,2])
    def test_casing_excludes_sentence_start(self):
        _,trace=extract('Apple meets Apple. Apple meets NASA.')
        terms={r['word']:r for r in trace['features']}
        self.assertEqual(terms['apple']['capital'],1)
        self.assertEqual(terms['nasa']['acronym'],1)
    def test_dedup_distance(self):
        self.assertAlmostEqual(similarity('apple','apples'),5/6)
        self.assertEqual(similarity('',''),1)
        self.assertEqual(similarity('abc','xyz'),0)
    def test_empty_stopwords_determinism(self):
        self.assertEqual(extract('')[0],[])
        self.assertEqual(extract('the and of')[0],[])
        self.assertEqual(extract('apple banana apple'),extract('apple banana apple'))
    def test_precision_unfilled_slots_and_duplicates(self):
        self.assertEqual(metrics(['Apple','apple'],{'apple'},10),(0.1,1.,2*.1/1.1))
    def test_invalid_configuration(self):
        with self.assertRaises(ValueError): Config(top_k=0)
    def test_scores_finite(self):
        for feature in [None,'WCase','WPosition','WFreq','WRel','WSpread']:
            predictions,trace=extract('NASA studies stars. Bright stars reveal galaxies.',omit=feature)
            self.assertTrue(all(math.isfinite(r['H']) and r['H']>0 for r in trace['features']))

if __name__=='__main__': unittest.main()
