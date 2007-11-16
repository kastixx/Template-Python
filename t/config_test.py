from template.config import Config
from template.test import TestCase, main
from template.util import Literal


class ConfigTest(TestCase):
  def testConfig(self):
    factory = Config

    # Parser:
    parser = factory.parser({ 'PRE_CHOMP': 1, 'INTERPOLATE': True })
    self.failUnless(parser)
    self.assertEquals(1, parser.PRE_CHOMP)
    self.failUnless(parser.INTERPOLATE)
    parser = factory.parser({ 'POST_CHOMP': 1 })
    self.failUnless(parser)
    self.assertEquals(1, parser.POST_CHOMP)

    # Provider:
    provider = factory.provider({ 'INCLUDE_PATH': 'here:there',
                                  'PARSER': parser })
    self.failUnless(provider)
    self.assertEquals(['here', 'there'], provider.INCLUDE_PATH)
    self.assertEquals(1, provider.PARSER.POST_CHOMP)
    provider = factory.provider({ 'INCLUDE_PATH': 'cat:mat',
                                  'ANYCASE': True,
                                  'INTERPOLATE': True })
    self.failUnless(provider)
    self.assertEquals(['cat', 'mat'], provider.INCLUDE_PATH)
    # Force the provider to instantiate a parser and check it uses the
    # correct parameters.
    text = 'The cat sat on the mat'
    self.failUnless(provider.fetch(Literal(text)))
    self.failUnless(provider.PARSER.ANYCASE)
    self.failUnless(provider.PARSER.INTERPOLATE)

    # Plugins:
    plugins = factory.plugins({ 'PLUGIN_BASE': ('my.plugins', 'MyPlugins') })
    self.failUnless(plugins)
    self.assertEquals([('my.plugins', 'MyPlugins'), 'template.plugin'],
                      plugins.PLUGIN_BASE)
    plugins = factory.plugins({ 'LOAD_PYTHON': True,
                                'PLUGIN_BASE': ('my.plugins', 'NewPlugins') })
    self.failUnless(plugins)
    self.failUnless(plugins.LOAD_PYTHON)
    self.assertEquals([('my.plugins', 'NewPlugins'), 'template.plugin'],
                      plugins.PLUGIN_BASE)

    # Filters:
    filters = factory.filters({ 'TOLERANT': True })
    self.failUnless(filters)
    self.failUnless(filters.TOLERANT)
    filters = factory.filters({ 'TOLERANT': True })
    self.failUnless(filters)
    self.failUnless(filters.TOLERANT)

    # Stash:
    stash = factory.stash({ 'foo': 10, 'bar': 20 })
    self.failUnless(stash)
    self.assertEquals(10, stash.get('foo').value())
    self.assertEquals(20, stash.get('bar').value())
    stash = factory.stash({ 'foo': 30, 'bar': lambda *_: 'forty' })
    self.failUnless(stash)
    self.assertEquals(30, stash.get('foo').value())
    self.assertEquals('forty', stash.get('bar').value())

    # Context:
    context = factory.context({})
    self.failUnless(context)
    context = factory.context({ 'INCLUDE_PATH': 'anywhere' })
    self.failUnless(context)
    self.assertEquals('anywhere', context.LOAD_TEMPLATES[0].INCLUDE_PATH[0])
    context = factory.context({ 'LOAD_TEMPLATES': [ provider ],
                                'LOAD_PLUGINS': [ plugins ],
                                'LOAD_FILTERS': [ filters ],
                                'STASH': stash })
    self.failUnless(context)
    self.assertEquals(30, context.stash().get('foo').value())
    self.failUnless(context.LOAD_TEMPLATES[0].PARSER.INTERPOLATE)
    self.failUnless(context.LOAD_PLUGINS[0].LOAD_PYTHON)
    self.failUnless(context.LOAD_FILTERS[0].TOLERANT)

    # Service:
    service = factory.service({ 'INCLUDE_PATH': 'amsterdam' })
    self.failUnless(service)
    self.assertEquals(['amsterdam'],
                      service.context().LOAD_TEMPLATES[0].INCLUDE_PATH)

    # Iterator:
    iterator = factory.iterator(['foo', 'bar', 'baz'])
    self.failUnless(iterator)
    self.assertEquals('foo', iterator.get_first())
    self.assertEquals('bar', iterator.get_next())
    self.assertEquals('baz', iterator.get_next())

    # Instdir:
    # (later)


main()
