import type { RootSearch } from '@/routes/router'

/** Mantém a lente ao navegar: o `search` dos links da casca repassa só `lente`. */
export const keepLens = (previous: RootSearch): RootSearch => ({ lente: previous.lente })
