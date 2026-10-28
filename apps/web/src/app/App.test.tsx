import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, mockApi } from '@/test/fake-api'
import { FAKE_NOIVO } from '@/test/render-route'
import { App } from './App'

describe('App', () => {
  it('abre na Visão Geral', async () => {
    mockApi({ 'GET /api/v1/auth/me': jsonResponse(200, FAKE_NOIVO) })
    render(<App />)

    expect(
      await screen.findByRole('heading', { level: 1, name: 'O momento de vocês' }),
    ).toBeInTheDocument()
  })
})
