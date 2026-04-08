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
        relative rounded-2xl border backdrop-blur-xl transition-all duration-300 overflow-hidden
        ${isHovered 
          ? 'bg-white/15 border-white/40 shadow-[0_8px_32px_0_rgba(255,255,255,0.1)]' 
          : 'bg-white/5 border-white/20 shadow-[0_8px_32px_0_rgba(255,255,255,0.05)]'
        }
        ${className}
      `}
    >
      {/* Shine effect on hover */}
      {isHovered && (
        <div 
          className="absolute w-40 h-40 bg-white/10 rounded-full blur-3xl pointer-events-none transition-all duration-300"
          style={{
            top: `${mousePos.y - 80}px`,
            left: `${mousePos.x - 80}px`,
          }}
        />
      )}

      {/* Gradient border effect */}
      {isHovered && (
        <div className="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent pointer-events-none rounded-2xl" />
      )}
      
      {/* Content */}
      <div className="relative z-10">
        {children}
      </div>
    </div>
  );
}
