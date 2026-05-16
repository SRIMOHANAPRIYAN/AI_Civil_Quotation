import json
import requests
import time

API_URL = "http://127.0.0.1:8000/api/generate-fusion"

def run_automated_tests():
    print("\n Starting Civil Engineering QA Testing Suite...\n")
    
    try:
        with open("test_suite.json", "r") as file:
            test_cases = json.load(file)
    except FileNotFoundError:
        print("ERROR: test_suite.json not found!")
        return
        
    passed = 0
    failed = 0
    
    for tc in test_cases:
        print(f"Running {tc['id']} [{tc['category']}]...")
        
        try:
            # We use 'data' to send form-data, mirroring how the UI sends text
            payload = {"text_data": tc["prompt"], "push_to_sheets": "false"}
            response = requests.post(API_URL, data=payload)
            status_code = response.status_code
            
            test_passed = False
            
            # 200 means successful extraction and RAG pricing found
            if tc["expected_status"] == "success" and status_code == 200:
                test_passed = True
            # 400 with our Security error message means the Firewall did its job
            elif tc["expected_status"] == "blocked" and status_code == 400 and "Security Alert" in response.text:
                test_passed = True
            # 400 or 500 without security alert means standard validation caught it (e.g., zero area)
            elif tc["expected_status"] == "error" and status_code != 200 and "Security Alert" not in response.text:
                test_passed = True
                
            if test_passed:
                print("PASS")
                passed += 1
            else:
                print(f"FAIL (Expected {tc['expected_status']}, Got HTTP {status_code})")
                print(f"Response: {response.text}")
                failed += 1
                
        except Exception as e:
            print(f"ERROR: Could not connect to server. Is Flask running? ({e})")
            failed += 1
            
        time.sleep(1) 
        

    print("TEST EXECUTION SUMMARY")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed:      {passed}")
    print(f"Failed:      {failed}")
    
if __name__ == "__main__":
    run_automated_tests()