import colors from "tailwindcss/colors";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Tailwind's default `gray` is blue-tinted (gray-700 = #374151), which
        // reads as off-color against the neutral #212121 / #2F2F2F surfaces.
        // Map every gray-* utility onto the true-neutral scale instead.
        gray: colors.neutral,
      },
    },
  },
  plugins: [],
};
