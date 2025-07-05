#!/usr/bin/env python3
"""
Test runner script for the PDF summarization service
"""

import os
import sys
import subprocess
import time
import signal
from pathlib import Path
import threading

def run_command(command, cwd=None):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def setup_test_environment():
    """Set up the test environment"""
    print("🔧 Setting up test environment...")
    
    # Set environment variables for testing
    os.environ["AUTH_TOKEN"] = "test_bearer_token"
    os.environ["OPENAI_API_KEY"] = "test_openai_key"
    os.environ["EXTERNAL_API_URL"] = "http://localhost:8001/mock-api"
    os.environ["EXTERNAL_API_TOKEN"] = "test_external_token"
    
    # Create test PDF if it doesn't exist
    pdf_path = Path("tests/sample_document.pdf")
    if not pdf_path.exists():
        print("📄 Creating test PDF...")
        success, stdout, stderr = run_command("python create_test_pdf.py")
        if not success:
            print(f"❌ Failed to create test PDF: {stderr}")
            return False
        print("✅ Test PDF created successfully")
    
    return True

def start_mock_server():
    """Start the mock external API server"""
    print("🚀 Starting mock external API server...")
    
    # Start the mock server in a separate process
    process = subprocess.Popen([
        sys.executable, "mock_external_api.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait a bit for the server to start
    time.sleep(2)
    
    # Check if the server is running
    success, stdout, stderr = run_command("curl -s http://localhost:8001/")
    if success:
        print("✅ Mock external API server is running")
        return process
    else:
        print("❌ Failed to start mock external API server")
        process.terminate()
        return None

def run_unit_tests():
    """Run unit tests"""
    print("\n🧪 Running unit tests...")
    
    success, stdout, stderr = run_command("python -m pytest tests/test_unit.py -v --tb=short")
    
    if success:
        print("✅ Unit tests passed")
        print(stdout)
        return True
    else:
        print("❌ Unit tests failed")
        print(stderr)
        return False

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running integration tests...")
    
    success, stdout, stderr = run_command("python -m pytest tests/test_integration.py -v --tb=short")
    
    if success:
        print("✅ Integration tests passed")
        print(stdout)
        return True
    else:
        print("❌ Integration tests failed")
        print(stderr)
        return False

def run_end_to_end_test():
    """Run end-to-end test with real API calls"""
    print("\n🌐 Running end-to-end test...")
    
    # Start the main application
    print("🚀 Starting main application...")
    main_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for the server to start
    time.sleep(3)
    
    # Test the upload endpoint with a real PDF
    print("📤 Testing PDF upload...")
    
    # Create a test PDF
    success, stdout, stderr = run_command("python create_test_pdf.py")
    if not success:
        print(f"❌ Failed to create test PDF: {stderr}")
        main_process.terminate()
        return False
    
    # Upload the PDF
    curl_command = '''
    curl -X POST "http://localhost:8000/upload" \
      -H "Authorization: Bearer test_bearer_token" \
      -F "file=@tests/sample_document.pdf" \
      -s -w "\\n%{http_code}\\n"
    '''
    
    success, stdout, stderr = run_command(curl_command)
    
    # Clean up
    main_process.terminate()
    
    if success and "200" in stdout:
        print("✅ End-to-end test passed")
        print(stdout)
        return True
    else:
        print("❌ End-to-end test failed")
        print(f"stdout: {stdout}")
        print(f"stderr: {stderr}")
        return False

def main():
    """Main test runner function"""
    print("🧪 PDF Summarization Service Test Runner")
    print("=" * 50)
    
    # Setup test environment
    if not setup_test_environment():
        print("❌ Failed to setup test environment")
        return 1
    
    # Start mock server
    mock_server = start_mock_server()
    if not mock_server:
        print("❌ Failed to start mock server")
        return 1
    
    try:
        # Run tests
        results = []
        
        # Unit tests
        results.append(run_unit_tests())
        
        # Integration tests
        results.append(run_integration_tests())
        
        # End-to-end test (optional, requires curl)
        if run_command("which curl")[0]:
            results.append(run_end_to_end_test())
        else:
            print("⚠️  Skipping end-to-end test (curl not available)")
        
        # Summary
        print("\n📊 Test Results Summary")
        print("=" * 30)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ Passed: {passed}/{total}")
        
        if passed == total:
            print("🎉 All tests passed!")
            return 0
        else:
            print("❌ Some tests failed")
            return 1
    
    finally:
        # Clean up mock server
        if mock_server:
            print("🧹 Cleaning up mock server...")
            mock_server.terminate()
            mock_server.wait()

if __name__ == "__main__":
    sys.exit(main())