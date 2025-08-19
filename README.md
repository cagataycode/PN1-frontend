# PN1 Frontend

A clean, minimal Expo React Native project built with TypeScript and Expo Router.

## Features

- **Expo Router**: File-based routing for React Native
- **TypeScript**: Full TypeScript support
- **Theme Support**: Light and dark mode support
- **Clean Architecture**: Minimal boilerplate, ready for development

## Getting Started

1. Install dependencies:

   ```bash
   npm install
   ```

2. Start the development server:

   ```bash
   npm start
   ```

3. Run on your preferred platform:
   - **iOS**: `npm run ios`
   - **Android**: `npm run android`
   - **Web**: `npm run web`

## Project Structure

```
PN1-frontend/
├── app/                 # App screens and routing
│   ├── _layout.tsx     # Root layout
│   ├── index.tsx       # Home screen
│   └── +not-found.tsx  # 404 page
├── components/          # Reusable components
│   ├── ThemedText.tsx  # Themed text component
│   └── ThemedView.tsx  # Themed view component
├── constants/           # App constants
│   └── Colors.ts       # Theme colors
├── hooks/               # Custom hooks
│   └── useColorScheme.ts # Color scheme hook
└── package.json         # Dependencies and scripts
```

## Development

This project is set up with:

- ESLint for code quality
- TypeScript for type safety
- Expo for cross-platform development

## License

This project is private and proprietary.
