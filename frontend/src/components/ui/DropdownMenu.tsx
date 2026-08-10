import * as React from 'react';
import * as RadixDropdownMenu from '@radix-ui/react-dropdown-menu';
import { cn } from '@/lib/cn';

const DropdownMenu = RadixDropdownMenu.Root;
const DropdownMenuTrigger = RadixDropdownMenu.Trigger;

interface DropdownMenuContentProps
  extends React.ComponentPropsWithoutRef<typeof RadixDropdownMenu.Content> {}

const DropdownMenuContent = React.forwardRef<
  React.ElementRef<typeof RadixDropdownMenu.Content>,
  DropdownMenuContentProps
>(({ className, ...props }, ref) => (
  <RadixDropdownMenu.Portal>
    <RadixDropdownMenu.Content
      ref={ref}
      className={cn(
        'z-50 min-w-[8rem] rounded-md border border-neutral-200 bg-surface shadow-md p-1',
        className
      )}
      {...props}
    />
  </RadixDropdownMenu.Portal>
));

DropdownMenuContent.displayName = 'DropdownMenuContent';

interface DropdownMenuItemProps
  extends React.ComponentPropsWithoutRef<typeof RadixDropdownMenu.Item> {}

const DropdownMenuItem = React.forwardRef<
  React.ElementRef<typeof RadixDropdownMenu.Item>,
  DropdownMenuItemProps
>(({ className, ...props }, ref) => (
  <RadixDropdownMenu.Item
    ref={ref}
    className={cn(
      'relative flex cursor-pointer select-none items-center rounded px-2 py-1.5 text-sm outline-none',
      'hover:bg-neutral-100 focus:bg-neutral-100',
      'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      className
    )}
    {...props}
  />
));

DropdownMenuItem.displayName = 'DropdownMenuItem';

interface DropdownMenuCheckboxItemProps
  extends React.ComponentPropsWithoutRef<typeof RadixDropdownMenu.CheckboxItem> {}

const DropdownMenuCheckboxItem = React.forwardRef<
  React.ElementRef<typeof RadixDropdownMenu.CheckboxItem>,
  DropdownMenuCheckboxItemProps
>(({ className, ...props }, ref) => (
  <RadixDropdownMenu.CheckboxItem
    ref={ref}
    className={cn(
      'relative flex cursor-pointer select-none items-center rounded py-1.5 pl-8 pr-2 text-sm outline-none',
      'hover:bg-neutral-100 focus:bg-neutral-100',
      'data-[disabled]:pointer-events-none data-[disabled]:opacity-50',
      className
    )}
    {...props}
  />
));

DropdownMenuCheckboxItem.displayName = 'DropdownMenuCheckboxItem';

interface DropdownMenuSeparatorProps
  extends React.ComponentPropsWithoutRef<typeof RadixDropdownMenu.Separator> {}

const DropdownMenuSeparator = React.forwardRef<
  React.ElementRef<typeof RadixDropdownMenu.Separator>,
  DropdownMenuSeparatorProps
>(({ className, ...props }, ref) => (
  <RadixDropdownMenu.Separator
    ref={ref}
    className={cn('my-1 h-px bg-neutral-200', className)}
    {...props}
  />
));

DropdownMenuSeparator.displayName = 'DropdownMenuSeparator';

export {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuSeparator,
};
