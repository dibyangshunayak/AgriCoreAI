import React from 'react';

export const Logo = ({ className = "w-6 h-6", fillClass = "" }) => {
  return (
    <svg 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg" 
      className={`${className} shrink-0`}
    >
      <defs>
        {/* Simple solid green colors instead of complex filters/glows */}
        <linearGradient id="sprout-grad" x1="0%" y1="100%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#059669" />
          <stop offset="100%" stopColor="#10b981" />
        </linearGradient>
      </defs>

      <g fill="url(#sprout-grad)">
        {/* Left Leaf */}
        <path 
          d="M 44,52 C 28,52 12,42 5,26 C -2,10 10,2 25,6 C 40,10 44,30 44,52 Z" 
        />

        {/* Right Leaf */}
        <path 
          d="M 52,24 C 54,12 65,3 78,0 C 92,-3 100,5 96,20 C 92,35 78,45 64,36 C 60,32 55,28 52,24 Z" 
        />

        {/* Stem */}
        <path 
          d="M 44,90 A 6,6 0 0,0 56,90 L 56,48 A 21,21 0 0,1 77,27 L 85,27 A 6,6 0 0,0 85,15 L 77,15 A 33,33 0 0,0 44,48 Z" 
        />
      </g>
    </svg>
  );
};

export default Logo;
