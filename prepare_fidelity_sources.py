"""Recover pinned public artifacts with checksums; leave raw archives local."""
import hashlib,json,tarfile,urllib.request,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'.cache/fidelity_sources'
def download(url,path):
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True)
        with urllib.request.urlopen(url,timeout=60) as response:path.write_bytes(response.read())
    return path.read_bytes()
def sha(b):return hashlib.sha256(b).hexdigest()
def prepare():
    CACHE.mkdir(parents=True,exist_ok=True);manifest={}
    meta=json.loads(download('https://pypi.org/pypi/yake/json',CACHE/'pypi_yake.json'))
    for v in ['0.3.0','0.3.2']:
        file=next(f for f in meta['releases'][v] if f['packagetype']=='sdist')
        path=CACHE/file['filename'];content=download(file['url'],path)
        assert sha(content)==file['digests']['sha256'],'PyPI hash mismatch'
        with tarfile.open(path) as archive:
            for member in archive.getmembers():
                if not member.isfile():continue
                rel=Path(member.name)
                if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe archive path')
                target=CACHE/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(archive.extractfile(member).read())
        manifest['yake-'+v]={'url':file['url'],'sha256':sha(content),'upload_time':file['upload_time_iso_8601'],'runtime':'Current pinned dependencies; original dependency versions unknown'}
    commit='14e153aa9cb2c02456df3880cd5fd30f7ee3aa95'
    url=f'https://raw.githubusercontent.com/zelandiya/RAKE-tutorial/{commit}/rake.py'
    b=download(url,CACHE/'rake_2018.py')
    manifest['RAKE-2018']={'url':url,'commit':commit,'sha256':sha(b)}
    for lang in ['en','es']:
        url=f'https://raw.githubusercontent.com/INESCTEC/kep/ef7ed02ae931dce9e84f25c7b9d0b1bd84c0768a/kep/StopwordsList/stopwords_{lang}.txt'
        b=download(url,CACHE/f'kep_stopwords_{lang}.txt');manifest['KEP-stopwords-'+lang]={'url':url,'sha256':sha(b),'date':'2020; not verified ECIR 2018 stoplists'}
    url='https://raw.githubusercontent.com/zelandiya/RAKE-tutorial/'+commit+'/data/stoplists/SmartStoplist.txt'
    b=download(url,CACHE/'SmartStoplist.txt');manifest['RAKE-SmartStoplist']={'url':url,'sha256':sha(b)}
    url='https://raw.githubusercontent.com/zelandiya/keyword-extraction-datasets/master/SemEval2010-Maui.zip'
    content=download(url,CACHE/'SemEval2010-Maui.zip');manifest['alternate-SemEval']={'url':url,'sha256':sha(content)}
    with zipfile.ZipFile(ROOT/'data/SemEval2010.zip') as old,zipfile.ZipFile(CACHE/'SemEval2010-Maui.zip') as alt:
        a={Path(n).stem:n for n in old.namelist() if '/docsutf8/' in n and n.endswith('.txt')}
        b={Path(n).stem:n for n in alt.namelist() if n.endswith('.txt') and not n.startswith('__MACOSX/')}
        assert len(a)==243 and len(b)==244 and set(b)-set(a)=={'C-86'}
        def gold(z,p):return {' '.join(x.casefold().split()) for x in z.read(p).decode('utf-8-sig').splitlines() if x.strip()}
        text_match=sum(old.read(a[k]).decode('utf-8-sig').strip()==alt.read(b[k]).decode('utf-8-sig').strip() for k in a)
        gold_match=sum(gold(old,a[k].replace('/docsutf8/','/keys/')[:-4]+'.key')==gold(alt,b[k][:-4]+'.key') for k in a)
        assert text_match==243 and gold_match==243
        # Preserve all existing 243 inputs byte-for-byte; append only the recovered pair.
        target=ROOT/'data/SemEval2010-recovered244.zip'
        with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as out:
            for ident in sorted(b):
                text=old.read(a[ident]) if ident in a else alt.read(b[ident])
                keys=old.read(a[ident].replace('/docsutf8/','/keys/')[:-4]+'.key') if ident in a else alt.read(b[ident][:-4]+'.key')
                out.writestr('SemEval2010/docsutf8/'+ident+'.txt',text);out.writestr('SemEval2010/keys/'+ident+'.key',keys)
        manifest['SemEval-recovery']={'shared_texts_equal_after_outer_whitespace_strip':text_match,'shared_normalized_gold_sets_equal':gold_match,'recovered_id':'C-86','documents_text':244,'documents_with_nonempty_comparable_gold':243,'recovered_gold_empty':True,'recovered_text_sha256':sha(alt.read(b['C-86'])),'recovered_gold_sha256':sha(alt.read(b['C-86'][:-4]+'.key')),'combined_archive_sha256':sha(target.read_bytes()),'original_archive_sha256':sha((ROOT/'data/SemEval2010.zip').read_bytes()),'policy':'Original 243 byte streams retained; C-86 pair appended from alternate archive'}
    out=ROOT/'configs/fidelity_sources.json';out.write_text(json.dumps(manifest,indent=2)+'\n');print('Verified historical sources and recovered SemEval244:',out)
    return manifest
if __name__=='__main__':prepare()
