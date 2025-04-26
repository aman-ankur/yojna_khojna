# Yojna Khojna Frontend

This is the frontend for the Yojna Khojna application, a conversational AI interface for asking questions about government schemes.

## Technologies Used

- React.js
- TypeScript
- Chakra UI for components and styling
- Axios for API communication

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)

### Installation

1. Clone the repository
2. Navigate to the frontend directory
3. Install dependencies:

```bash
npm install
```

4. Start the development server:

```bash
npm run dev
```

This will start the development server, typically on http://localhost:5173.

## Project Structure

```
frontend/
├── src/              # Source code
│   ├── components/   # React components
│   ├── services/     # API services
│   ├── App.tsx       # Main App component
│   └── main.tsx      # Entry point
├── public/           # Static assets
└── package.json      # Project dependencies
```

## Backend Connection

The frontend connects to the backend API at `http://localhost:8000` by default. If you need to change this URL, update it in the `services/api.ts` file.

## Features

- Simple chat interface for asking questions about government schemes
- Real-time conversation with the AI
- Responsive design works on desktop and mobile

## Additional Information

This project is part of the Yojna Khojna application, which uses a RAG (Retrieval Augmented Generation) approach to provide accurate information about government schemes in India.
