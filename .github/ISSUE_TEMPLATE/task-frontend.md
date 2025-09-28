---
name: Frontend Development Task
about: Create a task for frontend UI, components, or user experience implementation
title: "[T-XXX] Frontend Task: "
labels: ["task", "frontend", "ui"]
assignees: []
---

## Task Overview
**Story Reference**: S-XXX - Story Name
**Epic**: OSINT Research Platform
**Estimated Hours**: XX-XX hours
**Priority**: [Highest/High/Medium/Low]

## Implementation Phases

### Phase 1: Component Design & Setup (X hours)
- [ ] Create component structure and types
- [ ] Set up testing framework and utilities
- [ ] Design component API and props interface
- [ ] Create mock data and fixtures

### Phase 2: Core Implementation (X hours)
- [ ] Implement base component functionality
- [ ] Add state management and effects
- [ ] Implement user interactions and events
- [ ] Add styling and responsive design

### Phase 3: Integration & Testing (X hours)
- [ ] Integrate with backend API
- [ ] Add error handling and loading states
- [ ] Implement accessibility features
- [ ] Write comprehensive tests

## Component Specification

### Component Structure
```tsx
interface ComponentProps {
  prop1: Type;
  prop2: Type;
  onAction?: (data: Type) => void;
}

const Component: React.FC<ComponentProps> = ({ prop1, prop2, onAction }) => {
  // Implementation
};
```

### State Management
```tsx
interface ComponentState {
  data: Type[];
  loading: boolean;
  error: string | null;
}
```

### API Integration
```typescript
// API service calls
const fetchData = async (params: Parameters): Promise<Response> => {
  // Implementation
};
```

## User Experience Requirements

### User Interface
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Consistent styling with design system
- [ ] Loading states and progress indicators
- [ ] Error messages and user feedback

### Accessibility
- [ ] ARIA labels and roles
- [ ] Keyboard navigation support
- [ ] Screen reader compatibility
- [ ] Color contrast compliance

### Performance
- [ ] Component lazy loading
- [ ] Memoization for expensive calculations
- [ ] Optimized re-renders
- [ ] Bundle size optimization

## Testing Requirements

### Unit Tests (Jest + Testing Library)
- [ ] `test_component_renders_correctly`
- [ ] `test_user_interactions`
- [ ] `test_error_handling`
- [ ] `test_accessibility_features`

### Integration Tests
- [ ] API integration and data flow
- [ ] Component interaction testing
- [ ] Form validation and submission
- [ ] Navigation and routing tests

### E2E Tests (Playwright)
- [ ] Complete user workflow tests
- [ ] Cross-browser compatibility
- [ ] Mobile responsiveness
- [ ] Performance testing

## Styling and Design

### CSS/SCSS Structure
```scss
.component {
  // Base styles

  &__element {
    // Element styles
  }

  &--modifier {
    // Modifier styles
  }
}
```

### Design Tokens
- [ ] Use consistent colors and typography
- [ ] Follow spacing and layout guidelines
- [ ] Implement design system components
- [ ] Maintain theme consistency

## AI Coding Brief
```yaml
role: "You are a senior frontend engineer practicing component-driven development."
objective: "Create accessible, performant React components with comprehensive testing."
constraints:
  allowed_paths:
    - frontend/src/components/
    - frontend/src/pages/
    - frontend/src/hooks/
    - frontend/src/services/
    - frontend/src/types/
    - frontend/src/tests/
  framework: "React with TypeScript, React Testing Library, Playwright"
  testing: "Write tests for all user interactions and edge cases"
  accessibility: "Ensure WCAG 2.1 AA compliance"
  security:
    - "NEVER include author attribution in commits or code"
    - "Do not reference AI assistance in any deliverables"
    - "Sanitize all user inputs and API responses"
tests_to_make_pass:
  - frontend/src/tests/**/*.test.tsx
definition_of_done:
  - "All component tests pass with >95% coverage"
  - "Accessibility tests pass with axe-core"
  - "E2E tests verify user workflows"
  - "Performance budgets are met"
  - "TypeScript compilation is error-free"
  - "Design system guidelines followed"
  - "No attribution or AI references in code/commits"
```

## Performance Targets
- **Bundle Size**: Component < 50KB gzipped
- **Render Time**: First paint < 100ms
- **Interaction**: Response time < 16ms
- **Accessibility**: Lighthouse score > 95

## Browser Support
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

## Completion Criteria
- [ ] Component implemented with full functionality
- [ ] Responsive design working across breakpoints
- [ ] All tests passing with adequate coverage
- [ ] Accessibility requirements met
- [ ] Performance targets achieved
- [ ] Integration with backend APIs complete
- [ ] Code review completed and approved

---
**Links**:
- Task File: `planning/tasks/T-XXX-task-name.md`
- Related Story: `planning/stories/S-XXX-story-name.md`
- Design System: `frontend/src/components/design-system/`
- Storybook: `frontend/storybook/`