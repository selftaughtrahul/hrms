---
description: Reset HRMS database
---

1. Confirm deletion of `d:\realproject\hrm\hrms\db.sqlite3`.

// turbo
2. Delete and Migrate:
```powershell
Remove-Item d:\realproject\hrm\hrms\db.sqlite3 -Force
python d:\realproject\hrm\hrms\manage.py migrate
```

// turbo
3. Seed:
```powershell
python d:\realproject\hrm\hrms\seed_data.py
```
