/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx}',
    './src/components/**/*.{js,ts,jsx,tsx}',
    './src/app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      maxWidth: {
        '6xl': '72rem', // Wide layout to prevent text wrapping
      },
      spacing: {
        '5': '1.25rem', // Exact padding for vocabulary items
        '4': '1rem',   // Exact margin between items
      },
      height: {
        'screen': '100vh',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
