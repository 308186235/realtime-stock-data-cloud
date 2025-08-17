# Stock Trading System Frontend

This is the frontend module for the AI-driven stock trading system. It's built using uni-app framework for cross-platform compatibility.

## Project Structure

```
frontend/stock5/
├── components/         # Reusable UI components
│   ├── common/         # Common UI elements
│   ├── ai/             # AI-related components
│   └── trade/          # Trading-related components
├── mock/               # Mock data for development
│   ├── index.js        # Mock data entry point
│   ├── stock-data.js   # Stock market mock data
│   ├── trade-data.js   # Trading mock data
│   └── ai-recommendations.js # AI mock responses
├── pages/              # Application pages
├── static/             # Static assets (images, fonts, etc.)
├── utils/              # Utility functions
│   ├── request.js      # Enhanced HTTP request utility
│   └── secure-storage.js # Secure data storage utility
├── env.js              # Environment configuration
├── App.vue             # Application entry component
├── main.js             # Application entry point
└── manifest.json       # Application configuration
```

## Features

- **Cross-Platform**: Works on Web, iOS, Android, and WeChat Mini Program
- **Enhanced Mock Data**: Structured mock data system for development
- **Network Request Optimization**: Enhanced request utility with better error handling
- **Dynamic Environment Configuration**: Auto-detects device IP for better local development

## Development Setup

1. Install dependencies:
   ```
   npm install
   ```

2. Start development server:
   ```
   npm run dev
   ```

3. Build for production:
   ```
   npm run build
   ```

## Key Improvements

1. **Code Organization**:
   - Renamed directories from Chinese to English for better cross-platform compatibility
   - Structured mock data system for more maintainable development

2. **Network Handling**:
   - Enhanced request utility with better error categorization
   - Added request cancellation support
   - Improved mock data integration

3. **Environment Configuration**:
   - Dynamic IP detection for mobile development
   - Separated development and production settings

## Best Practices

1. **Naming Conventions**:
   - Use English for directory and file names
   - Use camelCase for JavaScript variables and functions
   - Use PascalCase for component names

2. **Code Style**:
   - Follow ESLint configuration
   - Document complex functions with JSDoc comments

3. **Testing**:
   - Write unit tests for utilities and services
   - Write component tests for critical UI elements 
 
