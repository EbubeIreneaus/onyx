// @ts-check
import withNuxt from './.nuxt/eslint.config.mjs'

export default withNuxt(
  {
    rules: {
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unused-vars': ['error', {
        argsIgnorePattern: '^_|err|e',
        varsIgnorePattern: '^_|err|e',
        caughtErrorsIgnorePattern: '.*'
      }],
      '@stylistic/max-statements-per-line': 'off'
    }
  }
)
