from app.services.employee_monthly_salary_periodic import calculate_monthly_salary_periodic

# Trigger task
result = calculate_monthly_salary_periodic.apply_async()
print(f"Task ID: {result.id}")
print(f"Task Status: {result.status}")

# Tunggu hingga task selesai
result.get(timeout=10)
print(f"Task Result: {result.result}")
