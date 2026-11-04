import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Chip } from './chip'

describe('Chip', () => {
  it('é um botão que diz em texto se está ativado (aria-pressed)', () => {
    render(
      <>
        <Chip pressed onClick={() => {}}>
          Ligado
        </Chip>
        <Chip pressed={false} onClick={() => {}}>
          Desligado
        </Chip>
      </>,
    )

    expect(screen.getByRole('button', { name: 'Ligado' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('button', { name: 'Desligado' })).toHaveAttribute(
      'aria-pressed',
      'false',
    )
  })

  it('avisa o clique, que quem o usa decide se liga ou desliga', async () => {
    const onClick = vi.fn()
    render(
      <Chip pressed={false} onClick={onClick}>
        Filtro
      </Chip>,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Filtro' }))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('funciona com o teclado: Enter e Espaço', async () => {
    const onClick = vi.fn()
    render(
      <Chip pressed={false} onClick={onClick}>
        Filtro
      </Chip>,
    )

    await userEvent.tab()
    await userEvent.keyboard('{Enter}')
    await userEvent.keyboard(' ')
    expect(onClick).toHaveBeenCalledTimes(2)
  })

  it('desabilitado, não avisa o clique', async () => {
    const onClick = vi.fn()
    render(
      <Chip pressed={false} disabled onClick={onClick}>
        Filtro
      </Chip>,
    )

    expect(screen.getByRole('button', { name: 'Filtro' })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: 'Filtro' }))
    expect(onClick).not.toHaveBeenCalled()
  })
})
