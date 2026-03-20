---
description: Run HRMS tests
---

// turbo-all
1. Run all tests:
```powershell
python d:\realproject\hrm\hrms\manage.py test attendance employees payroll leaves holidays core --verbosity=2
```

2. Run specific app:
```powershell
python d:\realproject\hrm\hrms\manage.py test <app_name> --verbosity=2
```
