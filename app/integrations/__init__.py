# shim package to expose top-level `integrations` modules under `app.integrations`
# This keeps imports like `from app.integrations import gemini_api` working while
# the real integration modules live in the repo-level `integrations/` folder.

from importlib import import_module
from types import ModuleType
import sys

# Map of available integration module names to their package path
_integration_names = [
    'calendar_api',
    'docs_api',
    'drive_api',
    'gemini_api',
    'oauth',
    'translate_api',
    'vertex_ai',
]

# Dynamically import each integration module from the top-level `integrations` package
for name in _integration_names:
    mod = import_module(f'integrations.{name}')
    # expose as attribute in this package
    globals()[name] = mod
    # also set sys.modules entry so `from app.integrations import gemini_api` works
    sys.modules[f'app.integrations.{name}'] = mod

# Optionally export names
__all__ = _integration_names
