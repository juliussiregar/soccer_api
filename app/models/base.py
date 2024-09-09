from sqlalchemy.ext.declarative import declarative_base

import importlib
import pkgutil
import app.models

Base = declarative_base()
metadata = Base.metadata

# Dynamically import all modules in the models package, except for base
for _, name, _ in pkgutil.iter_modules(app.models.__path__):
    if name != "base":
        importlib.import_module(f"app.models.{name}")
