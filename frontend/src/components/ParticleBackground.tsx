'use client';

import { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  opacity: number;
  hue: number;
  pulseSpeed: number;
  pulsePhase: number;
}

export default function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Track mouse position
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Particle array
    const particles: Particle[] = [];
    const particleCount = 80;

    // Initialize particles with vibrant colors
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 1.2,
        vy: (Math.random() - 0.5) * 1.2,
        radius: Math.random() * 2.5 + 1,
        opacity: Math.random() * 0.6 + 0.4,
        hue: Math.random() * 60 + 180, // Blue to cyan range
        pulseSpeed: Math.random() * 0.02 + 0.01,
        pulsePhase: Math.random() * Math.PI * 2,
      });
    }

    let time = 0;

    // Animation loop
    const animate = () => {
      time += 0.01;

      // Clear canvas with fade effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Update and draw particles
      particles.forEach((particle, index) => {
        // Mouse interaction - attract particles to mouse
        const dx = mouseRef.current.x - particle.x;
        const dy = mouseRef.current.y - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 200) {
          const force = (200 - distance) / 200;
          particle.vx += (dx / distance) * force * 0.05;
          particle.vy += (dy / distance) * force * 0.05;
        }

        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Add slight damping
        particle.vx *= 0.99;
        particle.vy *= 0.99;

        // Bounce off walls with energy
        if (particle.x - particle.radius < 0 || particle.x + particle.radius > canvas.width) {
          particle.vx *= -0.8;
          particle.x = Math.max(particle.radius, Math.min(canvas.width - particle.radius, particle.x));
        }
        if (particle.y - particle.radius < 0 || particle.y + particle.radius > canvas.height) {
          particle.vy *= -0.8;
          particle.y = Math.max(particle.radius, Math.min(canvas.height - particle.radius, particle.y));
        }

        // Pulsing effect
        const pulse = Math.sin(time * particle.pulseSpeed + particle.pulsePhase) * 0.3 + 1;
        const currentRadius = particle.radius * pulse;
        const currentOpacity = particle.opacity * pulse;

        // Draw particle with glow
        const gradient = ctx.createRadialGradient(
          particle.x, particle.y, 0,
          particle.x, particle.y, currentRadius * 3
        );
        gradient.addColorStop(0, `hsla(${particle.hue}, 80%, 60%, ${currentOpacity})`);
        gradient.addColorStop(0.5, `hsla(${particle.hue}, 70%, 50%, ${currentOpacity * 0.5})`);
        gradient.addColorStop(1, `hsla(${particle.hue}, 60%, 40%, 0)`);

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, currentRadius * 3, 0, Math.PI * 2);
        ctx.fill();

        // Draw core
        ctx.fillStyle = `hsla(${particle.hue}, 90%, 70%, ${currentOpacity})`;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, currentRadius, 0, Math.PI * 2);
        ctx.fill();

        // Draw connections to nearby particles
        particles.forEach((otherParticle, otherIndex) => {
          if (index < otherIndex) {
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 180) {
              const opacity = 0.4 * (1 - distance / 180);
              const avgHue = (particle.hue + otherParticle.hue) / 2;
              
              // Create gradient for line
              const lineGradient = ctx.createLinearGradient(
                particle.x, particle.y,
                otherParticle.x, otherParticle.y
              );
              lineGradient.addColorStop(0, `hsla(${particle.hue}, 70%, 60%, ${opacity})`);
              lineGradient.addColorStop(1, `hsla(${otherParticle.hue}, 70%, 60%, ${opacity})`);

              ctx.strokeStyle = lineGradient;
              ctx.lineWidth = 1.5;
              ctx.beginPath();
              ctx.moveTo(particle.x, particle.y);
              ctx.lineTo(otherParticle.x, otherParticle.y);
              ctx.stroke();
            }
          }
        });
      });

      requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed top-0 left-0 w-full h-full pointer-events-none z-0"
    />
  );
}
