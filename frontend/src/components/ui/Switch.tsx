import * as React from 'react';
import { cn } from '@/lib/cn';

interface SwitchProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  checked?: boolean;
  onCheckedChange?: (checked: boolean) => void;
  disabled?: boolean;
}

const Switch = React.forwardRef<HTMLButtonElement, SwitchProps>(
  ({ checked = false, onCheckedChange, disabled = false, className, ...props }, ref) => {
    const handleClick = () => {
      if (!disabled && onCheckedChange) {
        onCheckedChange(!checked);
      }
    };

    return (
      <button
        ref={ref}
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={handleClick}
        className={cn(
          'relative inline-flex h-5 w-9 flex-shrink-0 rounded-full border-2 border-transparent',
          'transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500',
          {
            'bg-brand-500': checked && !disabled,
            'bg-neutral-300': !checked && !disabled,
            'bg-neutral-200 opacity-50 cursor-not-allowed': disabled,
          },
          className
        )}
        {...props}
      >
        <span
          className={cn(
            'pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow-md transition-transform',
            {
              'translate-x-4': checked,
              'translate-x-0': !checked,
            }
          )}
        />
      </button>
    );
  }
);

Switch.displayName = 'Switch';

export { Switch };
