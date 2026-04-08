# Autonomous-Code-Security-Agent

# SecureShift Dashboard

A Next.js + Tailwind CSS dashboard with reusable components, featuring a modern cyberpunk-inspired design for security monitoring and analysis.

## Features

- Next.js 15 with App Router
- TypeScript
- Tailwind CSS 4 with custom design tokens
- Framer Motion animations
- Reusable component architecture
- Custom design system with Material Design 3 tokens
- Glass-morphism UI effects
- Responsive layout

## Project Structure

```
app/
├── layout.tsx          # Root layout with fonts
├── page.tsx            # Main page composition
└── globals.css         # Global styles

components/
├── Header.tsx          # Top navigation
├── Footer.tsx          # Bottom info bar
├── HeroSection.tsx     # Left hero content
├── LoginForm.tsx       # Right login panel
└── ui/
    ├── Button.tsx      # Reusable button component
    └── Input.tsx       # Reusable input component
```

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Component Architecture

### Reusable UI Components

- **Button**: Supports primary/secondary variants, icons, and full-width mode
- **Input**: Includes label, icon support, and helper links

### Page Components

- **Header**: Brand logo and help button
- **HeroSection**: Animated hero content with stats
- **LoginForm**: Glass-morphism login panel with social auth
- **Footer**: Status indicators and links

## Design System

The application uses a custom cyberpunk-inspired design system with:
- Custom color palette (neon blues, purples, and oranges)
- Material Design 3 naming conventions
- Glass-morphism effects
- Neon glow shadows
- Mesh gradient backgrounds

Design tokens are defined in `app/globals.css` using Tailwind v4's `@theme` directive.

## Build for Production

```bash
npm run build
npm start
```

## Technologies

- **Framework**: Next.js 15
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Fonts**: Inter & Space Grotesk (Google Fonts)

## License

Apache-2.0
