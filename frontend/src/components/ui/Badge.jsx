import React from 'react';
import clsx from 'clsx';

const COLOR_MAP = {
  blue: 'badge-blue',
  green: 'badge-green',
  red: 'badge-red',
  orange: 'badge-orange',
  purple: 'badge-purple',
};

export const Badge = ({ children, color = 'blue', className, ...props }) => {
  return (
    <span className={clsx('badge', COLOR_MAP[color], className)} {...props}>
      {children}
    </span>
  );
};
