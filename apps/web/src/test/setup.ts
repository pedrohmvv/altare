import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// Com `globals: false` o Testing Library não registra a limpeza do DOM sozinho.
afterEach(cleanup)

// O jsdom não implementa ResizeObserver, que o Radix usa para medir controles e popovers.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver ??= ResizeObserverStub
