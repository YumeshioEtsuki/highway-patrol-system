import os
import sys
import time
import json
import httpx

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
TOKEN = os.environ.get("ADMIN_TOKEN")

if not TOKEN:
    print("[ERROR] Missing ADMIN_TOKEN env var. Set ADMIN_TOKEN to a valid admin JWT.")
    print("Example: set ADMIN_TOKEN=eyJhbGciOiJI... (Windows)")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

client = httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=30)


def get_stats(data_type: str | None = None) -> dict:
    params = {}
    if data_type:
        params["data_type"] = data_type
    r = client.get("/api/admin/stats", params=params)
    r.raise_for_status()
    return r.json()


def generate(count: int = 30, include_photos: bool = False) -> dict:
    r = client.post("/api/admin/generate", params={"count": count, "include_photos": str(include_photos).lower()})
    r.raise_for_status()
    return r.json()


def clean_test_data() -> dict:
    r = client.post("/api/admin/clean-test-data")
    r.raise_for_status()
    return r.json()


def main():
    print("[STEP] Fetch initial stats (all)...")
    before = get_stats()
    print(json.dumps(before, ensure_ascii=False, indent=2))

    print("[STEP] Generate 30 test records...")
    gen = generate(30, False)
    print(json.dumps(gen, ensure_ascii=False, indent=2))
    assert gen.get("success") is True, "Generate failed"
    assert gen.get("inserted") == 30, f"Inserted {gen.get('inserted')} != 30"

    print("[STEP] Fetch stats after generation (all)...")
    after = get_stats()
    print(json.dumps(after, ensure_ascii=False, indent=2))
    assert after.get("total_records", 0) >= before.get("total_records", 0) + 30 - 1, "Total should increase by ~30"

    print("[STEP] Fetch stats for test data only...")
    only_test = get_stats("test")
    print(json.dumps(only_test, ensure_ascii=False, indent=2))
    assert only_test.get("total_records", 0) >= 30 - 1, "Test total should reflect new records"

    print("[STEP] Clean test data and recheck stats...")
    res = clean_test_data()
    print(json.dumps(res, ensure_ascii=False, indent=2))
    assert res.get("success") is True

    # After clean, test stats should drop
    only_test2 = get_stats("test")
    print(json.dumps(only_test2, ensure_ascii=False, indent=2))

    print("\n✅ Integration test completed.")


if __name__ == "__main__":
    main()
