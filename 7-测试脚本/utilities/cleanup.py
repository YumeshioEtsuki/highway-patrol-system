import httpx
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImFkbWluIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzY2NTE3ODg2fQ.CG8Y_dv3rjwXJKr655DFJBZX3dzLlWFkvZ-GYhpYB8Y"
c = httpx.Client(base_url='http://127.0.0.1:5000', headers={'Authorization': f'Bearer {TOKEN}'})
r = c.post('/api/admin/clean-test-data').json()
print(f"已删除{r.get('deleted_count')}条数据")
s = c.get('/api/admin/stats').json()
print(f"当前总数: {s.get('total_records')}")
