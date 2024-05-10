/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../griddy/templates/**/*.{html,js}"],
  darkMode: 'class',
  theme: {
  },
  daisyui: {
    themes: ["cupcake"],
  },
  plugins: [
      require("@tailwindcss/typography"),
      require('daisyui'),
  ],
}
