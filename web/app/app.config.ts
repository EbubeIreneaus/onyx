export default defineAppConfig({
  ui: {
    colors: {
      primary: 'neutral',
      neutral: 'neutral'
    },
    button: {
      defaultVariants: {
        color: 'neutral',
        size: 'md'
      }
    },
    input: {
      defaultVariants: {
        size: 'md'
      },
      slots: {
        root: 'w-full',
        base: 'h-11 py-2.5 text-sm rounded-md'
      }
    }
  }
})
