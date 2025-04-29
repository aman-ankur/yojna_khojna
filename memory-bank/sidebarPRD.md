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
