import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from functools import wraps
import inspect
import json
import time

class LogManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LogManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize logging configuration"""
        self.logs_dir = os.path.join(os.getcwd(), 'logs')
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger('bibliometric_pipeline')
        self.logger.setLevel(logging.INFO)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(caller)s | %(message)s'
        )
        
        # Create handlers
        self.file_handler = logging.FileHandler(
            os.path.join(self.logs_dir, f'pipeline_{datetime.now().strftime("%Y%m%d")}.log')
        )
        self.file_handler.setFormatter(file_formatter)
        
        # Add handlers to logger
        self.logger.addHandler(self.file_handler)
        
        # Store execution context
        self.current_user = None
        self.current_script = None

        # Add pipeline tracking attributes
        self.pipeline_start_time = None
        self.current_phase = None
        self.phase_start_time = None
    
    def set_context(self, user_id: Optional[str] = None, script_name: Optional[str] = None):
        """Set the current execution context"""
        self.current_user = user_id
        self.current_script = script_name
        
    def _get_caller(self):
        """Get the name of the calling function and its class"""
        stack = inspect.stack()
        # Look for first external caller
        for frame in stack[2:]:  # Skip this function and its immediate caller
            module = inspect.getmodule(frame[0])
            if module and not module.__name__.startswith('logging'):
                return f"{module.__name__}.{frame.function}"
        return "unknown"
    
    def log(self, level: str, message: str, **kwargs):
        """Log a message with the current context"""
        extra = {
            'caller': self._get_caller(),
            'user_id': self.current_user,
            'script': self.current_script,
            **kwargs
        }
        
        # Format message with context
        context_msg = f"[User: {self.current_user or 'unknown'}] [Script: {self.current_script or 'unknown'}] {message}"
        
        if level.upper() == 'INFO':
            self.logger.info(context_msg, extra=extra)
        elif level.upper() == 'ERROR':
            self.logger.error(context_msg, extra=extra)
        elif level.upper() == 'WARNING':
            self.logger.warning(context_msg, extra=extra)
        
        # Save detailed log entry to JSON
        self._save_detailed_log(level, message, extra)
    
    def _save_detailed_log(self, level: str, message: str, extra: dict):
        """Save a detailed log entry to JSON file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            **extra
        }
        
        json_log_path = os.path.join(self.logs_dir, f'detailed_log_{datetime.now().strftime("%Y%m%d")}.json')
        
        try:
            # Load existing logs
            if os.path.exists(json_log_path):
                with open(json_log_path, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Append new log
            logs.append(log_entry)
            
            # Save updated logs
            with open(json_log_path, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save detailed log: {str(e)}")

    def start_pipeline(self):
        """Mark the start of pipeline execution"""
        self.pipeline_start_time = time.time()
        self.log('INFO', "Pipeline execution started")

    def end_pipeline(self, success: bool, stats: Dict[str, Any]):
        """Mark the end of pipeline execution"""
        duration = time.time() - (self.pipeline_start_time or time.time())
        status = "successfully" if success else "with errors"
        self.log('INFO', f"Pipeline execution ended {status} (duration: {duration:.2f}s)", stats=stats)
        self.pipeline_start_time = None

    def start_phase(self, phase_name: str):
        """Mark the start of a pipeline phase"""
        self.current_phase = phase_name
        self.phase_start_time = time.time()
        self.log('INFO', f"Starting phase: {phase_name}")

    def end_phase(self, success: bool, details: Dict[str, Any]) -> None:
        """Mark the end of a pipeline phase"""
        if not self.current_phase or not self.phase_start_time:
            return
            
        duration = time.time() - self.phase_start_time
        status = "successfully" if success else "with errors"
        
        # Create message and metadata separately
        message = f"Phase '{self.current_phase}' ended {status} (duration: {duration:.2f}s)"
        metadata = {
            'phase': self.current_phase,
            'duration': duration,
            'success': success,
            **details
        }
        
        # Log with metadata as extra kwargs
        self.log('INFO', message, **metadata)
                
        self.current_phase = None
        self.phase_start_time = None

    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline execution statistics"""
        return {
            "pipeline_duration": time.time() - (self.pipeline_start_time or time.time()) if self.pipeline_start_time else 0,
            "current_phase": self.current_phase,
            "phase_duration": time.time() - (self.phase_start_time or time.time()) if self.phase_start_time else 0
        }

    def log_error(self, error: Exception) -> None:
        """Log an error with traceback information."""
        import traceback
        error_msg = f"{str(error)}\n{''.join(traceback.format_tb(error.__traceback__))}"
        self.log('ERROR', error_msg)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Convenience method for warning logs."""
        self.log('WARNING', message, **kwargs)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Convenience method for info logs."""
        self.log('INFO', message, **kwargs)
        
    def save_summary(self, filename: str = "pipeline_execution.json") -> None:
        """Save execution summary to JSON file."""
        summary = {
            'pipeline_stats': self.get_statistics(),
            'timestamp': datetime.now().isoformat()
        }
        
        filepath = os.path.join(self.logs_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            self.log_error(e)

# Create decorator for logging function calls
def log_execution(level='INFO'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_manager = LogManager()
            
            # Get function context
            module = inspect.getmodule(func)
            script_name = module.__name__ if module else 'unknown'
            
            # Log function call
            log_manager.log(level, f"Executing {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                log_manager.log(level, f"Completed {func.__name__}")
                return result
            except Exception as e:
                log_manager.log('ERROR', f"Error in {func.__name__}: {str(e)}")
                raise
                
        return wrapper
    return decorator
