from pyramid import mako_templating
from plim import preprocessor



def includeme(config):
    config.add_renderer(
        config.get_settings().get('plim.file_extension', '.plm'),
        MakoPlimRenderer
    )


class MakoPlimRenderer(object):
    def __init__(self, info):
        info.settings['mako.preprocessor'] = preprocessor
        self.makoRenderer = mako_templating.renderer_factory(info)

    def __call__(self, value, system):
        return self.makoRenderer(value, system)
