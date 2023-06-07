from smarterbombing import configuration

TEST_PREFIX = 'test-'

def test_configuration_load():
    config = configuration.load(name_prefix=TEST_PREFIX)
    assert config is None

    default_config = configuration.create_default()

    config = configuration.load(create_if_missing=True, name_prefix=TEST_PREFIX)
    assert config == default_config

    configuration.delete(name_prefix=TEST_PREFIX)


def test_configuration_save():
    save_config = {
        'test1': 'test1',
        'test2': 2,
        'test3': [ 1, 2, 'three'],
        'test4': {
            '1': 1,
            '2': 'two',
        },
    }

    configuration.save(save_config, name_prefix=TEST_PREFIX)
    config = configuration.load(name_prefix=TEST_PREFIX)

    assert config == save_config

    configuration.delete(name_prefix=TEST_PREFIX)
