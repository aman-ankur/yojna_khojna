# Technical Specification

## Data Models

1.  **Conversation Object**

    ```typescript
    interface Conversation {
      id: string;             // Unique identifier for the conversation
      title: string;          // AI-generated title
      messages: Message[];    // Array of messages in the conversation
      createdAt: string;      // ISO timestamp of creation
      updatedAt: string;      // ISO timestamp of last update
    }

    interface Message {
      id: string;             // Unique identifier for the message
      role: 'user' | 'assistant'; // Who sent the message
      content: string;        // Message content
      timestamp: string;      // ISO timestamp
    }
    ```

2.  **User Identity**

    ```typescript
    interface UserIdentity {
      browserId: string;      // Random UUID generated for the browser
      createdAt: string;      // When this ID was created
    }
    ```

## Storage Architecture

### LocalStorage Schema