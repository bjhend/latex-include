
# Dynamic type checking with beartype
from beartype.claw import beartype_this_package
beartype_this_package()
# Don't export beartype_this_package
del beartype_this_package


from .main import latexIncludeFiles, latexInclude

