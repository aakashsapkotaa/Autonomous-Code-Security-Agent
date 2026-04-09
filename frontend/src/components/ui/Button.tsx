import { ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  type?: 'button' | 'submit';
  variant?: 'primary' | 'secondary';
  fullWidth?: boolean;
  icon?: ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export default function Button({ 
  children, 
  type = 'button', 
  variant = 'primary', 
  fullWidth = false,
  icon,
  onClick,
  disabled = false
}: ButtonProps) {
  const baseStyles = 'font-headline font-bold py-4 rounded-xl transition-all cursor-pointer';
  const widthStyles = fullWidth ? 'w-full' : '';
  
  const variantStyles = {
    primary: 'bg-gradient-to-r from-white to-zinc-300 text-black shadow-[0_16px_40px_-18px_rgba(255,255,255,0.65)] hover:scale-[1.02] active:scale-[0.98]',
    secondary: 'flex items-center justify-center gap-3 bg-surface-container-highest hover:bg-surface-bright text-on-surface border border-white/10 group',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${widthStyles} ${variantStyles[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
    >
      {icon && icon}
      {children}
    </button>
  );
}
