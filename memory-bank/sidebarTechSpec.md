# Product Requirements Document: Yojna Khojna UI Enhancements

## 1. Sidebar Color Refinement: Professional Gradient Approach

### Overview
Enhance the sidebar button colors using a sophisticated gradient approach to create a more elegant and visually appealing interface while maintaining the government scheme assistant's professional character.

### Requirements
* Implement subtle gradient backgrounds for sidebar buttons.
* Use a deep purple-blue color scheme as the base palette (`#4A55A2` to `#7895CB`).
* Create distinct visual states for default, hover, and active conditions.
* Ensure all colors maintain WCAG AA accessibility compliance (4.5:1 contrast ratio).
* Apply consistent styling across all sidebar elements.

### Design Details
* **Base Gradient:** Linear gradient from deep purple (`#4A55A2`) to blue (`#7895CB`).
* **Active State:** Slightly brighter gradient with increased opacity.
* **Hover State:** Add subtle glow effect with light box shadow.
* **Selected State:** Include thin accent border on the left side.
* **Text Color:** White or light gray for optimal contrast against gradient background.
* **Transition Effects:** Smooth transitions between states (0.2s ease-in-out).

### Expected Impact
* More visually refined and modern interface.
* Improved visual hierarchy of navigation elements.
* Enhanced user experience with subtle interactive feedback.
* More professional and polished appearance.

## 2. Pinned Conversations Feature

### Overview
Allow users to pin up to 3 important conversations to the top of the sidebar for quick access, improving workflow efficiency for frequent users tracking specific schemes.

### Requirements
* Users can pin up to 3 conversations maximum.
* Pinned conversations appear in a dedicated section at the top of the sidebar.
* Visual indicator clearly distinguishes pinned from regular conversations.
* Implement pin/unpin functionality with intuitive UI controls.
* Persist pinned status across sessions using `localStorage`.
* Include helpful empty state when no conversations are pinned.

### User Experience
* **Pinning Action:** Add pin icon button to each conversation item in the sidebar.
* **Pinned Section:** Create visually distinct "Pinned" section above regular conversations.
* **Limit Handling:** When user attempts to pin a 4th conversation, show a tooltip explaining the 3-pin limit.
* **Empty State:** When no conversations are pinned, show subtle helper text explaining the feature.
* **Visual Design:** Pinned conversations receive special styling with gradient accent.

## 3. Discover Schemes Page

### Overview
Create a dedicated "Discover" page accessible via the sidebar that showcases available government schemes in a visually appealing tile format, helping users explore relevant programs.

### Requirements
* Add "Discover" button to the main sidebar navigation using the new gradient styling.
* Create a responsive grid layout of scheme tiles.
* Each tile should include:
    * Scheme name as title
    * AI-generated simple illustration/icon
    * Brief 1-2 sentence description
    * Category tag (e.g., Housing, Education, Agriculture)
* Implement filtering capability by scheme category.
* Ensure mobile responsiveness with appropriately sized tiles.

### User Experience
* **Navigation:** Clicking "Discover" in sidebar transitions to the Discover page.
* **Tile Layout:** Responsive grid with 3-4 tiles per row on desktop, 2 per row on tablet, 1 per row on mobile.
* **Visual Design:** Clean, consistent tile design with subtle shadows and rounded corners.
* **Interaction:** Clicking any tile initiates a new conversation about that scheme.
* **Styling Consistency:** Use complementary gradients for category chips that harmonize with sidebar design.

---

# Technical Specification

## 1. Sidebar Color Refinement: Professional Gradient Approach

### Implementation Approach
* **Create Gradient Utility Module:**
    * Create a dedicated module for gradient definitions.
    * Define base, active, and hover gradient states for sidebar elements.
    * Use `linear-gradient` CSS for consistent cross-browser support.
* **Theme Integration:**
    * Update the MUI theme configuration to include new color definitions.
    * Define component overrides for list items and buttons.
    * Ensure proper contrast ratios for accessibility compliance.
* **Component Styling Guidelines:**
    * Apply gradients via `background` or `backgroundImage` CSS properties.
    * Use `box-shadow` for subtle elevation effects on hover/active states.
    * Implement smooth transitions between states for improved UX.
    * Add left border accent for selected state indication.
* **Consistency Considerations:**
    * Apply the gradient styling consistently across all sidebar elements.
    * Ensure text remains high-contrast and readable against gradient backgrounds.
    * Match styling of new elements (like the Discover button) to this theme.
    * Consider dark/light mode compatibility for future extensions.

## 2. Pinned Conversations Feature

### Data Model Extensions
* **Conversation Schema Updates:**
    * Add `isPinned` boolean flag to the `Conversation` interface.
    * Add optional `pinnedAt` timestamp for sorting pinned conversations.
    * Update type definitions throughout the application.

### Storage Implementation
* **Conversation Service Enhancements:**
    * Add `pin`/`unpin` methods to the conversation service.
    * Implement pin limit validation logic (maximum 3 pins).
    * Update `localStorage` persistence to include pinned status.
    * Add proper error handling for pin limit enforcement.
* **Context API Integration:**
    * Extend the `ConversationContext` to expose `pin`/`unpin` methods.
    * Add proper state updates when pin status changes.
    * Ensure UI refreshes when pin status is modified.

### UI Component Architecture
* **Component Hierarchy:**
    * Create a separate `PinnedConversationsList` component.
    * Update `ConversationListItem` to handle pin/unpin actions.
    * Modify `ConversationList` to incorporate the pinned section.
* **Visual Design Implementation:**
    * Use gradient styling for the pinned section header.
    * Add visual distinction for pinned conversation items.
    * Implement pin/unpin icon button with proper hover states.
    * Add section divider between pinned and regular conversations.
* **Interaction Handling:**
    * Implement click handler for pin/unpin toggle.
    * Add tooltip for pin/unpin action explanation.
    * Create toast notification for pin limit feedback.
    * Prevent event propagation to avoid triggering conversation selection.

## 3. Discover Schemes Page

### Data Architecture
* **Scheme Data Model:**
    * Define `Scheme` and `SchemeCategory` interfaces.
    * Create a static data file for initial scheme information.
    * Plan for future API integration for dynamic scheme data.
* **Category Styling System:**
    * Create a mapping between categories and corresponding colors/gradients.
    * Implement consistent styling rules for category indicators.
    * Ensure proper contrast for category labels.

### Page Implementation
* **Component Structure:**
    * Create a standalone `DiscoverPage` component.
    * Implement category filtering using React state.
    * Use React Router for navigation integration.
    * Develop responsive grid layout for scheme tiles.
* **UI Elements:**
    * Create category filter chips with active state indication.
    * Implement scheme card components with consistent styling.
    * Add hover effects for interactive feedback.
    * Develop empty state for no results condition.
* **Conversation Creation:**
    * Implement scheme-to-conversation transition logic.
    * Create initial message template based on scheme properties.
    * Set up automatic navigation to chat view after selection.
    * Ensure proper conversation context initialization.
* **Routing Integration:**
    * Update the application router to include the Discover page.
    * Add navigation logic in the sidebar component.
    * Implement proper route path handling.
    * Set appropriate default routes and redirects.

### Integration Strategy
* **Shared Resources:**
    * Coordinate gradient definitions between sidebar and Discover page.
    * Ensure consistent typography and spacing throughout the application.
    * Reuse components where appropriate (e.g., Chip components).
* **Testing Strategy:**
    * Component tests for new UI elements.
    * Integration tests for pin/unpin functionality.
    * `localStorage` persistence verification.
    * Visual regression testing for the new gradient styling.
    * Responsive design testing across device sizes.
* **Implementation Phases:**
    * Phase 1: Sidebar gradient styling update
    * Phase 2: Pinned conversations feature
    * Phase 3: Discover page implementation
* **Performance Considerations:**
    * Optimize gradient rendering for smooth scrolling.
    * Implement proper memoization for filtered schemes and conversations.
    * Consider lazy loading for scheme images.
    * Ensure efficient `localStorage` operations.

This technical specification provides a comprehensive blueprint for implementing all three requested features while maintaining the application's existing architecture and patterns.
