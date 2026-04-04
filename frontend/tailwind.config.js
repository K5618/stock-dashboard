/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        up: '#089981',        // TV Green
        down: '#f23645',      // TV Red
        primary: '#2962ff',   // TV Blue
        bgLight: '#F8F9FA',   // White/Grey Background
        cardLight: '#FFFFFF', // Pure White Component Backs
        borderLight: '#E0E3EB', // Light dividers
        textMain: '#131722',  // Primary Dark Text (TV)
        textMuted: '#787b86', // Secondary muted text
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Trebuchet MS',
          'Roboto',
          'Ubuntu',
          'sans-serif'
        ]
      }
    },
  },
  plugins: [],
}
