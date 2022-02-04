import sys
import os
import requests
import time
import yaml
import json
from os import listdir
from os.path import isfile, join

argv = sys.argv[1:]

def print_help():
    print(f"python cli.py --run-suite --suite-id=x")
    print(f"python cli.py --run-test --test-id=x")       

def run_test_suite(suite_id):
    headers = {
        'Content-type': 'application/json',
        'auth-token': 'ffeebe94-f164-436c-baae-95d27d00d31d'
    }
    tests = load_tests()
    data = {
        "forceCancelPreviousTesting": "true",
        "baselineMutations": [
        ]
    }
    for test in tests:
        data["baselineMutations"].append({
            "customSteps": f"{test.get('scenario')}",
            "description": f"{test.get('title')}",
            "labels": ["ci"]})
    json_data = json.dumps(data)
    r = requests.post(f"https://api.testrigor.com/api/v1/apps/{suite_id}/retest", data=json_data, headers=headers)
    print(r.status_code, r.reason)
    if r.status_code == 200:
        while True:
            r = requests.get(f"https://api.testrigor.com/api/v1/apps/{suite_id}/status", headers=headers)
            if r.status_code == 400 or r.status_code == 500:
                print("Error calling API")
                break
            elif r.status_code == 227 or r.status_code == 228:
                print("In Progress")
            elif r.status_code == 200:
                print("Passed")
                print(f"https://app.testrigor.com/test-suites/{suite_id}/last-run/reports")
                break
            elif r.status_code == 230:
                print("Failed")
                print(f"https://app.testrigor.com/test-suites/{suite_id}/last-run/reports")
                print(f"https://app.testrigor.com/test-suites/{suite_id}/last-run/errors")
                break
            time.sleep(10)    

def load_tests():
    result = []
    tests_dir = "./tests"
    test_files = [f for f in listdir(tests_dir) if isfile(join(tests_dir, f))]
    for test_file in test_files:
        with open(f"{tests_dir}/{test_file}", "r") as stream:
            try:
                yml = yaml.safe_load(stream)
                result.append({
                    "title": yml.get('Title'),
                    "scenario": yml.get('Scenario')
                })
            except yaml.YAMLError as e:
                print(e)
            pass
    return result

if len(argv) > 0:
    arg0 = argv[0]
    arg1 = argv[1]
    if arg0 == '-h' or arg0 == 'help':
        print_help()
    elif arg0 == '--run-suite' and len(argv) > 1 and arg1.startswith('--suite-id='):
        print(f'Running {arg1.replace("--suite-id=","")} suite')
        run_test_suite(arg1.replace("--suite-id=",""))
    elif arg0 == '--run-test' and len(argv) > 1 and arg1.startswith('--test-id='):
        print(f'Running {arg1.replace("--test-id=","")} test')
        run_test_suite(arg1.replace("--test-id-id=",""))
    else:
        print_help()
else:
    print_help()