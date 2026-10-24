/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#050505",
        surface: "#0D0F14",
        card: "rgba(18, 20, 26, 0.75)",
        primary: "#3B82F6",
        accent: "#60A5FA",
        border: "rgba(255, 255, 255, 0.08)",
      },
      fontFamily: {
        headline: ["'Bebas Neue'", "sans-serif"],
        sans: ["Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};
