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
        bgDark: '#131722',    // Primary dark background
        cardDark: '#1e222d',  // Component background
        borderDark: '#2a2e39',// Lines and dividers
        textMain: '#d1d4dc',  // Primary light text
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
