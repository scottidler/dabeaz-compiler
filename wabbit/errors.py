# errors.py
#
# Compiler error handling support.
#
# One of the most important (and annoying) parts of writing a compiler
# is reliable reporting of error messages back to the user.  This file
# should consolidate some basic error handling functionality in one
# place.  Make it easy to report errors.  Make it easy to find out
# if errors have occurred.
#
# I suggest making a unified error() function that is responsible for
# all error reporting.

from wabbit.model import Node
from dataclasses import dataclass

@dataclass
class WabbitError():
    msg: str
    node: Node
    filename: str = None
    lineno: int = None

class NameLookupError(WabbitError):
    pass

class SyntaxError(WabbitError):
    pass

class DefineError(WabbitError):
    pass

class TypeResolveError(WabbitError):
    pass
