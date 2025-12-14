# Ant Design Vue Migration Plan

**Project:** Archivia Digital Archive System
**Branch:** `feature/ant-design-ui`
**Created:** 2025-12-14
**Estimated Duration:** 10-12 weeks

---

## Executive Summary

This document outlines the migration strategy from Tailwind CSS to Ant Design Vue for the Archivia frontend. The migration will improve UI consistency, reduce custom CSS, and provide enterprise-grade components for better user experience.

### Key Metrics
- **Total Components:** 13 active components (~6,000 lines of code)
- **Estimated Effort:** 105 hours (2-3 weeks full-time development)
- **Risk Level:** Medium (manageable with phased approach)
- **Testing Required:** High (complex state management and modals)

---

## Current State Analysis

### Technology Stack
- **Vue:** 3.3.4 (Composition API)
- **UI Framework:** Tailwind CSS 4.1.11 + Headless UI
- **State Management:** Pinia 2.1.6
- **Router:** Vue Router 4.2.4
- **Build Tool:** Vite 4.4.9

### Component Inventory

#### Page Components (3)
1. `Login.vue` - Authentication (simple)
2. `Dashboard.vue` - Main layout (medium)
3. `Guide.vue` - User documentation (simple)

#### Document Management (3)
1. `DocumentsManager.vue` - Core operations, 1,257 lines (complex)
2. `DocumentDetailModal.vue` - Detail view/edit (complex)
3. `DocumentUploadForm.vue` - Multi-step wizard (complex)

#### File Management (4)
1. `FileList.vue` - File listing with pagination (medium)
2. `ImageUpload.vue` - Single/batch image upload (medium)
3. `ImageViewer.vue` - Image preview modal (simple)
4. `FolderUpload.vue` - ZIP archive upload (simple)

#### Batch Operations (3)
1. `ExcelBatchImport.vue` - Excel parsing & import (medium)
2. `BatchImageUpload.vue` - Batch image upload (medium)
3. `FileUpload.vue` - Basic file upload (simple)

### Key Features to Preserve
- ✅ Document upload (single file + ZIP folder)
- ✅ Multi-step document creation wizard
- ✅ Document list/table with batch operations
- ✅ Document editing with tabs
- ✅ File categorization (ECO-MiC structure)
- ✅ Excel batch import
- ✅ METS XML export with validation
- ✅ Image preview and management

---

## Migration Strategy

### Phase 1: Setup & Foundation (Week 1)

**Goal:** Install Ant Design Vue and migrate simple components

#### Tasks:
1. **Install Dependencies**
   ```bash
   cd frontend
   npm install ant-design-vue@^4.2.0 dayjs@^1.11.10
   ```

2. **Configure Ant Design**
   - Update `main.js` with Ant Design import
   - Configure theme customization
   - Set up icon imports

3. **Update Vite Config**
   - Remove Tailwind PostCSS plugins
   - Add Ant Design less/css loaders if needed

4. **Migrate Simple Components**
   - `Guide.vue` (static content)
   - `ImageViewer.vue` (modal only)
   - `FileUpload.vue` (basic upload)

**Deliverables:**
- ✅ Ant Design Vue installed and configured
- ✅ 3 simple components migrated
- ✅ Test suite for migrated components

**Estimated Time:** 8-12 hours

---

### Phase 2: Authentication & Forms (Week 2)

**Goal:** Migrate form-based components

#### Tasks:
1. **Login.vue Migration**
   - Replace Tailwind form with `a-form`
   - Use `a-input` and `a-button`
   - Implement form validation with Ant Design rules
   - Update gradient background styling

2. **FolderUpload.vue Migration**
   - Replace custom drag-drop with `a-upload`
   - Use `a-dragger` component
   - Update file status display

3. **Test & Validate**
   - Authentication flow testing
   - Form validation testing
   - Responsive behavior verification

**Component Mapping:**
```vue
<!-- Before (Tailwind) -->
<input type="text" class="px-3 py-2 border rounded-lg" />

<!-- After (Ant Design) -->
<a-input placeholder="Enter text" />
```

**Deliverables:**
- ✅ Login page fully migrated
- ✅ Folder upload component migrated
- ✅ Form validation working

**Estimated Time:** 12-16 hours

---

### Phase 3: Tables & Lists (Week 3)

**Goal:** Migrate table and list components

#### Tasks:
1. **FileList.vue Migration**
   - Replace custom table with `a-table`
   - Use Ant Design pagination
   - Implement column customization
   - Add action buttons with icons

2. **BatchImageUpload.vue Migration**
   - Use `a-table` with status badges
   - Implement `a-tag` for categorization
   - Add progress indicators

3. **Table Features**
   - Sorting
   - Filtering
   - Row selection
   - Responsive columns

**Component Mapping:**
```vue
<!-- Before (Tailwind) -->
<table class="min-w-full divide-y">
  <thead>...</thead>
  <tbody>...</tbody>
</table>

<!-- After (Ant Design) -->
<a-table
  :columns="columns"
  :data-source="data"
  :pagination="pagination"
/>
```

**Deliverables:**
- ✅ FileList component migrated
- ✅ BatchImageUpload migrated
- ✅ Table features working (sort, filter, pagination)

**Estimated Time:** 16-20 hours

---

### Phase 4: Complex Forms & Wizards (Week 4-5)

**Goal:** Migrate multi-step wizard and complex forms

#### Tasks:
1. **DocumentUploadForm.vue Migration** (Highest Priority)
   - Replace `vue3-form-wizard` with `a-steps`
   - Implement step navigation
   - Migrate all form fields to Ant Design inputs
   - Preserve metadata import functionality
   - Update file upload to `a-upload`

2. **ExcelBatchImport.vue Migration**
   - Use `a-steps` for workflow
   - Migrate table preview to `a-table`
   - Update file parsing UI

3. **Form Validation**
   - Implement Ant Design form rules
   - Add custom validators
   - Error message display

**Component Mapping:**
```vue
<!-- Before (vue3-form-wizard) -->
<form-wizard>
  <tab-content>Step 1</tab-content>
  <tab-content>Step 2</tab-content>
</form-wizard>

<!-- After (Ant Design) -->
<a-steps :current="currentStep">
  <a-step title="Step 1" />
  <a-step title="Step 2" />
</a-steps>
<div class="steps-content">
  <!-- Step content based on currentStep -->
</div>
```

**Deliverables:**
- ✅ DocumentUploadForm fully migrated
- ✅ ExcelBatchImport migrated
- ✅ Step navigation working
- ✅ Form validation complete

**Estimated Time:** 24-32 hours

---

### Phase 5: Modals & Complex UI (Week 6-7)

**Goal:** Migrate complex modal and detail views

#### Tasks:
1. **DocumentDetailModal.vue Migration**
   - Replace Headless UI Dialog with `a-modal`
   - Migrate tabs to `a-tabs`
   - Update nested forms
   - Implement file preview
   - Add edit/save functionality

2. **ImageUpload.vue Migration**
   - Migrate mode selection to `a-radio-group` or `a-segmented`
   - Update upload interface
   - Add progress indicators

3. **Modal State Management**
   - Ensure modal open/close works correctly
   - Handle nested modals
   - Preserve form state

**Component Mapping:**
```vue
<!-- Before (Headless UI) -->
<Dialog :open="isOpen" @close="closeModal">
  <DialogPanel>...</DialogPanel>
</Dialog>

<!-- After (Ant Design) -->
<a-modal
  v-model:open="isOpen"
  @cancel="closeModal"
>
  ...
</a-modal>
```

**Deliverables:**
- ✅ DocumentDetailModal migrated
- ✅ ImageUpload migrated
- ✅ Modal state management working
- ✅ Tabs and nested forms functional

**Estimated Time:** 20-28 hours

---

### Phase 6: Dashboard & Manager (Week 8-9)

**Goal:** Migrate the most complex component (DocumentsManager)

#### Tasks:
1. **Dashboard.vue Migration**
   - Replace custom layout with `a-layout`
   - Add `a-layout-header`, `a-layout-content`
   - Implement navigation menu

2. **DocumentsManager.vue Migration** (Most Complex - 1,257 lines)
   - Break into sub-components:
     - `DocumentTable.vue` (table display)
     - `DocumentActions.vue` (action buttons)
     - `DocumentFilters.vue` (search/filter)
   - Replace Headless UI Menu with `a-dropdown`
   - Migrate table to `a-table`
   - Update pagination
   - Implement batch selection
   - Update all modals

3. **Dropdown Menus**
   - Row actions dropdown
   - Bulk operations dropdown

**Component Mapping:**
```vue
<!-- Before (Headless UI) -->
<Menu as="div">
  <MenuButton>Actions</MenuButton>
  <MenuItems>
    <MenuItem>Action 1</MenuItem>
  </MenuItems>
</Menu>

<!-- After (Ant Design) -->
<a-dropdown>
  <a-button>Actions</a-button>
  <template #overlay>
    <a-menu>
      <a-menu-item>Action 1</a-menu-item>
    </a-menu>
  </template>
</a-dropdown>
```

**Deliverables:**
- ✅ Dashboard layout migrated
- ✅ DocumentsManager broken into sub-components
- ✅ All features working (search, filter, batch operations)
- ✅ Dropdown menus functional

**Estimated Time:** 28-36 hours

---

### Phase 7: Testing & Refinement (Week 10)

**Goal:** Comprehensive testing and bug fixes

#### Tasks:
1. **Functional Testing**
   - All document operations (create, read, update, delete)
   - File uploads (single, batch, ZIP)
   - Excel import workflow
   - METS export and validation
   - Batch operations

2. **UI/UX Testing**
   - Responsive behavior (mobile, tablet, desktop)
   - Modal interactions
   - Form validation
   - Loading states
   - Error handling

3. **Accessibility Testing**
   - Keyboard navigation
   - Screen reader support
   - ARIA labels
   - Focus management

4. **Performance Testing**
   - Table rendering with large datasets
   - Modal open/close performance
   - File upload performance

**Deliverables:**
- ✅ Test results documented
- ✅ All critical bugs fixed
- ✅ Accessibility compliant
- ✅ Performance optimized

**Estimated Time:** 16-24 hours

---

### Phase 8: Cleanup & Documentation (Week 11-12)

**Goal:** Remove old dependencies and finalize migration

#### Tasks:
1. **Remove Old Dependencies**
   ```bash
   npm uninstall tailwindcss @tailwindcss/postcss @tailwindcss/forms @tailwindcss/typography
   npm uninstall @headlessui/vue vue3-form-wizard
   npm uninstall autoprefixer postcss
   ```

2. **Clean Up CSS**
   - Remove unused Tailwind classes
   - Consolidate Ant Design customizations
   - Remove legacy CSS files

3. **Delete Legacy Components**
   - `Dashboard_fixed.vue`
   - `DocumentDetailModal_fixed.vue`
   - `DocumentsManager_old.vue`
   - `DocumentsManager_new.vue`

4. **Update Documentation**
   - Update README with new dependencies
   - Document component structure
   - Add styling guidelines
   - Update developer setup instructions

5. **Code Review & Optimization**
   - Remove unused imports
   - Optimize bundle size
   - Review CSS specificity
   - Ensure consistent styling

**Deliverables:**
- ✅ Old dependencies removed
- ✅ Legacy code deleted
- ✅ Documentation updated
- ✅ Code optimized

**Estimated Time:** 12-16 hours

---

## Technical Details

### Dependency Changes

**Add:**
```json
{
  "dependencies": {
    "ant-design-vue": "^4.2.0",
    "dayjs": "^1.11.10"
  }
}
```

**Remove:**
```json
{
  "dependencies": {
    "@headlessui/vue": "^1.7.23",
    "vue3-form-wizard": "^0.2.4"
  },
  "devDependencies": {
    "tailwindcss": "^4.1.11",
    "@tailwindcss/postcss": "^4.1.11",
    "@tailwindcss/forms": "^0.5.10",
    "@tailwindcss/typography": "^0.5.16",
    "postcss": "^8.5.6",
    "autoprefixer": "^10.4.21"
  }
}
```

**Keep:**
- `vue`, `vue-router`, `pinia`, `axios`
- `xlsx` (Excel parsing)
- `marked` (Markdown rendering)
- `vite` (build tool)

### Component Mapping Reference

| Current | Ant Design | Notes |
|---------|------------|-------|
| Tailwind classes | Ant Design components | Component-based approach |
| Headless UI Dialog | `a-modal` | Built-in backdrop, animations |
| Headless UI Menu | `a-dropdown` + `a-menu` | More features (icons, dividers) |
| vue3-form-wizard | `a-steps` | Need custom navigation logic |
| Custom pagination | `a-pagination` or `a-table` pagination | Built-in, easier to use |
| Custom file upload | `a-upload`, `a-dragger` | Drag-drop, progress built-in |
| Custom tabs | `a-tabs` | Better accessibility |
| Custom buttons | `a-button` | Many variants (primary, danger, etc.) |
| Custom inputs | `a-input`, `a-select`, etc. | Form validation support |
| Custom table | `a-table` | Sort, filter, pagination built-in |

### CSS Architecture

**Current:** `frontend/src/assets/css/tailwind.css` already contains Ant Design customizations!

**Approach:**
1. Keep existing Ant Design CSS customizations
2. Add new customizations as needed
3. Remove Tailwind-specific utilities gradually
4. Use Ant Design theme config for global styling

**Key Customizations to Preserve:**
- Button styles (`.ant-btn-*`)
- Card styles (`.ant-card`)
- Table styles (`.ant-table-*`)
- Form styles (`.ant-input`, `.ant-select-selector`)
- Modal styles (`.ant-modal-*`)
- Custom utilities (gradients, glass effect, hover-lift)

---

## Risk Management

### High-Risk Areas

1. **DocumentsManager.vue (1,257 lines)**
   - **Risk:** Breaking core functionality
   - **Mitigation:** Break into sub-components, extensive testing

2. **Multi-step Wizard (DocumentUploadForm)**
   - **Risk:** Step navigation bugs
   - **Mitigation:** Create reusable wizard wrapper component

3. **Modal State Management**
   - **Risk:** Lost state on modal close
   - **Mitigation:** Test all modal workflows thoroughly

4. **Headless UI Dialog → Ant Modal**
   - **Risk:** Different event handling
   - **Mitigation:** Create wrapper component for consistency

### Medium-Risk Areas

1. **Form Validation**
   - **Risk:** Validation logic changes
   - **Mitigation:** Use Ant Design validation (better!)

2. **Pagination**
   - **Risk:** Custom logic conflicts
   - **Mitigation:** Use built-in Ant Table pagination

3. **File Upload**
   - **Risk:** Different API
   - **Mitigation:** Test all upload scenarios

### Low-Risk Areas

1. Static content pages (Guide.vue)
2. Simple modals (ImageViewer.vue)
3. Basic forms (Login.vue)

---

## Testing Strategy

### Unit Testing
- Component rendering
- Form validation
- Event handling
- State management

### Integration Testing
- Document upload workflow
- Excel import workflow
- METS export workflow
- Batch operations

### E2E Testing
- Full user workflows
- Modal interactions
- Multi-step wizards
- File uploads

### Manual Testing
- Browser compatibility (Chrome, Firefox, Safari)
- Responsive design (mobile, tablet, desktop)
- Accessibility (keyboard navigation, screen readers)
- Performance (large datasets, multiple files)

---

## Success Criteria

### Functional Requirements
- ✅ All existing features work identically
- ✅ No regression in functionality
- ✅ Improved form validation
- ✅ Better error handling

### UI/UX Requirements
- ✅ Consistent design language
- ✅ Improved responsiveness
- ✅ Better accessibility
- ✅ Smoother animations

### Technical Requirements
- ✅ Reduced bundle size (target: <800KB)
- ✅ Faster page loads
- ✅ Less custom CSS (<500 lines)
- ✅ Better code maintainability

### Performance Metrics
- ✅ Initial load: <2s
- ✅ Modal open: <200ms
- ✅ Table render (1000 rows): <500ms
- ✅ File upload: No degradation

---

## Rollback Plan

If critical issues arise:

1. **Git Branch Strategy**
   - Keep `main` branch stable
   - All work in `feature/ant-design-ui` branch
   - Merge only when Phase 7 (Testing) is complete

2. **Rollback Procedure**
   ```bash
   git checkout main
   docker compose down
   docker compose up --build
   ```

3. **Partial Rollback**
   - Revert individual components via Git
   - Keep working components
   - Fix broken components

---

## Timeline Summary

| Phase | Duration | Components | Hours |
|-------|----------|------------|-------|
| 1. Setup & Simple | 1 week | 3 components | 8-12 |
| 2. Auth & Forms | 1 week | 2 components | 12-16 |
| 3. Tables & Lists | 1 week | 2 components | 16-20 |
| 4. Complex Forms | 2 weeks | 2 components | 24-32 |
| 5. Modals & UI | 2 weeks | 2 components | 20-28 |
| 6. Dashboard & Manager | 2 weeks | 2 components | 28-36 |
| 7. Testing | 1 week | All | 16-24 |
| 8. Cleanup | 1-2 weeks | Documentation | 12-16 |
| **TOTAL** | **10-12 weeks** | **13 components** | **~136-184 hours** |

**Note:** Timeline assumes single developer, part-time work (15-20 hours/week)

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Approve migration** or request changes
3. **Begin Phase 1** with setup and simple components
4. **Set up regular check-ins** (weekly)
5. **Create tracking board** (Kanban/Scrum)

---

## Resources

### Documentation
- [Ant Design Vue Docs](https://antdv.com/docs/vue/introduce)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Ant Design Icons](https://www.antdv.com/components/icon)

### Examples
- [Ant Design Vue Pro](https://github.com/vueComponent/ant-design-vue-pro)
- [Ant Design Vue Examples](https://github.com/vueComponent/ant-design-vue/tree/main/site/src/components)

### Migration Guides
- [Tailwind to Ant Design](https://github.com/ant-design/ant-design/discussions/31869)
- [Headless UI to Ant Design](https://ant.design/docs/react/migration-v4)

---

**Document Version:** 1.0
**Last Updated:** 2025-12-14
**Branch:** `feature/ant-design-ui`
**Status:** Ready for Review
