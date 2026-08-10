import * as React from 'react';
import { cn } from '@/lib/cn';

interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'neutral' | 'info' | 'success' | 'warning' | 'danger';
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = 'neutral', ...props }, ref) => {
    const variantStyles = {
      neutral: 'bg-neutral-100 text-neutral-900',
      info: 'bg-blue-100 text-blue-900',
      success: 'bg-green-100 text-green-900',
      warning: 'bg-yellow-100 text-yellow-900',
      danger: 'bg-red-100 text-red-900',
    };

    return (
      <div
        ref={ref}
        className={cn(
          'inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium',
          variantStyles[variant],
          className
        )}
        {...props}
      />
    );
  }
);

Badge.displayName = 'Badge';

export { Badge };
