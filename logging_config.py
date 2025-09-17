# logging_config.py
import logging
import logging.config
import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class LoggingManager:
    """Centralized logging configuration manager for different environments."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development").lower()
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.app_name = os.getenv("APP_NAME", "google-sdk-agent")
        
    def get_log_config(self) -> Dict[str, Any]:
        """Get logging configuration based on environment."""
        
        if self.environment == "production":
            return self._get_production_config()
        elif self.environment == "staging":
            return self._get_staging_config()
        elif self.environment == "development":
            return self._get_development_config()
        else:
            return self._get_default_config()
    
    def _get_development_config(self) -> Dict[str, Any]:
        """Development logging: Console with colors and detailed formatting."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                },
                'colored': {
                    '()': 'colorlog.ColoredFormatter',
                    'format': '%(log_color)s%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                    'log_colors': {
                        'DEBUG': 'cyan',
                        'INFO': 'green',
                        'WARNING': 'yellow',
                        'ERROR': 'red',
                        'CRITICAL': 'red,bg_white',
                    }
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.log_level,
                    'formatter': 'colored',
                    'stream': sys.stdout
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'level': 'DEBUG',
                    'formatter': 'detailed',
                    'filename': f'logs/{self.app_name}_dev.log',
                    'mode': 'a',
                    'encoding': 'utf-8'
                }
            },
            'loggers': {
                self.app_name: {
                    'level': 'DEBUG',
                    'handlers': ['console', 'file'],
                    'propagate': False
                },
                'uvicorn': {
                    'level': 'INFO',
                    'handlers': ['console'],
                    'propagate': False
                },
                'fastapi': {
                    'level': 'INFO',
                    'handlers': ['console'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        }
    
    def _get_staging_config(self) -> Dict[str, Any]:
        """Staging logging: Console + file with JSON formatting."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'json': {
                    '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                    'format': '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s'
                },
                'standard': {
                    'format': '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'standard',
                    'stream': sys.stdout
                },
                'file_json': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'json',
                    'filename': f'logs/{self.app_name}_staging.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'encoding': 'utf-8'
                }
            },
            'loggers': {
                self.app_name: {
                    'level': 'INFO',
                    'handlers': ['console', 'file_json'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['console']
            }
        }
    
    def _get_production_config(self) -> Dict[str, Any]:
        """Production logging: Structured JSON logs for cloud platforms."""
        
        # Check if running on Google Cloud Run
        is_cloud_run = os.getenv("K_SERVICE") is not None
        # Check if running on AWS ECS
        is_aws_ecs = os.getenv("AWS_EXECUTION_ENV") is not None
        
        if is_cloud_run:
            return self._get_cloud_run_config()
        elif is_aws_ecs:
            return self._get_aws_ecs_config()
        else:
            return self._get_generic_production_config()
    
    def _get_cloud_run_config(self) -> Dict[str, Any]:
        """Google Cloud Run optimized logging (JSON to stdout)."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'cloud_run': {
                    '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                    'format': '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(funcName)s %(message)s',
                    'reserved_attrs': ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process']
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'cloud_run',
                    'stream': sys.stdout
                }
            },
            'loggers': {
                self.app_name: {
                    'level': 'INFO',
                    'handlers': ['console'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'WARNING',
                'handlers': ['console']
            }
        }
    
    def _get_aws_ecs_config(self) -> Dict[str, Any]:
        """AWS ECS optimized logging (JSON to stdout)."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'aws_ecs': {
                    '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                    'format': '%(asctime)s %(aws_request_id)s %(name)s %(levelname)s %(message)s',
                    'datefmt': '%Y-%m-%dT%H:%M:%S.%fZ'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'INFO',
                    'formatter': 'aws_ecs',
                    'stream': sys.stdout
                }
            },
            'loggers': {
                self.app_name: {
                    'level': 'INFO',
                    'handlers': ['console'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'WARNING',
                'handlers': ['console']
            }
        }
    
    def _get_generic_production_config(self) -> Dict[str, Any]:
        """Generic production logging with file rotation."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'production': {
                    '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                    'format': '%(asctime)s %(name)s %(levelname)s %(filename)s %(lineno)d %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'WARNING',
                    'formatter': 'production',
                    'stream': sys.stdout
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'level': 'INFO',
                    'formatter': 'production',
                    'filename': f'logs/{self.app_name}_production.log',
                    'maxBytes': 52428800,  # 50MB
                    'backupCount': 10,
                    'encoding': 'utf-8'
                }
            },
            'loggers': {
                self.app_name: {
                    'level': 'INFO',
                    'handlers': ['console', 'file'],
                    'propagate': False
                }
            },
            'root': {
                'level': 'WARNING',
                'handlers': ['console']
            }
        }
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Default/fallback logging configuration."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'simple': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.log_level,
                    'formatter': 'simple'
                }
            },
            'root': {
                'level': self.log_level,
                'handlers': ['console']
            }
        }
    
    def setup_logging(self) -> logging.Logger:
        """Initialize logging configuration and return logger instance."""
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Get and apply configuration
        config = self.get_log_config()
        logging.config.dictConfig(config)
        
        # Get the main application logger
        logger = logging.getLogger(self.app_name)
        
        # Log initialization
        logger.info(
            f"Logging initialized",
            extra={
                "environment": self.environment,
                "log_level": self.log_level,
                "app_name": self.app_name
            }
        )
        
        return logger
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Get a logger instance."""
        logger_name = name or self.app_name
        return logging.getLogger(logger_name)


# Convenience functions for easy import
def setup_logging() -> logging.Logger:
    """Setup logging and return main application logger."""
    manager = LoggingManager()
    return manager.setup_logging()

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger instance."""
    manager = LoggingManager()
    return manager.get_logger(name)

# Custom filter for sensitive data
class SensitiveDataFilter(logging.Filter):
    """Filter to mask sensitive information in logs."""
    
    SENSITIVE_PATTERNS = [
        'password', 'secret', 'key', 'token', 'auth', 'credential'
    ]
    
    def filter(self, record):
        if hasattr(record, 'getMessage'):
            message = record.getMessage()
            for pattern in self.SENSITIVE_PATTERNS:
                if pattern.lower() in message.lower():
                    # Replace sensitive data with asterisks
                    import re
                    pattern_regex = rf'({pattern}["\s]*[:=]["\s]*)([^"\s,}}]+)'
                    record.msg = re.sub(pattern_regex, r'\1***', str(record.msg), flags=re.IGNORECASE)
        return True

# Usage example
if __name__ == "__main__":
    # Setup logging
    logger = setup_logging()
    
    # Test different log levels
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    # Test with extra fields (for JSON logging)
    logger.info("User action", extra={
        "user_id": "12345",
        "action": "login",
        "ip_address": "192.168.1.1"
    })
