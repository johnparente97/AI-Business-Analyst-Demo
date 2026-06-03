# DataInsight AI — React Frontend

A standalone client-side business analytics SPA built with React 19, TypeScript, and Vite.

## Features

- **Data Import**: Upload CSV/JSON files, fetch from public APIs, or use preset datasets
- **Instant Analytics**: Automatic numeric/categorical field detection, statistics, and trend analysis
- **AI Chat**: Multi-provider LLM integration (Gemini, Groq, OpenAI, Anthropic) with streaming responses
- **Dark Mode**: System-aware with manual toggle
- **Responsive Design**: Glassmorphism UI with smooth animations

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | React 19 + TypeScript |
| Build | Vite 8 |
| Styling | Tailwind CSS 4 |
| State | Zustand 5 |
| Charts | Recharts 3 |
| Icons | Lucide React |
| CSV Parsing | PapaParse |

## Getting Started

```bash
npm install
npm run dev
```

The app runs at `http://localhost:5173` by default.

## Project Structure

```
src/
├── components/          # UI components
│   ├── dashboard/       # Dashboard sub-components (stats, charts, table)
│   ├── chat/            # AI chat sub-components (messages, markdown, suggestions)
│   ├── LandingView.tsx  # Landing page with data import options
│   ├── Dashboard.tsx    # Main analytics dashboard
│   ├── ChatPanel.tsx    # AI chat interface
│   ├── DataImportPanel.tsx  # Data import modal
│   └── AISetupModal.tsx # LLM provider configuration
├── store/               # Zustand state management
├── hooks/               # Custom React hooks
├── types/               # TypeScript type definitions
└── utils/
    ├── analyze.ts       # Core analytics engine
    ├── parsers.ts       # CSV/JSON parsing
    ├── fetcher.ts       # API data fetching with presets
    └── llm/             # Multi-provider LLM integration
```

## Configuration

AI features require an API key from one of the supported providers. Configure via the AI Setup modal in the app — keys are stored in browser localStorage.

> **Note**: Anthropic's API does not support direct browser requests (CORS). Use Gemini, Groq, or OpenAI for browser-based usage.
