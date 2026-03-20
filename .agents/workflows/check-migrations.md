---
description: Check migration status
---

// turbo-all
1. Show status:
```powershell
python d:\realproject\hrm\hrms\manage.py showmigrations
```

2. Detect changes:
```powershell
python d:\realproject\hrm\hrms\manage.py makemigrations --check --dry-run
```
