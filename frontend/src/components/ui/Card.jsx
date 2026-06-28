import React from 'react';
import clsx from 'clsx';

export const Card = ({ children, className, variant = 'default', ...props }) => {
  return (
    <div
      className={clsx(
        'card',
        variant === 'glass' && 'card-glass',
        variant === 'elevated' && 'card-elevated',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
