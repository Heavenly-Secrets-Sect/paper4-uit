import importlib.util, sys
def load(path, name='paper4.ext_gate_cand'):
    import paper4
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); mod.__package__ = 'paper4'
    sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod
