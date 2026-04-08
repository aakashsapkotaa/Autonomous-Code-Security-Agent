import { Globe, Shield } from 'lucide-react';
import GlassFrame from './GlassFrame';

export default function Footer() {
  return (
    <footer className="relative z-20 w-full px-8 py-8 flex flex-col md:flex-row justify-between items-center gap-6 border-t border-outline-variant/20">
      <div className="flex items-center gap-8 text-on-surface-variant text-[10px] uppercase tracking-[0.2em] font-bold">
        <span className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_10px_rgba(255,255,255,0.8)]" />
          Operational Status: Secure
        </span>
        <span className="flex items-center gap-2">
          <Globe className="w-3 h-3" />
          Region: us-east-1
        </span>
      </div>
      
      <div className="flex items-center gap-3 text-xs text-on-surface-variant">
        <GlassFrame className="rounded-full px-4 py-2">
          <a className="hover:text-primary transition-colors" href="#">
            Security Policy
          </a>
        </GlassFrame>
        <GlassFrame className="rounded-full px-4 py-2">
          <a className="hover:text-primary transition-colors" href="#">
            Terminals
          </a>
        </GlassFrame>
        <span className="flex items-center gap-2 px-2">
          <Shield className="w-3 h-3" />
          System v4.2.0
        </span>
      </div>
    </footer>
  );
}
