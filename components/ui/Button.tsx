import { ReactNode } from 'react';

interface ButtonProps {
  children: ReactNode;
  type?: 'button' | 'submit';
  variant?: 'primary' | 'secondary';
  fullWidth?: boolean;
  icon?: ReactNode;
  onClick?: () => void;
}

export default function Button({ 
  children, 
  type = 'button', 
  variant = 'primary', 
  fullWidth = false,
  icon,
  onClick 
}: ButtonProps) {
  const baseStyles = 'font-headline font-bold py-4 rounded-xl transition-all cursor-pointer';
  const widthStyles = fullWidth ? 'w-full' : '';
  
  const variantStyles = {
    primary: 'bg-gradient-to-r from-primary to-primary-container text-on-primary-container shadow-[0_8px_20px_-6px_rgba(0,227,253,0.3)] hover:scale-[1.02] active:scale-[0.98]',
    secondary: 'flex items-center justify-center gap-3 bg-surface-container-highest hover:bg-surface-bright text-on-surface border border-outline-variant/10 group',
  };

  return (
    <button
      type={type}
      onClick={onClick}
      className={`${baseStyles} ${widthStyles} ${variantStyles[variant]}`}
    >
      {icon && icon}
      {children}
    </button>
  );
}
