/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        midnight: "#0E1020",
        canvas: "#F6F3F0",
        ink: "#3D3F50",
        peach: "#FFC982",
        gold: "#FFAE41",
        melon: "#FF7E51",
        risk: "#D14600",
        sky: "#A1E6FF",
        trueblue: "#4995FF",
        royal: "#004AAC",
      },
      fontFamily: {
        display: ["'Playfair Display'", "Georgia", "serif"],
        body: ["'DM Sans'", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
}
