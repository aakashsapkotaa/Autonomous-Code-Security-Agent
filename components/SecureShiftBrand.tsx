export default function SecureShiftBrand({ className = '' }: { className?: string }) {
  return (
    <span className={className}>
      <span className="text-primary font-bold">Secure</span>
      <span className="text-on-background font-bold">Shift</span>
    </span>
  );
}
