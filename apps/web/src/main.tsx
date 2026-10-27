import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@fontsource-variable/jetbrains-mono/wght.css'
import '@fontsource-variable/newsreader/wght.css'
import '@fontsource-variable/newsreader/wght-italic.css'
import '@fontsource-variable/plus-jakarta-sans/wght.css'
import { App } from '@/app/App'
import '@/styles/index.css'

const root = document.getElementById('root')
if (!root) {
  throw new Error('Elemento #root não encontrado no index.html')
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
