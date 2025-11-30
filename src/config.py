"""
Configuration management module for Parla Italiano Bot.

This module provides centralized configuration loading and validation
using pydantic models. It separates sensitive data (stored in .env)
from non-sensitive configuration (stored in config.ini).
"""

import os
import configparser
from typing import Set
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig(BaseModel):
    """Database configuration"""
    host: str = Field(..., description="Database host")
    port: int = Field(..., ge=1, le=65535, description="Database port")
    name: str = Field(..., description="Database name")
    user: str = Field(..., description="Database user")
    password: str = Field(..., description="Database password")

    model_config = {'env_prefix': 'DB_'}


class LLMConfig(BaseModel):
    """LLM (Language Model) configuration"""
    api_url: str = Field(..., description="LLM API base URL")
    api_key: str = Field(..., description="LLM API key")
    model_name: str = Field(..., description="LLM model identifier")


class BotConfig(BaseModel):
    """Telegram Bot configuration"""
    token: str = Field(..., description="Telegram bot token")


class ValidationConfig(BaseModel):
    """Validation configuration"""
    italian_characters: Set[str] = Field(..., description="Valid Italian characters for sentence validation")
    russian_characters: Set[str] = Field(..., description="Valid Russian characters for sentence validation")


class LoggingConfig(BaseModel):
    """Logging configuration"""
    log_dir: str = Field(..., description="Log directory path")


class ApplicationConfig(BaseModel):
    """Main application configuration"""
    database: DatabaseConfig
    llm: LLMConfig
    bot: BotConfig
    validation: ValidationConfig
    logging: LoggingConfig = LoggingConfig(log_dir='./logs')


def load_config_from_env():
    """Load configuration from environment variables"""
    return {
        'database': {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'name': os.getenv('DB_NAME', 'parla_italiano'),
            'user': os.getenv('DB_USER', 'parla_user'),
            'password': os.getenv('DB_PASSWORD', '')
        },
        'llm': {
            'api_key': os.getenv('LLM_API_KEY', '')
        },
        'bot': {
            'token': os.getenv('TELEGRAM_BOT_TOKEN', '')
        },
        'logging': {
            'log_dir': os.getenv('LOG_DIR', './logs')
        }
    }


def load_config_from_ini(config_file: str = 'config.ini') -> dict:
    """Load configuration from INI file"""
    config = configparser.ConfigParser()
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file {config_file} not found")
    
    config.read(config_file)
    
    ini_config = {}
    
    # Load database configuration
    if 'Database' in config:
        ini_config['database'] = {
            'host': config['Database'].get('DB_HOST', 'localhost'),
            'port': int(config['Database'].get('DB_PORT', 5432)),
            'name': config['Database'].get('DB_NAME', 'parla_italiano'),
            'user': config['Database'].get('DB_USER', 'parla_user')
        }
    
    # Load LLM configuration  
    if 'LLM' in config:
        ini_config['llm'] = {
            'api_url': config['LLM'].get('LLM_API_URL', 'https://openrouter.ai/api/v1'),
            'model_name': config['LLM'].get('LLM_MODEL_NAME', 'qwen/qwen3-235b-a22b:free')
        }
    
    # Load validation configuration
    if 'Validation' in config:
        italian_chars_str = config['Validation'].get('ITALIAN_CHARACTERS',
                                                   'abcdefghiklmnopqrstuvzàèéìíîòóùú .,;:!?\'-—')
        russian_chars_str = config['Validation'].get('RUSSIAN_CHARACTERS',
                                                   'абвгдеёжзийклмнопрстуфхцчшщъыьэюя .,;:!?\'-—')
        ini_config['validation'] = {
            'italian_characters': set(italian_chars_str),
            'russian_characters': set(russian_chars_str)
        }
    
    # Load logging configuration
    if 'Logging' in config:
        ini_config['logging'] = {
            'log_dir': config['Logging'].get('LOG_DIR', './logs')
        }
    
    return ini_config


def merge_configurations(env_config: dict, ini_config: dict) -> dict:
    """Merge environment and INI configurations"""
    merged = {}
    
    # Merge database config
    merged['database'] = {**ini_config.get('database', {}), **env_config.get('database', {})}
    
    # Merge LLM config
    merged['llm'] = {**ini_config.get('llm', {}), **env_config.get('llm', {})}
    
    # Merge bot config
    merged['bot'] = env_config.get('bot', {})
    
    # Add validation config from INI
    if 'validation' in ini_config:
        merged['validation'] = ini_config['validation']
    
    # Add logging config (prefer env, fallback to ini)
    if 'logging' in env_config:
        merged['logging'] = env_config['logging']
    elif 'logging' in ini_config:
        merged['logging'] = ini_config['logging']
    
    return merged


def validate_config(config_dict: dict) -> ApplicationConfig:
    """Validate and create ApplicationConfig from dictionary"""
    return ApplicationConfig(**config_dict)


def load_application_config(config_file: str = 'config.ini') -> ApplicationConfig:
    """
    Load and validate application configuration from both environment variables and INI file.
    
    Environment variables take precedence over INI file values.
    Returns a validated ApplicationConfig instance.
    """
    # Load configurations from different sources
    env_config = load_config_from_env()
    ini_config = load_config_from_ini(config_file)
    
    # Merge configurations (env takes precedence)
    merged_config = merge_configurations(env_config, ini_config)
    
    # Validate and return ApplicationConfig
    return validate_config(merged_config)


def get_config() -> ApplicationConfig:
    """
    Get the singleton application configuration instance.
    This function can be called throughout the application to access configuration.
    """
    if not hasattr(get_config, '_instance'):
        get_config._instance = load_application_config()
    return get_config._instance


# Convenience functions for accessing specific configuration sections
def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return get_config().database


def get_llm_config() -> LLMConfig:
    """Get LLM configuration"""
    return get_config().llm


def get_database_config() -> DatabaseConfig:
    """Get database configuration"""
    return get_config().database


def get_bot_config() -> BotConfig:
    """Get bot configuration"""
    return get_config().bot


def get_validation_config() -> ValidationConfig:
    """Get validation configuration"""
    return get_config().validation


def get_logging_config() -> LoggingConfig:
    """Get logging configuration"""
    return get_config().logging