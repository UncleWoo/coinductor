module.exports = {
  content: [
    './coinductor/templates/**/*.html',
    './*/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        'brand-white': '#FFFFFF',
        'brand-accent': '#EAA430',
        'brand-charcoal': '#2B2B2B',
      },
      borderRadius: {
        'brand': '0.5rem',
      },
      boxShadow: {
        'brand-card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)',
        'brand-focus': '0 0 0 3px rgba(234, 164, 48, 0.3)',
      },
      fontFamily: {
        'sans': ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
