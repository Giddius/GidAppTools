

from gidapptools.abstract_classes import AbstractMetaFactory, AbstractMetaItem


class FakeMetaItem(AbstractMetaItem):
    pass


class FakeFactory(AbstractMetaFactory):
    default_configuration = {'fake_kwarg': 'fake_kwarg_string'}
    product_class = FakeMetaItem

    def setup(self) -> None:
        self.is_setup = True

    def _build(self) -> None:
        print('building')


DEFAULT_CONFIGURATION = {'fake_runtime_kwarg': 13}


def register(app_meta):
    app_meta.register(FakeFactory, default_configuration=DEFAULT_CONFIGURATION)
