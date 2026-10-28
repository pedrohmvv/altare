import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { Button } from './button'
import { Sheet, SheetClose, SheetContent, SheetTrigger } from './sheet'

const renderSheet = () =>
  render(
    <Sheet>
      <SheetTrigger asChild>
        <Button>Abrir categoria</Button>
      </SheetTrigger>
      <SheetContent title="Fotografia" description="Detalhes da frente.">
        <p>Conteúdo do painel</p>
        <SheetClose asChild>
          <Button variant="secondary">Voltar à lista</Button>
        </SheetClose>
      </SheetContent>
    </Sheet>,
  )

describe('Sheet', () => {
  it('começa fechado', () => {
    renderSheet()
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('abre com o título como nome, a descrição ligada e o conteúdo', async () => {
    renderSheet()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir categoria' }))

    const painel = screen.getByRole('dialog', { name: 'Fotografia' })
    expect(painel).toHaveAccessibleDescription('Detalhes da frente.')
    expect(painel).toHaveTextContent('Conteúdo do painel')
  })

  it('fica abaixo do diálogo, do popover e do aviso (camada da gaveta)', async () => {
    renderSheet()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir categoria' }))
    expect(screen.getByRole('dialog')).toHaveClass('z-30')
  })

  it('o Esc fecha e devolve o foco ao gatilho', async () => {
    renderSheet()
    const gatilho = screen.getByRole('button', { name: 'Abrir categoria' })
    await userEvent.click(gatilho)
    await userEvent.keyboard('{Escape}')

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(gatilho).toHaveFocus()
  })

  it('o botão Fechar e o SheetClose fecham', async () => {
    renderSheet()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir categoria' }))
    await userEvent.click(screen.getByRole('button', { name: 'Fechar' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())

    await userEvent.click(screen.getByRole('button', { name: 'Abrir categoria' }))
    await userEvent.click(screen.getByRole('button', { name: 'Voltar à lista' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })
})
