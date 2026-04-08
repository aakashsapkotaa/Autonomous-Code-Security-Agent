# SecureShift Dashboard

A Next.js + Tailwind CSS dashboard with reusable components, featuring a modern cyberpunk-inspired design.

## Features

- Next.js 15 with App Router
- TypeScript
- Tailwind CSS 4
- Framer Motion animations
- Reusable component architecture
- Custom design system with Material Design 3 tokens

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

## Customization

Design tokens are defined in `tailwind.config.ts`. Modify colors, fonts, and spacing there to match your brand.

## Build

```bash
npm run build
npm start
```
