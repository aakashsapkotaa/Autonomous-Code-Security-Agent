import { AtSign, Lock } from 'lucide-react';

interface InputProps {
  id: string;
  label: string;
  type: string;
  placeholder: string;
  icon?: 'email' | 'lock';
  helperLink?: {
    text: string;
    href: string;
  };
}

export default function Input({ id, label, type, placeholder, icon, helperLink }: InputProps) {
  const IconComponent = icon === 'email' ? AtSign : icon === 'lock' ? Lock : null;

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between items-center">
        <label 
          className="text-xs font-bold uppercase tracking-widest text-on-surface-variant" 
          htmlFor={id}
        >
          {label}
        </label>
        {helperLink && (
          <a 
            className="text-xs text-primary/70 hover:text-primary transition-colors" 
            href={helperLink.href}
          >
            {helperLink.text}
          </a>
        )}
      </div>
      <div className="relative group">
        {IconComponent && (
          <IconComponent className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-on-surface-variant/50 group-focus-within:text-primary transition-colors" />
        )}
        <input
          className={`w-full bg-surface-container-low border-0 rounded-xl py-4 ${IconComponent ? 'pl-12' : 'pl-4'} pr-4 text-on-background placeholder:text-outline/50 focus:ring-2 focus:ring-primary/50 transition-all outline-none`}
          id={id}
          placeholder={placeholder}
          type={type}
        />
      </div>
    </div>
  );
}
