"""
Tests for the configuration module.
"""

import pytest
import os
from unittest.mock import patch, mock_open

from src.config import (
    load_config_from_env,
    load_config_from_ini,
    merge_configurations,
    validate_config,
    ApplicationConfig,
    DatabaseConfig,
    LLMConfig,
    BotConfig,
    ValidationConfig,
    LoggingConfig
)


class TestConfigLoading:
    """Test configuration loading from different sources"""

    def test_load_config_from_env(self):
        """Test loading configuration from environment variables"""
        with patch.dict(os.environ, {
            'DB_HOST': 'test_host',
            'DB_PORT': '1234',
            'DB_NAME': 'test_db',
            'DB_USER': 'test_user',
            'DB_PASSWORD': 'test_pass',
            'LLM_API_KEY': 'test_api_key',
            'TELEGRAM_BOT_TOKEN': 'test_bot_token',
            'LOG_DIR': '/test/logs'
        }):
            config = load_config_from_env()
            
            assert config['database']['host'] == 'test_host'
            assert config['database']['port'] == 1234
            assert config['database']['name'] == 'test_db'
            assert config['database']['user'] == 'test_user'
            assert config['database']['password'] == 'test_pass'
            assert config['llm']['api_key'] == 'test_api_key'
            assert config['bot']['token'] == 'test_bot_token'
            assert config['logging']['log_dir'] == '/test/logs'

    def test_load_config_from_ini(self):
        """Test loading configuration from INI file"""
        ini_content = """
[Database]
DB_HOST = test_host
DB_PORT = 1234
DB_NAME = test_db
DB_USER = test_user

[LLM]
LLM_API_URL = https://test.ai/api/v1
LLM_MODEL_NAME = test-model

[Validation]
ITALIAN_CHARACTERS = abcdefghil .,;:!

[Logging]
LOG_DIR = /test/logs
"""
        
        with patch('builtins.open', mock_open(read_data=ini_content)):
            with patch('os.path.exists', return_value=True):
                config = load_config_from_ini('test.ini')
            
            assert config['database']['host'] == 'test_host'
            assert config['database']['port'] == 1234
            assert config['database']['name'] == 'test_db'
            assert config['database']['user'] == 'test_user'
            assert config['llm']['api_url'] == 'https://test.ai/api/v1'
            assert config['llm']['model_name'] == 'test-model'
            assert config['validation']['italian_characters'] == set('abcdefghil .,;:!')
            assert config['logging']['log_dir'] == '/test/logs'

    def test_merge_configurations(self):
        """Test merging environment and INI configurations"""
        env_config = {
            'database': {
                'host': 'env_host',
                'password': 'env_password'
            },
            'llm': {
                'api_key': 'env_api_key'
            },
            'bot': {
                'token': 'env_token'
            },
            'logging': {
                'log_dir': '/env/logs'
            }
        }
        
        ini_config = {
            'database': {
                'host': 'ini_host',
                'port': 1234,
                'name': 'ini_db',
                'user': 'ini_user'
            },
            'llm': {
                'api_url': 'https://ini.ai/api/v1',
                'model_name': 'ini-model'
            },
            'validation': {
                'italian_characters': set('abcdefghil')
            }
        }
        
        merged = merge_configurations(env_config, ini_config)
        
        # Environment variables should take precedence
        assert merged['database']['host'] == 'env_host'
        assert merged['database']['password'] == 'env_password'
        assert merged['llm']['api_key'] == 'env_api_key'
        assert merged['bot']['token'] == 'env_token'
        assert merged['logging']['log_dir'] == '/env/logs'
        
        # INI values should be used when not in environment
        assert merged['database']['port'] == 1234
        assert merged['database']['name'] == 'ini_db'
        assert merged['database']['user'] == 'ini_user'
        assert merged['llm']['api_url'] == 'https://ini.ai/api/v1'
        assert merged['llm']['model_name'] == 'ini-model'
        assert merged['validation']['italian_characters'] == set('abcdefghil')


class TestConfigValidation:
    """Test configuration validation with pydantic models"""

    def test_database_config_validation(self):
        """Test database configuration validation"""
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            name='test_db',
            user='test_user',
            password='test_password'
        )
        
        assert config.host == 'localhost'
        assert config.port == 5432
        assert config.name == 'test_db'
        assert config.user == 'test_user'
        assert config.password == 'test_password'

    def test_database_config_validation_invalid_port(self):
        """Test database configuration validation with invalid port"""
        with pytest.raises(ValueError):
            DatabaseConfig(
                host='localhost',
                port=70000,  # Invalid port
                name='test_db',
                user='test_user',
                password='test_password'
            )

    def test_llm_config_validation(self):
        """Test LLM configuration validation"""
        config = LLMConfig(
            api_url='https://test.ai/api/v1',
            api_key='test_api_key',
            model_name='test-model'
        )
        
        assert config.api_url == 'https://test.ai/api/v1'
        assert config.api_key == 'test_api_key'
        assert config.model_name == 'test-model'

    def test_bot_config_validation(self):
        """Test bot configuration validation"""
        config = BotConfig(token='test_bot_token')
        assert config.token == 'test_bot_token'

    def test_validation_config_validation(self):
        """Test validation configuration validation"""
        config = ValidationConfig(italian_characters=set('abcdefghil .,;:!'))
        assert config.italian_characters == set('abcdefghil .,;:!')

    def test_logging_config_validation(self):
        """Test logging configuration validation"""
        config = LoggingConfig(log_dir='/test/logs')
        assert config.log_dir == '/test/logs'

    def test_application_config_validation(self):
        """Test full application configuration validation"""
        config = ApplicationConfig(
            database=DatabaseConfig(
                host='localhost',
                port=5432,
                name='parla_italiano',
                user='parla_user',
                password='parla_password'
            ),
            llm=LLMConfig(
                api_url='https://openrouter.ai/api/v1',
                api_key='test_api_key',
                model_name='qwen/qwen3-235b-a22b:free'
            ),
            bot=BotConfig(token='test_bot_token'),
            validation=ValidationConfig(italian_characters=set('abcdefghiklmnopqrstuvzàèéìíîòóùú .,;:!?\'-')),
            logging=LoggingConfig(log_dir='./logs')
        )
        
        assert config.database.host == 'localhost'
        assert config.llm.api_url == 'https://openrouter.ai/api/v1'
        assert config.bot.token == 'test_bot_token'
        assert len(config.validation.italian_characters) > 0
        assert config.logging.log_dir == './logs'


def test_config_singleton():
    """Test that get_config returns the same instance"""
    from src.config import get_config
    
    config1 = get_config()
    config2 = get_config()
    
    assert config1 is config2


def test_convenience_functions():
    """Test convenience functions for accessing configuration"""
    from src.config import (
        get_database_config, get_llm_config, get_bot_config,
        get_validation_config, get_logging_config
    )
    
    # These should not raise exceptions if configuration is loaded
    db_config = get_database_config()
    llm_config = get_llm_config()
    bot_config = get_bot_config()
    validation_config = get_validation_config()
    logging_config = get_logging_config()
    
    assert isinstance(db_config, DatabaseConfig)
    assert isinstance(llm_config, LLMConfig)
    assert isinstance(bot_config, BotConfig)
    assert isinstance(validation_config, ValidationConfig)
    assert isinstance(logging_config, LoggingConfig)