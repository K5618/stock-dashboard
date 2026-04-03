/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        up: '#089981',      // TradingView Green
        down: '#F23645',    // TradingView Red
        primary: '#2962FF', // TradingView Blue
        bgLight: '#F8F9FA',      
        cardLight: '#FFFFFF',
        textDark: '#131722',
        textMuted: '#787B86'
      }
    },
  },
  plugins: [],
}
