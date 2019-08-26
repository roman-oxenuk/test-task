
class BaseConfig:
    MONGO_URI = 'mongodb://db:27017/test'


class TestingConfig(BaseConfig):
    MONGO_URI = 'mongodb://db:27017/test_test'
    LOGIN_DISABLED = True
