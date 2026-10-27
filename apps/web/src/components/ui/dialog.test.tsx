import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Button } from './button'
import { Dialog, DialogClose, DialogContent, DialogFooter, DialogTrigger } from './dialog'

const renderDialog = (content: Partial<Parameters<typeof DialogContent>[0]> = {}) =>
  render(
    <Dialog>
      <DialogTrigger asChild>
        <Button>Abrir</Button>
      </DialogTrigger>
      <DialogContent
        title="Registrar decisão"
        description="Confirme o espaço escolhido."
        {...content}
      >
        <p>Espaço Exemplo A</p>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="secondary">Cancelar</Button>
          </DialogClose>
        </DialogFooter>
      </DialogContent>
    </Dialog>,
  )

describe('Dialog', () => {
  it('começa fechado', () => {
    renderDialog()

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('abre pelo gatilho com o título como nome e a descrição ligada', async () => {
    renderDialog()

    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    const dialog = screen.getByRole('dialog', { name: 'Registrar decisão' })
    expect(dialog).toHaveAccessibleDescription('Confirme o espaço escolhido.')
    expect(screen.getByText('Espaço Exemplo A')).toBeVisible()
  })

  it('sem descrição não liga aria-describedby', async () => {
    renderDialog({ description: undefined })

    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    expect(screen.getByRole('dialog')).not.toHaveAttribute('aria-describedby')
  })

  it('fecha com a tecla Esc', async () => {
    renderDialog()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    await userEvent.keyboard('{Escape}')

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('fecha pelo botão Fechar, sempre presente', async () => {
    renderDialog()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    await userEvent.click(screen.getByRole('button', { name: 'Fechar' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('fecha por um DialogClose do conteúdo', async () => {
    renderDialog()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    await userEvent.click(screen.getByRole('button', { name: 'Cancelar' }))

    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
  })

  it('leva o foco para dentro e o mantém preso ao navegar com Tab', async () => {
    renderDialog()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))
    const dialog = screen.getByRole('dialog')

    expect(dialog).toContainElement(document.activeElement as HTMLElement)
    for (let i = 0; i < 5; i++) {
      await userEvent.tab()
      expect(dialog).toContainElement(document.activeElement as HTMLElement)
    }
  })

  it('devolve o foco ao gatilho ao fechar', async () => {
    renderDialog()
    const trigger = screen.getByRole('button', { name: 'Abrir' })
    await userEvent.click(trigger)

    await userEvent.keyboard('{Escape}')

    await waitFor(() => expect(trigger).toHaveFocus())
  })

  it('deixa o conteúdo de trás fora da árvore de acessibilidade enquanto aberto', async () => {
    renderDialog()
    await userEvent.click(screen.getByRole('button', { name: 'Abrir' }))

    expect(screen.queryByRole('button', { name: 'Abrir' })).not.toBeInTheDocument()
  })

  it('funciona controlado e avisa a mudança de estado', async () => {
    const onOpenChange = vi.fn()
    render(
      <Dialog open onOpenChange={onOpenChange}>
        <DialogContent title="Controlado">x</DialogContent>
      </Dialog>,
    )

    await userEvent.keyboard('{Escape}')

    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('exige o título no tipo (verificado pelo tsc)', () => {
    // @ts-expect-error diálogo sem título não compila: o leitor de tela precisa do nome
    const semTitulo = <DialogContent>x</DialogContent>

    expect(semTitulo).toBeDefined()
  })
})
