/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#FAFAFA',      
          surface: '#FFFFFF',  
          primary: '#8A9A86',  
          text: '#1A1A1A',     
          muted: '#9CA3AF',    
        }
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Courier Prime', 'monospace'], 
      }
    },
  },
  plugins: [],
}