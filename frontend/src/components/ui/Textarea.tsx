import * as React from 'react';
import { cn } from '@/lib/cn';

type TextareaProps = React.TextareaHTMLAttributes<HTMLTextAreaElement>;

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, ...props }, ref) => (
    <textarea
      className={cn(
        'flex min-h-[100px] w-full rounded-md border border-neutral-300 bg-surface px-3 py-2 text-base',
        'placeholder:text-neutral-500',
        'focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500',
        'disabled:cursor-not-allowed disabled:opacity-50',
        'resize-none',
        className
      )}
      ref={ref}
      {...props}
    />
  )
);

Textarea.displayName = 'Textarea';

export { Textarea };
