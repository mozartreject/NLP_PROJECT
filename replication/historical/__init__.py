"""Isolated loaders for hash-verified upstream code; original sources stay unmodified."""
import importlib.util,sys,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'.cache/fidelity_sources'
def load_yake(version):
    alias='historical_yake_'+version.replace('.','_');folder=CACHE/('yake-'+version)/'yake'
    if alias not in sys.modules:
        package=types.ModuleType(alias);package.__path__=[str(folder)];sys.modules[alias]=package
        spec=importlib.util.spec_from_file_location(alias+'.datarepresentation',folder/'datarepresentation.py')
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        main=types.ModuleType(alias+'.yake');main.__file__=str(folder/'yake.py');sys.modules[main.__name__]=main
        source=(folder/'yake.py').read_text().replace('from yake.datarepresentation import DataCore',f'from {alias}.datarepresentation import DataCore')
        exec(compile(source,str(folder/'yake.py'),'exec'),main.__dict__)
    return sys.modules[alias+'.yake'].KeywordExtractor

def load_rake():
    spec=importlib.util.spec_from_file_location('historical_rake',CACHE/'rake_2018.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module.Rake
