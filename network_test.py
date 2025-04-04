import httpx
import socket
import json
import sys
import os

def test_dns():
    print("Testing DNS resolution...")
    try:
        ip_address = socket.gethostbyname("api.deepseek.com")
        print(f"DNS resolution successful: api.deepseek.com resolves to {ip_address}")
        return True
    except socket.gaierror as e:
        print(f"DNS resolution failed: {e}")
        return False

def test_connection():
    print("Testing connection to api.deepseek.com...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(("api.deepseek.com", 443))
        s.close()
        print("TCP connection successful on port 443")
        return True
    except socket.error as e:
        print(f"TCP connection failed: {e}")
        return False

def test_http_request():
    print("Testing HTTP request to DeepSeek API...")
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get("https://api.deepseek.com/")
            print(f"HTTP GET status code: {response.status_code}")
            print(f"HTTP GET response: {response.text[:200]}...")
            return True
    except Exception as e:
        print(f"HTTP request failed: {e}")
        return False

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def test_api_auth():
    config = load_config()
    api_token = config.get("api_token", "")
    
    if not api_token:
        print("No API token found in config.json")
        return False
    
    print(f"Testing API authentication with token (first 5 chars): {api_token[:5]}...")
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get("https://api.deepseek.com/v1/models", headers=headers)
            print(f"API auth status code: {response.status_code}")
            if response.status_code == 200:
                print("API authentication successful!")
                models = response.json()
                print(f"Available models: {json.dumps(models, indent=2)}")
                return True
            else:
                print(f"API authentication failed. Response: {response.text}")
                return False
    except Exception as e:
        print(f"API authentication test failed: {e}")
        return False

if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print(f"HTTPX version: {httpx.__version__}")
    print(f"Operating system: {os.name} - {sys.platform}")
    print("\n" + "="*50 + "\n")
    
    dns_ok = test_dns()
    conn_ok = test_connection()
    http_ok = test_http_request()
    auth_ok = test_api_auth()
    
    print("\n" + "="*50 + "\n")
    print("Summary:")
    print(f"- DNS resolution: {'✓' if dns_ok else '✗'}")
    print(f"- TCP connection: {'✓' if conn_ok else '✗'}")
    print(f"- HTTP request: {'✓' if http_ok else '✗'}")
    print(f"- API authentication: {'✓' if auth_ok else '✗'}")
    
    if not all([dns_ok, conn_ok, http_ok, auth_ok]):
        print("\nSome tests failed. Please check your network connection and API token.")
        if not dns_ok:
            print("- Check your DNS settings or internet connection")
        if not conn_ok:
            print("- Check if a firewall is blocking outbound connections to port 443")
        if not http_ok:
            print("- Check your internet connection or proxy settings")
        if not auth_ok:
            print("- Verify that your API token is valid")
    else:
        print("\nAll tests passed! Your connection to the DeepSeek API is working correctly.") 