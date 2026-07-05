// Responsive breakpoints (px). Mirror the CSS tokens in app/globals.css.
export const BREAKPOINTS = {
  mobile: 0,
  tablet: 768,
  laptop: 1024,
  desktop: 1280,
} as const

export const isMobile = (width: number) => width < BREAKPOINTS.tablet
export const isTablet = (width: number) => width >= BREAKPOINTS.tablet && width < BREAKPOINTS.laptop
export const isLaptop = (width: number) => width >= BREAKPOINTS.laptop && width < BREAKPOINTS.desktop
export const isDesktop = (width: number) => width >= BREAKPOINTS.desktop