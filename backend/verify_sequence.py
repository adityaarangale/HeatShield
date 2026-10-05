import sys
import random
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_verification_sequence():
    print("=" * 65)
    print("  RUNNING BACKEND VERIFICATION SEQUENCE")
    print("=" * 65)

    
    results = []
    
    # Step 1: GET /api/health
    try:
        res1 = client.get("/api/health")
        if res1.status_code == 200 and res1.json().get("status") == "ok" and res1.json().get("db") == "connected":
            results.append(("Step 1: GET /api/health", "PASSED", f"Response: {res1.json()}"))
        else:
            results.append(("Step 1: GET /api/health", "FAILED", f"Status: {res1.status_code}, Body: {res1.text}"))
    except Exception as e:
        results.append(("Step 1: GET /api/health", "FAILED", f"Error: {e}"))

    # Generate unique 10-digit phone numbers
    phone_cit = "".join([str(random.randint(0, 9)) for _ in range(10)])
    phone_auth = "".join([str(random.randint(0, 9)) for _ in range(10)])
    password_cit = "CitPass2026!"
    password_auth = "AuthPass2026!"

    # Step 2: Sign up test citizen account
    try:
        res2 = client.post("/api/auth/signup", json={
            "name": "Verification Citizen",
            "phone": phone_cit,
            "password": password_cit,
            "role": "citizen",
            "ward_or_department": "Chandrapur Ward 1"
        })
        if res2.status_code == 201:
            data2 = res2.json()
            if data2.get("id") and data2.get("role") == "citizen" and "password_hash" not in data2:
                results.append(("Step 2: Sign up test citizen account", "PASSED", f"Created User ID: {data2.get('id')}, Phone: {phone_cit}"))
            else:
                results.append(("Step 2: Sign up test citizen account", "FAILED", f"Unexpected payload: {data2}"))
        else:
            results.append(("Step 2: Sign up test citizen account", "FAILED", f"Status: {res2.status_code}, Body: {res2.text}"))
    except Exception as e:
        results.append(("Step 2: Sign up test citizen account", "FAILED", f"Error: {e}"))

    # Step 3: Sign up test authority account
    try:
        res3 = client.post("/api/auth/signup", json={
            "name": "Verification Officer",
            "phone": phone_auth,
            "password": password_auth,
            "role": "authority",
            "ward_or_department": "DDMA Relief Cell"
        })
        if res3.status_code == 201:
            data3 = res3.json()
            if data3.get("id") and data3.get("role") == "authority" and "password_hash" not in data3:
                results.append(("Step 3: Sign up test authority account", "PASSED", f"Created Officer ID: {data3.get('id')}, Phone: {phone_auth}"))
            else:
                results.append(("Step 3: Sign up test authority account", "FAILED", f"Unexpected payload: {data3}"))
        else:
            results.append(("Step 3: Sign up test authority account", "FAILED", f"Status: {res3.status_code}, Body: {res3.text}"))
    except Exception as e:
        results.append(("Step 3: Sign up test authority account", "FAILED", f"Error: {e}"))

    # Step 4: Log in as each and confirm token and role
    citizen_token = None
    authority_token = None
    try:
        login_cit = client.post("/api/auth/login", json={"phone": phone_cit, "password": password_cit})
        login_auth = client.post("/api/auth/login", json={"phone": phone_auth, "password": password_auth})

        if login_cit.status_code == 200 and login_auth.status_code == 200:
            c_data = login_cit.json()
            a_data = login_auth.json()
            if c_data.get("access_token") and c_data.get("role") == "citizen" and a_data.get("access_token") and a_data.get("role") == "authority":
                citizen_token = c_data.get("access_token")
                authority_token = a_data.get("access_token")
                results.append(("Step 4: Log in as each & confirm token/role", "PASSED", f"Citizen Role: {c_data.get('role')}, Authority Role: {a_data.get('role')}"))
            else:
                results.append(("Step 4: Log in as each & confirm token/role", "FAILED", f"Citizen Data: {c_data}, Authority Data: {a_data}"))
        else:
            results.append(("Step 4: Log in as each & confirm token/role", "FAILED", f"Citizen Login Status: {login_cit.status_code}, Authority Login Status: {login_auth.status_code}"))
    except Exception as e:
        results.append(("Step 4: Log in as each & confirm token/role", "FAILED", f"Error: {e}"))

    # Step 5: Call /api/admin/accounts as authority token and confirm both test accounts appear
    try:
        if authority_token:
            admin_res = client.get("/api/admin/accounts", headers={"Authorization": f"Bearer {authority_token}"})
            if admin_res.status_code == 200:
                accounts = admin_res.json()
                phones_found = [a.get("phone") for a in accounts]
                if phone_cit in phones_found and phone_auth in phones_found:
                    results.append(("Step 5: Call /api/admin/accounts with authority token", "PASSED", f"Found both test phone numbers in directory ({len(accounts)} total accounts)"))
                else:
                    results.append(("Step 5: Call /api/admin/accounts with authority token", "FAILED", f"Missing phones. Found: {phones_found}"))
            else:
                results.append(("Step 5: Call /api/admin/accounts with authority token", "FAILED", f"Status: {admin_res.status_code}, Body: {admin_res.text}"))
        else:
            results.append(("Step 5: Call /api/admin/accounts with authority token", "SKIPPED", "No authority token from Step 4"))
    except Exception as e:
        results.append(("Step 5: Call /api/admin/accounts with authority token", "FAILED", f"Error: {e}"))

    # Step 6: Attempt to call /api/admin/accounts with citizen token and confirm 403 rejection
    try:
        if citizen_token:
            cit_admin_res = client.get("/api/admin/accounts", headers={"Authorization": f"Bearer {citizen_token}"})
            if cit_admin_res.status_code == 403:
                results.append(("Step 6: Attempt /api/admin/accounts with citizen token", "PASSED", f"Rejected with HTTP 403 Forbidden: {cit_admin_res.json().get('detail')}"))
            else:
                results.append(("Step 6: Attempt /api/admin/accounts with citizen token", "FAILED", f"Expected HTTP 403, got Status: {cit_admin_res.status_code}, Body: {cit_admin_res.text}"))
        else:
            results.append(("Step 6: Attempt /api/admin/accounts with citizen token", "SKIPPED", "No citizen token from Step 4"))
    except Exception as e:
        results.append(("Step 6: Attempt /api/admin/accounts with citizen token", "FAILED", f"Error: {e}"))

    # Print summary report
    print("\n" + "=" * 65)
    print("  RESULTS SUMMARY:")
    print("=" * 65)
    all_passed = True
    for step, status, detail in results:
        symbol = "[OK]" if status == "PASSED" else "[FAIL]"
        if status != "PASSED":
            all_passed = False
        print(f"{symbol} [{status:<7}] {step}")
        print(f"   |- {detail}")


    print("=" * 65)
    return all_passed

if __name__ == "__main__":
    success = run_verification_sequence()
    sys.exit(0 if success else 1)
