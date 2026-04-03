/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        up: "#10B981",
        down: "#EF4444",
        bgDark: "#0F172A",
        cardDark: "#1E293B",
      }
    },
  },
  plugins: [],
}
