from typing import Text


def import_from_path(module_path: Text):
    import importlib
    if "." in module_path:
        module_name, _, class_name = module_path.rpartition(".")
        m = importlib.import_module(module_name)
        return getattr(m, class_name)
    else:
        module = globals().get(module_path, locals().get(module_path))
        if module is not None:
            return module
        else:
            raise ImportError(f"Cannot retrieve class from path {module_path}.")
