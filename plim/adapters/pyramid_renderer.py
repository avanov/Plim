try:
    from pyramid.mako_templating import renderer_factory as mako_renderer_factory
except ImportError:
    # Looks like we have Pyramid 1.5a2+
    try:
        from pyramid_mako import renderer_factory as mako_renderer_factory
    except ImportError:
        raise NotImplementedError(
            "It seems that you are trying to integrate Plim with Pyramid-1.5a2 or higher. "
            "To do so, please install the pyramid_mako template bindings."
        )

from plim import preprocessor


def includeme(config):
    config.add_renderer(
        config.get_settings().get('plim.file_extension', '.plim'),
        MakoPlimRenderer
    )


class MakoPlimRenderer(object):
    def __init__(self, info):
        info.settings['mako.preprocessor'] = preprocessor
        self.makoRenderer = mako_renderer_factory(info)

    def __call__(self, value, system):
        return self.makoRenderer(value, system)
