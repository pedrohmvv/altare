import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'
import { describe, expect, it, vi } from 'vitest'
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogTrigger,
} from './alert-dialog'
import { Button } from './button'
import { Dialog, DialogContent, DialogTrigger } from './dialog'

function Example({
  onConfirm = () => {},
  onCloseAutoFocus,
  onEscapeKeyDown,
  pending,
}: {
  onConfirm?: () => void
  onCloseAutoFocus?: (event: Event) => void
  onEscapeKeyDown?: (event: KeyboardEvent) => void
  pending?: boolean
}) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        <Button variant="soft-destructive">Excluir exemplo</Button>
      </AlertDialogTrigger>
      <AlertDialogContent
        title="Excluir o Espaço Exemplo A?"
        description="Ele sai da lista, mas o registro fica guardado."
        onCloseAutoFocus={onCloseAutoFocus}
        onEscapeKeyDown={onEscapeKeyDown}
        pending={pending}
      >
        <AlertDialogFooter>
          <AlertDialogCancel asChild>
            <Button variant="ghost">Cancelar</Button>
          </AlertDialogCancel>
          <Button variant="soft-destructive" onClick={onConfirm}>
            Excluir
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}

const open = () => userEvent.click(screen.getByRole('button', { name: 'Excluir exemplo' }))

function InsidePanel() {
  const [sheetOpen, setSheetOpen] = useState(true)
  return (
    <Dialog open={sheetOpen} onOpenChange={setSheetOpen}>
      <DialogTrigger asChild>
        <Button>Abrir painel</Button>
      </DialogTrigger>
      <DialogContent title="Painel Exemplo" description="Um painel.">
        <Example />
      </DialogContent>
    </Dialog>
  )
}

describe('AlertDialog', () => {
  it('começa fechado', () => {
    render(<Example />)

    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
  })

  it('abre como alertdialog, com o título por nome e a descrição ligada', async () => {
    render(<Example />)

    await open()

    const dialog = screen.getByRole('alertdialog', { name: 'Excluir o Espaço Exemplo A?' })
    expect(dialog).toHaveAccessibleDescription('Ele sai da lista, mas o registro fica guardado.')
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('não tem o botão Fechar: sai-se só por Cancelar, pela confirmação ou pelo Esc', async () => {
    render(<Example />)

    await open()

    expect(screen.queryByRole('button', { name: 'Fechar' })).not.toBeInTheDocument()
  })

  it('leva o foco inicial ao Cancelar, o lado seguro', async () => {
    render(<Example />)

    await open()

    expect(screen.getByRole('button', { name: 'Cancelar' })).toHaveFocus()
  })

  it('fecha com o Esc e devolve o foco ao gatilho', async () => {
    render(<Example />)
    await open()

    await userEvent.keyboard('{Escape}')

    await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Excluir exemplo' })).toHaveFocus(),
    )
  })

  it('com a escrita pendente, o Esc não fecha; sem ela, fecha', async () => {
    const { rerender } = render(<Example pending />)
    await open()

    await userEvent.keyboard('{Escape}')

    expect(screen.getByRole('alertdialog')).toBeInTheDocument()
    rerender(<Example pending={false} />)
    await userEvent.keyboard('{Escape}')
    await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
  })

  it('com a escrita pendente, ainda chama o onEscapeKeyDown de quem usa', async () => {
    const onEscapeKeyDown = vi.fn()
    render(<Example pending onEscapeKeyDown={onEscapeKeyDown} />)
    await open()

    await userEvent.keyboard('{Escape}')

    expect(onEscapeKeyDown).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('alertdialog')).toBeInTheDocument()
  })

  it('fecha pelo Cancelar e devolve o foco ao gatilho', async () => {
    render(<Example />)
    await open()

    await userEvent.click(screen.getByRole('button', { name: 'Cancelar' }))

    await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Excluir exemplo' })).toHaveFocus(),
    )
  })

  it('um clique fora não fecha: a confirmação pede uma resposta', async () => {
    render(<Example />)
    await open()

    // O Radix bloqueia o ponteiro fora do diálogo; o teste dispara o clique mesmo assim.
    await userEvent.setup({ pointerEventsCheck: 0 }).click(document.body)

    expect(screen.getByRole('alertdialog')).toBeInTheDocument()
  })

  it('o botão de confirmar é comum: age sem fechar, para a tela mostrar a escrita e o erro', async () => {
    const onConfirm = vi.fn()
    render(<Example onConfirm={onConfirm} />)
    await open()

    await userEvent.click(screen.getByRole('button', { name: 'Excluir' }))

    expect(onConfirm).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('alertdialog')).toBeInTheDocument()
  })

  it('repassa onCloseAutoFocus: quem usa decide para onde o foco vai ao fechar', async () => {
    const elsewhere = document.createElement('button')
    document.body.append(elsewhere)
    render(
      <Example
        onCloseAutoFocus={(event) => {
          event.preventDefault()
          elsewhere.focus()
        }}
      />,
    )
    await open()

    await userEvent.keyboard('{Escape}')

    await waitFor(() => expect(elsewhere).toHaveFocus())
    elsewhere.remove()
  })

  it('dentro de outro painel, o Esc fecha só a confirmação', async () => {
    render(<InsidePanel />)
    await open()
    expect(screen.getByRole('alertdialog')).toBeInTheDocument()

    await userEvent.keyboard('{Escape}')

    await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
    expect(screen.getByRole('dialog', { name: 'Painel Exemplo' })).toBeInTheDocument()
  })

  it('exige título e descrição no tipo (verificado pelo tsc)', () => {
    // @ts-expect-error confirmação sem título não compila: o leitor de tela precisa do nome
    const semTitulo = <AlertDialogContent description="x">x</AlertDialogContent>
    // @ts-expect-error confirmação sem descrição não compila: ela explica a consequência
    const semDescricao = <AlertDialogContent title="x">x</AlertDialogContent>

    expect(semTitulo).toBeDefined()
    expect(semDescricao).toBeDefined()
  })
})
