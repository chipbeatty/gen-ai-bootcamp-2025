/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      maxWidth: {
        '6xl': '72rem', // Wide layout as per requirements
      },
      padding: {
        '5': '1.25rem', // Specified padding for vocabulary items
      },
      margin: {
        '4': '1rem', // Specified margin between items
      },
    },
  },
  plugins: [],
}
