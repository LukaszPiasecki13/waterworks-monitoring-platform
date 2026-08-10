import * as React from 'react';
import * as RadixPopover from '@radix-ui/react-popover';
import { cn } from '@/lib/cn';

const Popover = RadixPopover.Root;
const PopoverTrigger = RadixPopover.Trigger;

interface PopoverContentProps
  extends React.ComponentPropsWithoutRef<typeof RadixPopover.Content> {}

const PopoverContent = React.forwardRef<
  React.ElementRef<typeof RadixPopover.Content>,
  PopoverContentProps
>(({ className, align = 'center', sideOffset = 4, ...props }, ref) => (
  <RadixPopover.Portal>
    <RadixPopover.Content
      ref={ref}
      align={align}
      sideOffset={sideOffset}
      className={cn(
        'z-50 w-72 rounded-md border border-neutral-200 bg-surface shadow-md p-4',
        className
      )}
      {...props}
    />
  </RadixPopover.Portal>
));

PopoverContent.displayName = 'PopoverContent';

export { Popover, PopoverTrigger, PopoverContent };
