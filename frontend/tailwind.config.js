import tokens from "./src/design-tokens.json";

/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: tokens.color.primary,
        neutral: tokens.color.neutral,
        accent: tokens.color.accent,
        surface: tokens.color.surface,
      },
      fontFamily: {
        sans: tokens.typography.fontFamily.sans.split(", "),
        mono: tokens.typography.fontFamily.mono.split(", "),
      },
      borderRadius: tokens.borderRadius,
      boxShadow: tokens.shadow,
      spacing: tokens.spacing,
    },
  },
  plugins: [],
};
