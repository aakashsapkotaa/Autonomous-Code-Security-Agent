import { Globe, Shield } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="w-full px-8 py-8 flex flex-col md:flex-row justify-between items-center gap-6 border-t border-outline-variant/10">
      <div className="flex items-center gap-8 text-on-surface-variant text-[10px] uppercase tracking-[0.2em] font-bold">
        <span className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_8px_rgba(129,236,255,0.8)]" />
          Operational Status: Secure
        </span>
        <span className="flex items-center gap-2">
          <Globe className="w-3 h-3" />
          Region: us-east-1
        </span>
      </div>
      
      <div className="flex items-center gap-6 text-xs text-on-surface-variant">
        <a className="hover:text-primary transition-colors" href="#">
          Security Policy
        </a>
        <a className="hover:text-primary transition-colors" href="#">
          Terminals
        </a>
        <span className="flex items-center gap-2">
          <Shield className="w-3 h-3" />
          System v4.2.0
        </span>
      </div>
    </footer>
  );
}
