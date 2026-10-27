import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { App } from './App'

describe('App', () => {
  it('abre na Visão Geral', async () => {
    render(<App />)

    expect(
      await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' }),
    ).toBeInTheDocument()
  })
})
