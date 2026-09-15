# Superuser Intervention Report

## Overview
This feature adds a comprehensive reporting system to track all status changes made by superusers using the "Update Status" feature in the Odoo workflow system.

## Implementation Details

### 1. Database Changes

#### approval.log Model Enhancement
- **New Field**: `is_superuser_intervention` (Boolean)
  - Marks log entries created when superusers manually update document statuses
  - Default value: `False`
  - Description: "Indicates if this state change was done by superuser using 'Update Status' feature"

### 2. Wizard Enhancement

#### approval.state.update (wizard/approval_state_update.py)
Modified the `action_update()` method to:
- Store old states before updating
- Create approval log entries with `is_superuser_intervention=True`
- Add descriptive message: "Status updated by superuser using 'Update Status' feature"

### 3. SQL View Report

#### approval.superuser.intervention.report (models/approval_superuser_intervention_report.py)
Created a SQL view-based reporting model that:
- Shows all superuser interventions
- Joins with previous log entries to show old status
- Retrieves document type names (with Arabic translation support)
- Fields:
  - `id`: Unique identifier
  - `date`: Intervention timestamp
  - `user_id`: Superuser who made the change
  - `model_id`: Document model type
  - `record_id`: Document ID
  - `old_state`: Previous status code
  - `state`: New status code
  - `old_name`: Previous status name (computed)
  - `name`: New status name (computed)
  - `description`: Intervention description
  - `document_name`: Document type name (with Arabic support)

### 4. User Interface

#### Tree View
- Read-only list view showing all interventions
- Columns: Date, Superuser, Document Type, Document ID, Old Status, New Status, Description
- No create/edit/delete operations allowed

#### Search View
Filters:
- **Quick Filters**:
  - Today
  - This Week
  - This Month
  
- **Searchable Fields**:
  - Superuser
  - Document Type
  - Document ID
  - Date

- **Group By Options**:
  - Superuser
  - Document Type
  - Date (by day)

### 5. Menu Structure
- **Location**: Settings > Workflow Config > Superuser Interventions
- **Access**: Restricted to `base.group_system` (System administrators only)
- **Sequence**: 100 (appears at the end of the menu)

### 6. Security

#### Access Rights (security/ir.model.access.csv)
- Model: `approval.superuser.intervention.report`
- Group: `base.group_system`
- Permissions: Read only (no write, create, or delete)

### 7. Internationalization

#### Arabic Translations (i18n/ar.po)
Complete Arabic translations added for:
- Menu items
- Field labels
- Help text
- Filter names
- View titles

## Usage

### For Superusers
1. Navigate to any document with approval workflow
2. Click "Action" menu (⚙️) → "Update Status"
3. Select the new status
4. Click "Update"
5. The intervention is automatically logged

### For Auditors/Administrators
1. Go to: Settings > Workflow Config > Superuser Interventions
2. View all superuser interventions in the list
3. Filter by:
   - Time period (Today, This Week, This Month)
   - Specific superuser
   - Document type
   - Document ID
4. Group by:
   - Superuser (to see who made the most interventions)
   - Document Type (to see which documents are most affected)
   - Date (to see trends over time)

## Technical Notes

### SQL View Structure
The view uses:
- `LEFT JOIN` to get previous log entries
- Subquery to find the most recent previous state
- Direct reference to `ir_model.name` for document type (automatically translated by Odoo ORM)
- Filters on `is_superuser_intervention = true`

**Note**: The `document_name` field pulls from `ir_model.name` which is automatically translated by Odoo's ORM based on the user's language preference. No direct translation table queries are needed.

### Performance Considerations
- The SQL view is efficient as it directly queries the database
- Indexes on `approval_log` table (especially on `is_superuser_intervention`, `model_id`, `record_id`) will improve performance
- The view is read-only, so no write performance impact

### Future Enhancements
Potential improvements:
1. Add export to Excel functionality
2. Add graphical charts (e.g., interventions over time)
3. Add email notifications when interventions occur
4. Add approval/rejection workflow for interventions
5. Add reason field to the update status wizard

## Files Modified/Created

### New Files:
1. `models/approval_superuser_intervention_report.py` - Report model
2. `view/approval_superuser_intervention_report.xml` - Views and menu
3. `SUPERUSER_INTERVENTION_REPORT.md` - This documentation

### Modified Files:
1. `models/approval_log.py` - Added `is_superuser_intervention` field
2. `wizard/approval_state_update.py` - Added logging logic
3. `models/__init__.py` - Imported new report model
4. `__manifest__.py` - Added new view file
5. `security/ir.model.access.csv` - Added access rights
6. `i18n/ar.po` - Added Arabic translations

## Testing Checklist

- [ ] Upgrade module successfully
- [ ] Superuser can access "Update Status" feature
- [ ] Status updates are logged with `is_superuser_intervention=True`
- [ ] Report shows logged interventions
- [ ] Filters work correctly
- [ ] Group by works correctly
- [ ] Arabic translations display correctly
- [ ] Only system users can access the report
- [ ] Old status is correctly retrieved
- [ ] Document type names show correctly

## Deployment Notes

### Module Upgrade
After deploying these changes:
```bash
# Stop Odoo server
# Deploy code changes
# Restart Odoo server
# Upgrade module via UI or CLI:
odoo-bin -u eds_workflow -d <database_name>
```

### Database Migration
- No manual database migration needed
- SQL view is created automatically via `init()` method
- New field is added automatically to `approval_log` table

## Support

For issues or questions about this feature:
- Check Odoo logs for errors
- Verify `approval_log` table has `is_superuser_intervention` column
- Verify SQL view exists: `SELECT * FROM approval_superuser_intervention_report LIMIT 1;`
- Check user permissions (must be in `base.group_system`)

---
**Created**: November 23, 2025  
**Author**: Omar Khaled  
**Module**: eds_workflow  
**Version**: 17.0.1.6.7+

