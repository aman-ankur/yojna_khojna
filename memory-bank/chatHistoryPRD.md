# Product Requirements Document: Conversation History Feature

## Overview
The Conversation History feature will allow users to maintain multiple persistent conversations with the Yojna Khojna assistant without requiring user authentication. Conversations will be automatically saved and accessible via a sidebar, enabling users to revisit previous interactions.

## User Experience Goals
* Users can maintain up to 25 separate conversations
* Conversations persist between browser sessions
* Users can easily switch between conversations
* Each conversation has an AI-generated title based on content
* Users can delete unwanted conversations

## Feature Details
1.  **Conversation Management**
    * New Conversation: Users can start a new conversation at any time via a prominent button in the sidebar
    * Switching: Users can switch between conversations by clicking on items in the sidebar
    * Persistence: All conversations are automatically saved to `localStorage` and remain accessible after browser restarts
    * Limit: System supports up to 25 conversations per browser/device
2.  **Conversation Sidebar**
    * Location: Left side of the interface (collapsible on mobile)
    * Elements:
        * List of existing conversations with AI-generated titles and dates
        * "New Conversation" button at the top
        * Current conversation visually highlighted
    * Organization: Conversations listed in reverse chronological order (newest first)
    * Responsiveness: Sidebar collapses/expands appropriately on different screen sizes
3.  **Conversation Identification**
    * Titles: AI automatically generates a title after 2-3 exchanges based on conversation content
    * Timestamps: Each conversation displays its creation date and last update time
    * Preview: Shows a snippet of the first user message when hovering (optional)
4.  **Conversation Actions**
    * Delete: Each conversation has a delete option (with confirmation dialog)
    * Future v2: Rename functionality will be added in v2
5.  **Implementation Approach**
    * Hybrid Storage:
        * Active conversation maintained in React state for performance
        * All conversations periodically synced to `localStorage` for persistence
    * Unique browser identifier created and stored if none exists

## Success Criteria
* Users can successfully maintain multiple conversations that persist between sessions
* Switching between conversations is intuitive and maintains complete conversation history
* Conversation titles meaningfully reflect the conversation content
* System properly handles the 25 conversation limit
* Delete functionality works reliably