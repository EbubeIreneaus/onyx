// Universal plugin (SSR + Client) to restore auth session before app renders
export default defineNuxtPlugin(async () => {
  const { restore, initialized } = useAuth()
  if (!initialized.value) {
    await restore()
  }
})
