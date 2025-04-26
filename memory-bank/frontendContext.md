# Frontend Context: Yojna Khojna Chat Interface

This document details the architecture, technology stack, and key decisions specifically for the frontend application.

## Core Technologies

*   **Framework:** React.js (v19)
*   **Language:** TypeScript
*   **Build Tool:** Vite
*   **UI Library:** Material UI (MUI) v5
    *   *Rationale:* Initially started with Chakra UI, but switched to MUI due to persistent integration/build issues encountered with Chakra UI v3 and the Vite/React 19 setup. MUI provides a mature, comprehensive set of components and theming capabilities.
*   **API Client:** Axios
    *   *Rationale:* Standard, promise-based HTTP client for browser environments.
*   **Styling:** Emotion (via MUI), global CSS (`App.css` for resets/base styles)
*   **Testing:**
    *   Runner/Framework: Vitest
    *   Utilities: React Testing Library (RTL)
    *   DOM Assertions: `@testing-library/jest-dom`
    *   User Interactions: `@testing-library/user-event`
    *   Environment: `jsdom`
    *   Mocking: `vi` (built-in with Vitest)

## Project Structure (`frontend/`)

```
frontend/
├── public/           # Static assets (e.g., index.html, favicons)
├── src/
│   ├── __tests__/    # Vitest tests for top-level components (e.g., App.test.tsx)
│   ├── assets/       # Static assets bundled with the app (images, etc.)
│   ├── components/   # Reusable React components
│   │   ├── __tests__/ # Tests specific to components
│   │   ├── ChatContainer.tsx  # Main container for chat functionality
│   │   ├── ChatInput.tsx      # Enhanced input with image upload
│   │   ├── ChatMessages.tsx   # Message display components
│   │   ├── LanguageToggle.tsx # Language context and toggle control
│   │   ├── Sidebar.tsx        # Navigation sidebar
│   │   ├── SuggestedPrompts.tsx # Prompt suggestion cards
│   │   └── WelcomeHeader.tsx  # Welcome screen header
│   ├── services/     # API communication logic
│   │   └── api.ts      # Axios instance setup and API service functions
│   ├── theme/        # MUI theme customization
│   │   └── index.ts    # Theme configuration object
│   ├── App.css       # Global CSS styles/resets
│   ├── App.tsx       # Main application component (routing, layout)
│   ├── index.css     # Global styles including animations
│   ├── main.tsx      # Application entry point (renders App)
│   ├── setupTests.ts # Vitest setup (e.g., import jest-dom, mock globals)
│   └── vite-env.d.ts # TypeScript definitions for Vite env variables
├── .eslintrc.cjs     # ESLint configuration
├── index.html        # Main HTML file template (entry point for Vite)
├── package.json      # Project dependencies and scripts
├── tsconfig.json     # Base TypeScript configuration
├── tsconfig.app.json # TypeScript configuration for the application code
├── tsconfig.node.json# TypeScript configuration for Vite/Node.js context
└── vite.config.ts    # Vite build tool configuration (including Vitest config)
```

## Key Components

*   **`App.tsx`**: Main application wrapper. Sets up MUI `ThemeProvider`, `CssBaseline`, `LanguageProvider` and the overall layout. Renders `Sidebar` and `ChatContainer` in a flex layout.

*   **`ChatContainer.tsx`**: The core container component that manages chat state and conditional rendering between welcome screen and chat view. Handles message state, API calls, and renders appropriate sub-components.

*   **`WelcomeHeader.tsx`**: Displays personalized greeting with gradient text effects. Includes language toggle and welcome text in the selected language.

*   **`SuggestedPrompts.tsx`**: Grid of clickable prompt cards that help users start conversations with common questions.

*   **`ChatMessages.tsx`**: Displays conversation history with styled message bubbles for user and assistant. Includes typing indicator for loading state.

*   **`ChatInput.tsx`**: Enhanced input field with attachment and image upload capabilities. Features a gradient send button and character counter.

*   **`Sidebar.tsx`**: Minimalist navigation sidebar with icon buttons. Responsive design that collapses on mobile.

*   **`LanguageToggle.tsx`**: Provides language context (Hindi/English) with translations and a toggle button. Uses React Context API for language state management.

## State Management

*   **Local Component State:** Uses React `useState` hooks within components to manage UI state (messages, input values, loading states, etc.).
*   **Context API:** Implements React Context for language preferences (`LanguageContext`) to provide translations throughout the app.
*   *Future Consideration:* If complexity grows (e.g., user sessions, global settings), consider adopting a dedicated state management library like Zustand or Redux Toolkit.

## UI Design

*   **Inspiration:** UI design based on Claude AI's interface with clean, minimalist aesthetics.
*   **Key Features:**
    *   Gradient text effects for headers and buttons
    *   Distinct styling for user and assistant message bubbles
    *   Subtle background patterns using CSS gradients
    *   Smooth animations for typing indicators and message transitions
    *   Responsive design with mobile-specific adaptations

## API Communication

*   Centralized in `src/services/api.ts`.
*   Uses an Axios instance with base URL configured for the backend (`http://localhost:8000`).
*   Provides typed functions (`chatService.sendMessage`) for interacting with backend endpoints.
*   Includes basic error handling (logs errors, throws them for components to catch).

## Styling and Theming

*   Uses MUI `ThemeProvider` in `App.tsx`.
*   Custom theme options defined in `src/theme/index.ts`:
    *   Purple-based color palette to match Claude-style design
    *   Typography settings for consistent text sizing
    *   Component overrides for buttons, inputs, and cards
*   Gradient effects using CSS background gradients with text clipping
*   Animations defined in global CSS (`index.css`) for reusability
*   Primarily uses MUI's `sx` prop with Emotion for component styling

## Internationalization

*   Custom implementation using React Context API (`LanguageContext`).
*   Supports Hindi and English languages.
*   Translation strings defined in the `LanguageToggle.tsx` component.
*   Language toggle button in the UI for user control.
*   Automatically formats interface text based on selected language.

## Testing Strategy

*   **Unit/Component Tests:** Using Vitest and React Testing Library.
    *   Testing component rendering, interactions, and state changes.
    *   Mocking API calls, language context, and browser features.
    *   Verifying UI behavior in different states (loading, error, etc.).
*   **Setup:** Test configuration within `vite.config.ts`, setup file `src/setupTests.ts` for global mocks/imports.
*   **Goal:** Ensure components function correctly in isolation and catch regressions during development. 