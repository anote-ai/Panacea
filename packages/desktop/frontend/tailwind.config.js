import colors from "tailwindcss/colors";

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      // Same as packages/web: neutral grays instead of Tailwind's blue-tinted default.
      colors: { gray: colors.neutral },
    },
  },
  plugins: [],
};
