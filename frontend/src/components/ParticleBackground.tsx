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
    const particleCount = 120; // Increased from 80

    // Initialize particles with vibrant colors
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 1.5, // Increased speed
        vy: (Math.random() - 0.5) * 1.5,
        radius: Math.random() * 3 + 1.5, // Larger particles
        opacity: Math.random() * 0.7 + 0.5, // More visible
        hue: Math.random() * 80 + 170, // Wider color range (cyan to purple)
        pulseSpeed: Math.random() * 0.03 + 0.015,
        pulsePhase: Math.random() * Math.PI * 2,
      });
    }

    let time = 0;

    // Animation loop
    const animate = () => {
      time += 0.01;

      // Clear canvas with fade effect
      ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; // Slower fade for more trails
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Update and draw particles
      particles.forEach((particle, index) => {
        // Mouse interaction - attract particles to mouse
        const dx = mouseRef.current.x - particle.x;
        const dy = mouseRef.current.y - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 250) { // Increased interaction radius
          const force = (250 - distance) / 250;
          particle.vx += (dx / distance) * force * 0.08; // Stronger attraction
          particle.vy += (dy / distance) * force * 0.08;
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
          particle.x, particle.y, currentRadius * 4 // Larger glow
        );
        gradient.addColorStop(0, `hsla(${particle.hue}, 85%, 65%, ${currentOpacity})`);
        gradient.addColorStop(0.4, `hsla(${particle.hue}, 75%, 55%, ${currentOpacity * 0.6})`);
        gradient.addColorStop(1, `hsla(${particle.hue}, 65%, 45%, 0)`);

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, currentRadius * 4, 0, Math.PI * 2);
        ctx.fill();

        // Draw core
        ctx.fillStyle = `hsla(${particle.hue}, 95%, 75%, ${currentOpacity})`;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, currentRadius, 0, Math.PI * 2);
        ctx.fill();

        // Draw connections to nearby particles
        particles.forEach((otherParticle, otherIndex) => {
          if (index < otherIndex) {
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 200) { // Increased connection distance
              const opacity = 0.5 * (1 - distance / 200); // More visible connections
              const avgHue = (particle.hue + otherParticle.hue) / 2;
              
              // Create gradient for line
              const lineGradient = ctx.createLinearGradient(
                particle.x, particle.y,
                otherParticle.x, otherParticle.y
              );
              lineGradient.addColorStop(0, `hsla(${particle.hue}, 75%, 65%, ${opacity})`);
              lineGradient.addColorStop(1, `hsla(${otherParticle.hue}, 75%, 65%, ${opacity})`);

              ctx.strokeStyle = lineGradient;
              ctx.lineWidth = 2; // Thicker lines
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
