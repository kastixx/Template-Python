#
#  The Template-Python distribution is Copyright (C) Sean McAfee 2007-2008,
#  derived from the Perl Template Toolkit Copyright (C) 1996-2007 Andy
#  Wardley.  All Rights Reserved.
#
#  The file "LICENSE" at the top level of this source distribution describes
#  the terms under which this file may be distributed.
#

from io import StringIO
import os
import re
import tempfile

from template import util
from template.iterator import Iterator
from template.constants import *
from template.util import TemplateException


"""
template.document.Document - Compiled template document object


SYNOPSIS

    import template.document

    doc = template.document.Document({
	'BLOCK': lambda: some_text(),
	'DEFBLOCKS': {
	    'header': lambda: some_more_text(),
	    'footer': lambda: yet_more_text(),
	},
	'METADATA': {
	    'author': 'Andy Wardley',
	    'version': 3.14,
	}
    })

    print doc.process(context)


DESCRIPTION

This module defines an object class whose instances represent compiled
template documents.  The template.parser.Parser class creates a
template.document.ocument instance to encapsulate a template as it is
compiled into Python code.

The constructor expects a reference to a dictionary containing the
BLOCK, DEFBLOCKS and METADATA items.  The BLOCK item should contain a
Python callable or a textual representation of Python code, as
generated by the template.parser.Parser class, which is then evaluated
into a subroutine.  The DEFLOCKS item should reference a dictionary
containing further named BLOCKs which may be defined in the template.
The keys represent BLOCK names and the values should be callables or
text strings of Python code as per the main BLOCK item.  The METADATA
item should reference a dictionary of metadata items relevant to the
document.

The process() method can then be called on the instantiated Document
object, passing a reference to a template.context.Content object as
the first parameter.  This will install any locally defined blocks
(DEFBLOCKS) in the the contexts() BLOCKS cache (via a call to visit())
so that they may be subsequently resolved by the context.  The main
BLOCK subroutine is then executed, passing the context on as a
parameter.  The text returned from the template subroutine is then
returned by the process() method, after calling the context leave()
method to permit cleanup and de-registration of named BLOCKS
previously installed.

A __getattr__ method provides access to the METADATA items for the
document.  The template.service.Service class installs a the main
template.document.Document object in the stash as the 'template'
variable.  This allows metadata items to be accessed from within
templates, including PRE_PROCESS templates.

header:

    <html>
    <head>
    <title>[% template.title %]
    </head>
    ...

Document objects are usually created by the template.parser.Parser
class but can be manually instantiated or sub-classed to provide
custom template components.


INSTANCE METHODS

__init__(config)

Constructor method which accept a dictionary containing the structure
as shown in this example:

    doc = template.document.Document({
	'BLOCK': lambda: some_text(),
	'DEFBLOCKS': {
	    'header': lambda: more_text(),
	    'footer': lambda: yet_more_text(),
	},
	'METADATA': {
	    'author': 'Andy Wardley',
	    'version': 3.14,
	}
    })

BLOCK and DEFBLOCKS items may be expressed as references to Python
subroutines or as text strings containing Python subroutine
definitions, as is generated by the template.parser.Parser class.

process(context)

Main processing routine for the compiled template document.  A
template.context.Context object should be passed as the first
parameter.  The method installs any locally defined blocks via a call
to the context visit() method, processes its own template, passing
the context reference by parameter and then calls leave() in the
context to allow cleanup.

    print doc.process(context)

Returns a text string representing the generated output for the template.

block()

Returns a reference to the main BLOCK subroutine.

blocks()

Returns a reference to the hash array of named DEFBLOCKS subroutines.


CLASS METHODS

write_python_file(config)

This class method is provided to effect persistence of compiled
templates.  If the COMPILE_EXT option is set (to indicate a file
extension for saving compiled templates) then the
template.parser.Parser object calls this subroutine before
instantiating an object.  At this stage, the parser has a
representation of the template as text strings containing Python code.
We can write that to a file, enclosed in a small wrapper which will
allow us to susequently load the file and have Python parse and
compile it into a Document.  Thus we have persistence of compiled
templates.

"""

class Error(Exception):
  """A trivial local exception class."""
  pass


class Document:
  """Module defining a class of objects which encapsulate compiled
  templates, storing additional block definitions and metadata as well
  as the compiled Python functions representing the main template
  content.
  """
  def __init__(self, doc):
    #evaluate Python code in block to create sub-routine reference if necessary
    self.__block = self.__compile(doc.get("BLOCK"))

    # same for any additional BLOCK definitions
    self.__defblocks = {}
    for name, block in doc.get("DEFBLOCKS", {}).items():
      self.__defblocks[name] = self.__compile(block)

    self.__meta = doc.get("METADATA", {}).copy()
    self.__hot = False

  def __compile(self, block, debug=False):
    if callable(block):
      return block
    if debug:
      print(block)
    return self.evaluate(block)

  def __getattr__(self, name):
    if name and name[0].islower():
      return self.__meta.get(name)
    else:
      raise AttributeError

  def block(self):
    """Returns a reference to the internal sub-routine reference
    that constitutes the main document template.
    """
    return self.__block

  def blocks(self):
    """Returns a reference to a dictionary containing any BLOCK
    definitions from the template.  The dictionary keys are the BLOCK
    names and the values are references to template.document.Document
    objects.
    """
    return self.__defblocks

  def process(self, context):
    """Process the document in a particular context.  Checks for recursion,
    registers the document with the context via visit(), processes itself,
    and then unwinds with a large gin and tonic.
    """
    if self.__hot and not context.recursion():
      return context.throw(ERROR_FILE, "recursion into '%s'" % self.name)
    context.visit(self, self.__defblocks)
    self.__hot = True
    try:
      try:
        return self.__block(context)
      except TemplateException as e:
        raise context.catch(e)
    finally:
      self.__hot = False
      context.leave()

  @classmethod
  def evaluate(cls, block, name="block"):
    """Evaluates a given block of Python code in a namespace providing
    all of the named objects that might be needed by code generated by
    the template.directive module.

    Returns the namespace entry with the given name after evaluating the
    block.  The default name is 'block'.
    """
    namespace = PYEVAL_NAMESPACE.copy()
    exec(block, namespace)
    return namespace.get(name)

  @classmethod
  def evaluate_file(cls, path, name="document"):
    """Evaluates a given file of Python code in a namespace providing
    all of the named objects that might be needed by code generated by
    the template.directive module.

    Returns the namespace entry with the given name after evaluating the
    file.  The default name is 'document'.
    """
    namespace = PYEVAL_NAMESPACE.copy()
    exec(path, namespace)
    return namespace.get(name)

  @classmethod
  def write_python_file(cls, path, content):
    """Writes a representation of the compiled template 'content' to the
    named file.
    """
    if not path:
      raise Error("invalid null filename")
    tmpfh, tmppath = tempfile.mkstemp(dir=os.path.dirname(path))
    try:
      tmpfile = None
      try:
        tmpfile = os.fdopen(tmpfh, "w")
        write_python_doc(tmpfile,
                         content.get("METADATA"),
                         content.get("DEFBLOCKS", {}),
                         content["BLOCK"])
      finally:
        if tmpfile:
          tmpfile.close()
    except:
      os.remove(tmppath)
      raise
    else:
      os.rename(tmppath, path)


def write_python_doc(fh, metadata, defblocks, block):
  """Writes a representation of a compiled template--its metadata, defined
  blocks, and primary block--to the given file handle.
  """
  fh.write("# Compiled template generated by the Template Toolkit\n\n")
  fh.write("metadata = %r\n\n" % metadata)
  fh.write("blocks = {}\n\n")
  for name, code in sorted(defblocks.items()):
    fh.write(code)
    fh.write("\nblocks[%r] = block\n\n" % name)
  fh.write(block)
  fh.write("\ndocument = Document({'METADATA': metadata, "
           "'DEFBLOCKS': blocks, 'BLOCK': block})\n")



# A dictionary of named objects that may be required by Python code
# generated by the this module.

PYEVAL_NAMESPACE = {
  "scalar":    util.PerlScalar,
  "Buffer":    util.StringBuffer,
  "Error":     TemplateException,
  "Iterator":  Iterator.Create,
  "Regex":     re.compile,
  "List":      util.ScalarList,
  "Dict":      util.ScalarDictionary,
  "Switch":    util.SwitchList,
  "Concat":    util.Concatenate,
  "Continue":  util.Continue,
  "Break":     util.Break,
  "Evaluate":  util.EvaluateCode,
  "Document":  Document,
}
