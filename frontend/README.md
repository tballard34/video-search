# Frontend Boilerplate

A modern React frontend boilerplate built with TypeScript, Vite, and Tailwind CSS.

## Using This Boilerplate

When using this boilerplate for a new project, update these files:

1. **`package.json`** - Change name from "temp-frontend" to your project name
2. **`index.html`** - Update title, description, author, and Open Graph tags
3. **`public/site.webmanifest`** - Update app name, description, and icon references
4. **Icons/Images** - Replace all temp-prefixed files in `public/images/` with your branding
5. **`tailwind.config.ts`** - Update color scheme if using temp-blue
6. **README.md** - Replace this content with your project-specific information

## Tech Stack

- **pnpm** - Fast, disk-efficient package manager
- **Vite** - Lightning fast build tool and dev server
- **React 19** - UI library with TypeScript support
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible component primitives
- **TanStack Router** - Type-safe client-side routing
- **React Icons** - Popular icon library
- **Vitest** - Fast unit testing framework
- **ESLint + Prettier** - Code formatting and linting
- **Vercel** - Deployment platform ready

## Getting Started

### Prerequisites

Make sure you have [pnpm](https://pnpm.io/) installed:

```bash
npm install -g pnpm
```

### Installation

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test

# Preview production build
pnpm preview
```

### Development

The app will be available at `http://localhost:5173` when running in development mode.

### Code Quality

```bash
# Run linter
pnpm lint

# Fix linting issues
pnpm lint:fix

# Format code
pnpm format

# Check formatting
pnpm format:check
```

### Testing

Run the test suite with:

```bash
pnpm test
```

For interactive testing:

```bash
pnpm test:ui
```

### Building

Build the app for production:

```bash
pnpm build
```

The built files will be in the `dist` directory.

## Project Structure

```
src/
├── components/          # React components
│   ├── ui/             # Reusable UI components
│   └── __tests__/      # Component tests
├── lib/                # Utility functions
├── routes/             # TanStack Router routes
│   ├── __root.tsx      # Root route layout
│   └── index.tsx       # Home page route
├── test/               # Test configuration
├── main.tsx            # App entry point
├── routeTree.gen.ts    # Generated route tree (auto-generated)
└── index.css           # Global styles
```

## Routing

This boilerplate uses [TanStack Router](https://tanstack.com/router) for type-safe routing. Routes are defined in the `src/routes/` directory using file-based routing.

- The route tree is automatically generated in `routeTree.gen.ts`
- TanStack Router DevTools are included in development mode

## Deployment

This project is configured for deployment on Vercel. Simply connect your repository to Vercel and it will automatically deploy when you push to main.

### Manual Deployment

1. Build the project: `pnpm build`
2. Deploy the `dist` directory to your hosting platform

## Features

- ⚡️ Lightning fast development with Vite
- 🔥 Hot module replacement
- 📝 TypeScript support
- 🎨 Tailwind CSS for styling
- 🧭 Type-safe routing with TanStack Router
- 🧪 Testing setup with Vitest
- 📏 ESLint + Prettier for code quality
- 🚀 Ready for Vercel deployment
