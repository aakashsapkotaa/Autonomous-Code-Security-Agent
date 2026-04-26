<script lang="ts">
  import { onMount } from 'svelte';

  interface Particle {
    x: number; y: number;
    vx: number; vy: number;
    radius: number; opacity: number;
    hue: number; pulseSpeed: number; pulsePhase: number;
  }

  let canvas: HTMLCanvasElement;
  let mouse = { x: 0, y: 0 };

  onMount(() => {
    const ctx = canvas.getContext('2d')!;
    const resize = () => { canvas.width = window.innerWidth; canvas.height = window.innerHeight; };
    resize();
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', (e) => { mouse.x = e.clientX; mouse.y = e.clientY; });

    const particles: Particle[] = Array.from({ length: 120 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 1.5,
      vy: (Math.random() - 0.5) * 1.5,
      radius: Math.random() * 3 + 1.5,
      opacity: Math.random() * 0.7 + 0.5,
      hue: Math.random() * 80 + 170,
      pulseSpeed: Math.random() * 0.03 + 0.015,
      pulsePhase: Math.random() * Math.PI * 2,
    }));

    let time = 0;
    let raf: number;

    const animate = () => {
      time += 0.01;
      ctx.fillStyle = 'rgba(0,0,0,0.05)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      particles.forEach((p, i) => {
        const dx = mouse.x - p.x, dy = mouse.y - p.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 250) {
          const f = (250 - dist) / 250;
          p.vx += (dx / dist) * f * 0.08;
          p.vy += (dy / dist) * f * 0.08;
        }
        p.x += p.vx; p.y += p.vy;
        p.vx *= 0.99; p.vy *= 0.99;
        if (p.x - p.radius < 0 || p.x + p.radius > canvas.width) { p.vx *= -0.8; p.x = Math.max(p.radius, Math.min(canvas.width - p.radius, p.x)); }
        if (p.y - p.radius < 0 || p.y + p.radius > canvas.height) { p.vy *= -0.8; p.y = Math.max(p.radius, Math.min(canvas.height - p.radius, p.y)); }

        const pulse = Math.sin(time * p.pulseSpeed + p.pulsePhase) * 0.3 + 1;
        const r = p.radius * pulse, op = p.opacity * pulse;

        const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 4);
        g.addColorStop(0, `hsla(${p.hue},85%,65%,${op})`);
        g.addColorStop(0.4, `hsla(${p.hue},75%,55%,${op * 0.6})`);
        g.addColorStop(1, `hsla(${p.hue},65%,45%,0)`);
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(p.x, p.y, r * 4, 0, Math.PI * 2); ctx.fill();

        ctx.fillStyle = `hsla(${p.hue},95%,75%,${op})`;
        ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, Math.PI * 2); ctx.fill();

        particles.forEach((o, j) => {
          if (i >= j) return;
          const dx2 = p.x - o.x, dy2 = p.y - o.y;
          const d2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);
          if (d2 < 200) {
            const alpha = 0.5 * (1 - d2 / 200);
            const lg = ctx.createLinearGradient(p.x, p.y, o.x, o.y);
            lg.addColorStop(0, `hsla(${p.hue},75%,65%,${alpha})`);
            lg.addColorStop(1, `hsla(${o.hue},75%,65%,${alpha})`);
            ctx.strokeStyle = lg; ctx.lineWidth = 2;
            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(o.x, o.y); ctx.stroke();
          }
        });
      });
      raf = requestAnimationFrame(animate);
    };
    animate();
    return () => { cancelAnimationFrame(raf); window.removeEventListener('resize', resize); };
  });
</script>

<canvas bind:this={canvas} class="fixed top-0 left-0 w-full h-full pointer-events-none z-0"></canvas>
