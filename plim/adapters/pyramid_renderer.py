import copy
try:
    from pyramid_mako import MakoRendererFactory
    from pyramid_mako import parse_options_from_settings
    from pyramid_mako import PkgResourceTemplateLookup
except ImportError:
    raise NotImplementedError(
        "It seems that you are trying to integrate Plim with Pyramid. "
        "To do so, please install Pyramid>=1.5 and pyramid_mako>=0.3.1 template bindings."
    )


def add_plim_renderer(config, extension, mako_settings_prefix='mako.'):
    """
    Register a Plim renderer for a template extension.

    This function is available on the Pyramid configurator after
    including the package:

    .. code-block:: python

        config.add_plim_renderer('.plim', mako_settings_prefix='mako.')

    The renderer will load its configuration from a provided mako prefix in the Pyramid
    settings dictionary. The default prefix is 'mako.'.

    :param config: Pyramid Config instance
    :param extension: renderer file extension
    :type extension: str
    :param mako_settings_prefix: prefix of mako configuration options.
    :type mako_settings_prefix: str
    """
    renderer_factory = MakoRendererFactory()
    config.add_renderer(extension, renderer_factory)

    def register():
        settings = copy.copy(config.registry.settings)
        settings['{prefix}preprocessor'.format(prefix=mako_settings_prefix)] = 'plim.preprocessor'

        opts = parse_options_from_settings(settings, mako_settings_prefix, config.maybe_dotted)
        lookup = PkgResourceTemplateLookup(**opts)

        renderer_factory.lookup = lookup

    # read about config.action() at
    # http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/extconfig.html#using-config-action-in-a-directive
    config.action(('plim-renderer', extension), register)


def includeme(config):
    """
    Set up standard configurator registrations. Use via:

    .. code-block:: python

        config = Configurator()
        config.include('pyramid_mako')

    Once this function has been invoked, the ``.plim`` renderer
    is available for use in Pyramid. This can be overridden and more may be
    added via the ``config.add_plim_renderer`` directive.
    """
    config.add_directive('add_plim_renderer', add_plim_renderer)
    config.add_plim_renderer('.plim')
