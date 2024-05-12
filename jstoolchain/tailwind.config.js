/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
      "../griddy/templates/**/*.html",
      "../griddy/static/js/**/*.js",
      "./node_modules/preline/dist/*.js",
  ],
  darkMode: 'class',
  theme: {
  },
  plugins: [
      require("@tailwindcss/typography"),
      require("@tailwindcss/forms"),
      require("preline/plugin"),
  ],
}
