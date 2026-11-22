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
        // The palette is black / white / neutral gray, with red and green only
        // for error and success. Coworker screens use amber (warnings, "needs
        // you") and blue (queued, info) utilities; render those on the same
        // neutral scale so no accent hue reaches the UI.
        amber: colors.neutral,
        blue: colors.neutral,
      },
    },
  },
  plugins: [],
};
