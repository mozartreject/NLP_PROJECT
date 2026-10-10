import unittest
from full_comparison import load_model,rake,score,load_dataset
from replication.core import Config,extract
import pke

class FullComparisonTests(unittest.TestCase):
    def test_rake_hand_calculation(self):
        result=rake('apple banana. apple banana.',set())
        self.assertEqual(result,[('apple banana',4.)])
    def test_rake_discards_long_phrases_before_counts(self):
        self.assertEqual(rake('apple banana cherry date.',set()),[])
    def test_spanish_stopword_policy(self):
        result,_=extract('de datos',Config(),stopwords={'de'})
        self.assertFalse(any(p=='de' or p.startswith('de ') for p,s in result))
    def test_fast_mode_preserves_keywords(self):
        text='NASA studies stars. Bright stars reveal galaxies and distant worlds.'
        self.assertEqual(extract(text)[0],extract(text,collect_trace=False)[0])
    def test_common_pos_candidates(self):
        model=load_model(pke.unsupervised.TfIdf,[[('bright','ADJ'),('stars','NOUN'),('shine','VERB')]],'en',set())
        self.assertIn('bright stars',model.candidates)
        self.assertNotIn('shine',model.candidates)
        self.assertNotIn('stars shine',model.candidates)
    def test_tfidf_explicit_corpus_statistics(self):
        model=load_model(pke.unsupervised.TfIdf,[[('apple','NOUN'),('apple','NOUN')]],'en',set())
        model.candidate_weighting(df={'--NB_DOC--':3,'apple':1,'apple apple':1})
        self.assertAlmostEqual(model.weights['apple'],2.)
    def test_empty_predictions_not_dropped(self):
        self.assertEqual(score([],{'apple'}),(0.,0.,0.))
    def test_four_dataset_counts_and_ids(self):
        for name,count in [('500N-KPCrowd',500),('SemEval2010',243),('Schutz2008',1231),('WICC',1640)]:
            rows,digest,lang=load_dataset(name)
            self.assertEqual(len(rows),count)
            self.assertEqual(len({r[0] for r in rows}),count)
            self.assertEqual(len(digest),64)

if __name__=='__main__':unittest.main()
