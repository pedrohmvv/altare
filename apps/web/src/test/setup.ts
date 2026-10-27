import '@testing-library/jest-dom/vitest'

// O jsdom não implementa ResizeObserver, que o Radix usa para medir controles e popovers.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
globalThis.ResizeObserver ??= ResizeObserverStub
