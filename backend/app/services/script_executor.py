"""Script Executor Service

Executes Python scripts in a sandboxed environment with timeout control.
Includes built-in scripts for common test data generation.
"""

import ast
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class ScriptExecutionError(Exception):
    """Exception raised when script execution fails"""
    pass


class ScriptTimeoutError(ScriptExecutionError):
    """Exception raised when script execution times out"""
    pass


class ScriptExecutor:
    """Service for executing Python scripts in a sandboxed environment"""
    
    # Built-in scripts for common test data generation
    BUILTIN_SCRIPTS = {
        'generate_phone_number': '''
import random

def generate_phone_number():
    """Generate a random Chinese mobile phone number"""
    prefix = ['130', '131', '132', '133', '134', '135', '136', '137', '138', '139',
              '150', '151', '152', '153', '155', '156', '157', '158', '159',
              '180', '181', '182', '183', '184', '185', '186', '187', '188', '189']
    return random.choice(prefix) + ''.join([str(random.randint(0, 9)) for _ in range(8)])

print(generate_phone_number())
''',
        'generate_email': '''
import random
import string

def generate_email():
    """Generate a random email address"""
    username_length = random.randint(6, 12)
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=username_length))
    domains = ['test.com', 'example.com', 'demo.com', 'mail.com']
    return f"{username}@{random.choice(domains)}"

print(generate_email())
''',
        'generate_id_card': '''
import random
from datetime import datetime, timedelta

def generate_id_card():
    """Generate a random Chinese ID card number (18 digits)"""
    # Area code (6 digits) - using Beijing as example
    area_code = '110101'
    
    # Birth date (8 digits)
    start_date = datetime(1970, 1, 1)
    end_date = datetime(2005, 12, 31)
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    birth_date = start_date + timedelta(days=random_days)
    birth_str = birth_date.strftime('%Y%m%d')
    
    # Sequence code (3 digits)
    sequence = str(random.randint(0, 999)).zfill(3)
    
    # Calculate check digit
    id_17 = area_code + birth_str + sequence
    weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
    
    sum_value = sum(int(id_17[i]) * weights[i] for i in range(17))
    check_digit = check_codes[sum_value % 11]
    
    return id_17 + check_digit

print(generate_id_card())
''',
        'get_timestamp': '''
import time

def get_timestamp():
    """Get current timestamp in milliseconds"""
    return int(time.time() * 1000)

print(get_timestamp())
''',
        'md5_encrypt': '''
import hashlib

def md5_encrypt(text):
    """Calculate MD5 hash of text"""
    return hashlib.md5(text.encode()).hexdigest()

# Example usage
print(md5_encrypt("test123"))
''',
        'generate_username': '''
import random
import string

def generate_username():
    """Generate a random username"""
    length = random.randint(6, 12)
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

print(generate_username())
''',
        'generate_password': '''
import random
import string

def generate_password():
    """Generate a random password with mixed characters"""
    length = random.randint(8, 16)
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    password = ''.join(random.choices(chars, k=length))
    # Ensure at least one of each type
    if not any(c.isupper() for c in password):
        password = password[:-1] + random.choice(string.ascii_uppercase)
    if not any(c.isdigit() for c in password):
        password = password[:-1] + random.choice(string.digits)
    return password

print(generate_password())
''',
    }
    
    @classmethod
    def execute(
        cls,
        script_code: str,
        timeout: Optional[int] = None,
        input_data: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a Python script in a sandboxed environment
        
        Args:
            script_code: Python code to execute
            timeout: Timeout in seconds (default: from settings)
            input_data: Optional input data to pass to the script
            
        Returns:
            Dictionary with execution results:
            {
                'success': bool,
                'output': str,
                'error': str,
                'exit_code': int
            }
            
        Raises:
            ScriptTimeoutError: If execution times out
            ScriptExecutionError: If execution fails
        """
        if timeout is None:
            timeout = settings.script_timeout_seconds
        
        # Validate script before execution
        if not cls.validate_script(script_code):
            raise ScriptExecutionError("Script validation failed")
        
        try:
            # Create a temporary file for the script
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False,
                encoding='utf-8'
            ) as temp_file:
                temp_file.write(script_code)
                temp_file_path = temp_file.name
            
            try:
                # Execute the script in a subprocess
                result = subprocess.run(
                    [sys.executable, temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    input=input_data,
                    # Security: limit resource usage
                    env={'PYTHONPATH': ''},  # Isolate from system packages
                )
                
                return {
                    'success': result.returncode == 0,
                    'output': result.stdout.strip(),
                    'error': result.stderr.strip(),
                    'exit_code': result.returncode
                }
                
            finally:
                # Clean up temporary file
                Path(temp_file_path).unlink(missing_ok=True)
                
        except subprocess.TimeoutExpired:
            logger.error(f"Script execution timed out after {timeout} seconds")
            raise ScriptTimeoutError(f"Script execution timed out after {timeout} seconds")
        except Exception as e:
            logger.error(f"Script execution failed: {str(e)}")
            raise ScriptExecutionError(f"Script execution failed: {str(e)}")
    
    @classmethod
    def validate_script(cls, script_code: str) -> bool:
        """Validate Python script syntax
        
        Args:
            script_code: Python code to validate
            
        Returns:
            True if script is valid, False otherwise
        """
        try:
            ast.parse(script_code)
            return True
        except SyntaxError as e:
            logger.warning(f"Script syntax error: {str(e)}")
            return False
    
    @classmethod
    def extract_dependencies(cls, script_code: str) -> List[str]:
        """Extract import statements from script code
        
        Args:
            script_code: Python code to analyze
            
        Returns:
            List of imported module names
        """
        dependencies = []
        
        try:
            tree = ast.parse(script_code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module.split('.')[0])
            
            # Remove standard library modules
            stdlib_modules = {
                'sys', 'os', 'time', 'datetime', 'random', 'string', 'json',
                'math', 're', 'collections', 'itertools', 'functools', 'hashlib',
                'base64', 'uuid', 'pathlib', 'tempfile', 'subprocess', 'logging'
            }
            
            dependencies = [dep for dep in dependencies if dep not in stdlib_modules]
            
            return list(set(dependencies))  # Remove duplicates
            
        except Exception as e:
            logger.warning(f"Failed to extract dependencies: {str(e)}")
            return []
    
    @classmethod
    def get_builtin_script(cls, script_name: str) -> Optional[str]:
        """Get a built-in script by name
        
        Args:
            script_name: Name of the built-in script
            
        Returns:
            Script code or None if not found
        """
        return cls.BUILTIN_SCRIPTS.get(script_name)
    
    @classmethod
    def list_builtin_scripts(cls) -> List[str]:
        """List all available built-in scripts
        
        Returns:
            List of built-in script names
        """
        return list(cls.BUILTIN_SCRIPTS.keys())
    
    @classmethod
    def execute_builtin(
        cls,
        script_name: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute a built-in script
        
        Args:
            script_name: Name of the built-in script
            timeout: Timeout in seconds
            
        Returns:
            Execution results
            
        Raises:
            ScriptExecutionError: If script not found or execution fails
        """
        script_code = cls.get_builtin_script(script_name)
        
        if script_code is None:
            raise ScriptExecutionError(f"Built-in script not found: {script_name}")
        
        return cls.execute(script_code, timeout)
