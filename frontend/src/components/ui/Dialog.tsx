import * as React from 'react';
import * as RadixDialog from '@radix-ui/react-dialog';
import { X } from 'lucide-react';
import { cn } from '@/lib/cn';

interface DialogProps {
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  children: React.ReactNode;
}

const Dialog = ({ open, onOpenChange, children }: DialogProps) => (
  <RadixDialog.Root open={open} onOpenChange={onOpenChange}>
    {children}
  </RadixDialog.Root>
);

interface DialogTriggerProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

const DialogTrigger = React.forwardRef<HTMLButtonElement, DialogTriggerProps>(
  ({ ...props }, ref) => <RadixDialog.Trigger ref={ref} {...props} />
);

DialogTrigger.displayName = 'DialogTrigger';

const DialogContent = React.forwardRef<
  React.ElementRef<typeof RadixDialog.Content>,
  React.ComponentPropsWithoutRef<typeof RadixDialog.Content>
>(({ className, ...props }, ref) => (
  <RadixDialog.Portal>
    <RadixDialog.Overlay className="fixed inset-0 bg-black bg-opacity-50 z-50" />
    <RadixDialog.Content
      ref={ref}
      className={cn(
        'fixed left-1/2 top-1/2 z-50 w-full max-w-lg translate-x--1/2 translate-y--1/2',
        'rounded-lg border border-neutral-200 bg-surface shadow-lg p-6',
        'focus-visible:outline-none',
        className
      )}
      {...props}
    />
  </RadixDialog.Portal>
));

DialogContent.displayName = 'DialogContent';

interface DialogHeaderProps extends React.HTMLAttributes<HTMLDivElement> {}

const DialogHeader = React.forwardRef<HTMLDivElement, DialogHeaderProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex items-center justify-between mb-4', className)} {...props} />
  )
);

DialogHeader.displayName = 'DialogHeader';

interface DialogTitleProps extends React.ComponentPropsWithoutRef<typeof RadixDialog.Title> {}

const DialogTitle = React.forwardRef<
  React.ElementRef<typeof RadixDialog.Title>,
  DialogTitleProps
>(({ className, ...props }, ref) => (
  <RadixDialog.Title
    ref={ref}
    className={cn('text-lg font-semibold text-neutral-900', className)}
    {...props}
  />
));

DialogTitle.displayName = 'DialogTitle';

interface DialogCloseProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {}

const DialogClose = React.forwardRef<HTMLButtonElement, DialogCloseProps>(
  ({ className, ...props }, ref) => (
    <RadixDialog.Close
      ref={ref}
      className={cn(
        'rounded p-1 hover:bg-neutral-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-brand-500',
        className
      )}
      {...props}
    >
      <X className="h-5 w-5" />
    </RadixDialog.Close>
  )
);

DialogClose.displayName = 'DialogClose';

interface DialogBodyProps extends React.HTMLAttributes<HTMLDivElement> {}

const DialogBody = React.forwardRef<HTMLDivElement, DialogBodyProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('mb-6', className)} {...props} />
  )
);

DialogBody.displayName = 'DialogBody';

interface DialogFooterProps extends React.HTMLAttributes<HTMLDivElement> {}

const DialogFooter = React.forwardRef<HTMLDivElement, DialogFooterProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn('flex justify-end gap-3', className)} {...props} />
  )
);

DialogFooter.displayName = 'DialogFooter';

export {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
  DialogBody,
  DialogFooter,
};
