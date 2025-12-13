"""
Test script for METS ECO-MiC validation integration
Run this script to test the validation functionality
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_USER_EMAIL = "admin@example.com"  # Change to your test user
TEST_USER_PASSWORD = "admin123"        # Change to your test password

def login():
    """Login and get auth token"""
    login_data = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(f"{API_BASE_URL}/api/auth/login", data=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_mets_validation(token):
    """Test METS validation from form data"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data that should generate valid METS XML
    test_data = {
        "logical_id": "TEST-DOC-001",
        "title": "Test Document for METS Validation",
        "description": "A test document to verify METS ECO-MiC validation",
        "archive_name": "Test Archive",
        "archive_contact": "test@example.com",
        "document_type": "manuscript",
        "total_pages": 10,
        "language": "it",
        "location": "Rome, Italy",
        "conservative_id": "CONS-001",
        "conservative_id_authority": "ISIL",
        "date_from": "2024-01-01",
        "date_to": "2024-12-31",
        "subjects": "test, validation, mets"
    }
    
    print(f"\n🔍 Testing METS validation with data:")
    print(json.dumps(test_data, indent=2))
    
    response = requests.post(
        f"{API_BASE_URL}/api/documents/validate-mets-from-data",
        json=test_data,
        headers=headers
    )
    
    print(f"\n📡 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Validation Response:")
        print(f"   Valid: {result['valid']}")
        print(f"   Summary: {result['summary']}")
        
        if not result['valid'] and result['errors']:
            print(f"   Errors ({len(result['errors'])}):")
            for i, error in enumerate(result['errors'][:3]):  # Show first 3 errors
                print(f"     {i+1}. {error['type']}: {error['description']}")
                if len(result['errors']) > 3:
                    print(f"     ... and {len(result['errors'])-3} more errors")
        
        return result
    else:
        print(f"❌ Validation failed: {response.status_code}")
        print(response.text)
        return None

def test_invalid_data(token):
    """Test with intentionally invalid data"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test data with missing required fields
    invalid_data = {
        "logical_id": "",  # Empty logical ID should cause issues
        "title": "",       # Empty title
    }
    
    print(f"\n🔍 Testing with invalid data:")
    print(json.dumps(invalid_data, indent=2))
    
    response = requests.post(
        f"{API_BASE_URL}/api/documents/validate-mets-from-data",
        json=invalid_data,
        headers=headers
    )
    
    print(f"\n📡 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"📋 Validation Response:")
        print(f"   Valid: {result['valid']}")
        print(f"   Summary: {result['summary']}")
        
        if not result['valid'] and result['errors']:
            print(f"   Expected errors found: {len(result['errors'])}")
        
        return result
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(response.text)
        return None

def main():
    print("🚀 METS ECO-MiC Validation Integration Test")
    print("="*50)
    
    # Login
    token = login()
    if not token:
        return
    
    # Test valid data
    print("\n" + "="*50)
    print("TEST 1: Valid METS Data")
    print("="*50)
    test_mets_validation(token)
    
    # Test invalid data
    print("\n" + "="*50)
    print("TEST 2: Invalid METS Data")
    print("="*50)
    test_invalid_data(token)
    
    print("\n" + "="*50)
    print("✅ Tests completed!")
    print("="*50)
    print("\nIf both tests ran successfully, the METS validation integration is working.")
    print("You can now test the frontend by:")
    print("1. Going to the document upload wizard")
    print("2. Filling out the form")
    print("3. In the review step, clicking 'Verifica METS ECO-MiC'")

if __name__ == "__main__":
    main()