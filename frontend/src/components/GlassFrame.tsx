'use client';

import { ReactNode, useState, MouseEvent } from 'react';

interface GlassFrameProps {
  children: ReactNode;
  className?: string;
}

export default function GlassFrame({ children, className = '' }: GlassFrameProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setMousePos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  return (
    <div
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onMouseMove={handleMouseMove}
      className={`
        relative overflow-hidden rounded-2xl border backdrop-blur-2xl transition-all duration-300
        ${isHovered 
          ? 'bg-white/10 border-white/24 shadow-[0_18px_44px_-26px_rgba(255,255,255,0.16)]' 
          : 'bg-white/6 border-white/10 shadow-[0_18px_44px_-30px_rgba(255,255,255,0.1)]'
        }
        ${className}
      `}
    >
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-white/[0.1] via-white/[0.025] to-transparent" />

      {/* Shine effect on hover */}
      {isHovered && (
        <div 
          className="pointer-events-none absolute h-40 w-40 rounded-full bg-white/10 blur-3xl transition-all duration-300"
          style={{
            top: `${mousePos.y - 80}px`,
            left: `${mousePos.x - 80}px`,
          }}
        />
      )}

      {/* Gradient border effect */}
      {isHovered && (
        <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-white/18 via-transparent to-transparent" />
      )}
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
