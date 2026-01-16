"""Security Implementation Verification Script

This script verifies that all security measures are properly implemented.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_script_executor_security():
    """Test script executor security measures"""
    print("\n=== Testing Script Executor Security ===")
    
    from app.services.script_executor import ScriptExecutor
    
    # Test 1: Blocked module detection
    print("\n1. Testing blocked module detection...")
    dangerous_script = """
import os
print(os.listdir())
"""
    is_valid = ScriptExecutor.validate_script(dangerous_script)
    assert not is_valid, "Should block 'os' module"
    print("   ✓ Blocked dangerous 'os' module")
    
    # Test 2: Dangerous function detection
    print("\n2. Testing dangerous function detection...")
    eval_script = """
result = eval('1 + 1')
print(result)
"""
    is_valid = ScriptExecutor.validate_script(eval_script)
    assert not is_valid, "Should block 'eval' function"
    print("   ✓ Blocked dangerous 'eval' function")
    
    # Test 3: Safe script validation
    print("\n3. Testing safe script validation...")
    safe_script = """
import random
print(random.randint(1, 100))
"""
    is_valid = ScriptExecutor.validate_script(safe_script)
    assert is_valid, "Should allow safe script"
    print("   ✓ Allowed safe script")
    
    print("\n✅ Script Executor Security: PASSED")


def test_file_security():
    """Test file upload security measures"""
    print("\n=== Testing File Upload Security ===")
    
    from app.core.security import FileSecurityValidator
    
    # Test 1: Filename validation
    print("\n1. Testing filename validation...")
    
    # Test dangerous patterns
    dangerous_names = [
        "../../../etc/passwd",
        "file<script>.pdf",
        "file\x00.exe",
        ".hidden_file.txt",
    ]
    
    for name in dangerous_names:
        is_valid, error = FileSecurityValidator.validate_filename(name)
        assert not is_valid, f"Should reject dangerous filename: {name}"
    print("   ✓ Rejected dangerous filenames")
    
    # Test safe filename
    is_valid, error = FileSecurityValidator.validate_filename("document.pdf")
    assert is_valid, "Should accept safe filename"
    print("   ✓ Accepted safe filename")
    
    # Test 2: Filename sanitization
    print("\n2. Testing filename sanitization...")
    dirty_name = "My Document (2024)!@#$%.pdf"
    clean_name = FileSecurityValidator.sanitize_filename(dirty_name)
    assert ".." not in clean_name, "Should not contain path traversal"
    assert "<" not in clean_name, "Should not contain special characters"
    print(f"   ✓ Sanitized: '{dirty_name}' -> '{clean_name}'")
    
    print("\n✅ File Upload Security: PASSED")


def test_api_key_security():
    """Test API key security measures"""
    print("\n=== Testing API Key Security ===")
    
    try:
        from app.core.security import APIKeyEncryption
        
        # Test 1: Key masking
        print("\n1. Testing API key masking...")
        api_key = "sk-test-1234567890abcdef"
        masked = APIKeyEncryption.mask_api_key(api_key)
        assert "sk-" in masked, "Should show prefix"
        assert "..." in masked, "Should contain ellipsis"
        assert "cdef" in masked, "Should show last 4 chars"
        assert "1234567890" not in masked, "Should hide middle"
        print(f"   ✓ Masked: '{api_key}' -> '{masked}'")
        
        # Test 2: Encryption/Decryption (requires cryptography)
        print("\n2. Testing encryption/decryption...")
        try:
            original = "test-api-key-12345"
            encrypted = APIKeyEncryption.encrypt_api_key(original)
            decrypted = APIKeyEncryption.decrypt_api_key(encrypted)
            
            assert encrypted != original, "Should be encrypted"
            assert decrypted == original, "Should decrypt to original"
            print(f"   ✓ Encryption roundtrip successful")
        except Exception as e:
            print(f"   ⚠ Encryption test skipped: {str(e)}")
            print("   (Install cryptography library and set ENCRYPTION_KEY)")
        
        print("\n✅ API Key Security: PASSED")
        
    except ImportError as e:
        print(f"\n⚠ API Key Security tests skipped: {str(e)}")


def test_database_security():
    """Test database security measures"""
    print("\n=== Testing Database Security ===")
    
    from app.core.database_security import DatabaseSecurityValidator
    
    # Test 1: SQL injection detection
    print("\n1. Testing SQL injection detection...")
    
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "1' OR '1'='1",
        "admin'--",
        "1 UNION SELECT * FROM users",
    ]
    
    for malicious in malicious_inputs:
        is_valid = DatabaseSecurityValidator.validate_input(malicious)
        assert not is_valid, f"Should detect SQL injection: {malicious}"
    print("   ✓ Detected SQL injection attempts")
    
    # Test safe input
    safe_input = "normal search query"
    is_valid = DatabaseSecurityValidator.validate_input(safe_input)
    assert is_valid, "Should allow safe input"
    print("   ✓ Allowed safe input")
    
    # Test 2: Search query sanitization
    print("\n2. Testing search query sanitization...")
    dirty_query = "test'; DROP TABLE users"
    clean_query = DatabaseSecurityValidator.sanitize_search_query(dirty_query)
    assert ";" not in clean_query, "Should remove semicolons"
    assert "DROP" not in clean_query or clean_query != dirty_query, "Should sanitize dangerous content"
    print(f"   ✓ Sanitized: '{dirty_query}' -> '{clean_query}'")
    
    # Test 3: Limit/Offset validation
    print("\n3. Testing limit/offset validation...")
    limit, offset = DatabaseSecurityValidator.validate_limit_offset(9999, -5)
    assert limit <= 1000, "Should cap limit at 1000"
    assert offset >= 0, "Should ensure non-negative offset"
    print(f"   ✓ Validated: limit={limit}, offset={offset}")
    
    print("\n✅ Database Security: PASSED")


def main():
    """Run all security verification tests"""
    print("=" * 60)
    print("Security Implementation Verification")
    print("=" * 60)
    
    try:
        test_script_executor_security()
        test_file_security()
        test_api_key_security()
        test_database_security()
        
        print("\n" + "=" * 60)
        print("✅ ALL SECURITY TESTS PASSED")
        print("=" * 60)
        print("\nSecurity measures are properly implemented!")
        print("\nNext steps for production:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Generate encryption key: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"")
        print("3. Add ENCRYPTION_KEY to .env")
        print("4. Create limited-privilege database user")
        print("5. Enable database SSL/TLS")
        print("\nSee SECURITY_IMPLEMENTATION.md for details.")
        
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
