---
description: Scaffold a new Django app inside the HRMS project
---

1. Ask user for the app name.

// turbo
2. Create the app:
```powershell
python d:\realproject\hrm\hrms\manage.py startapp <app_name> d:\realproject\hrm\hrms\<app_name>
```

3. Add to `INSTALLED_APPS` in `d:\realproject\hrm\hrms\hrms_project\settings.py`.

4. **SaaS Pattern**:
   - Models MUST inherit from `core.models.TenantAwareModel`.
   - Use `unique_together = ['tenant', 'field_name']` for unique constraints.
   - If app has a custom manager, it MUST inherit from `core.models.TenantManager`.

5. Register URLs in `d:\realproject\hrm\hrms\hrms_project\urls.py`.

// turbo
6. Migration:
```powershell
python d:\realproject\hrm\hrms\manage.py makemigrations <app_name>
python d:\realproject\hrm\hrms\manage.py migrate
```
