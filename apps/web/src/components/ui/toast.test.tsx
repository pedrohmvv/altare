import { act, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { Button } from './button'
import { type ToastOptions, ToastProvider, useToast } from './toast'

function Demo({ options }: { options: ToastOptions }) {
  const { toast } = useToast()
  return <Button onClick={() => toast(options)}>Mostrar</Button>
}

const setup = (options: ToastOptions) => {
  const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
  render(
    <ToastProvider>
      <Demo options={options} />
    </ToastProvider>,
  )
  return user
}

const region = () => screen.getByRole('region', { name: /Notificações/ })

describe('Toast', () => {
  beforeEach(() => {
    vi.useFakeTimers({ shouldAdvanceTime: true })
  })
  afterEach(() => {
    vi.useRealTimers()
  })

  it('mostra o título e a descrição na região de notificações', async () => {
    const user = setup({
      title: 'Decisão registrada',
      description: 'Espaço Exemplo A foi escolhido.',
      tone: 'success',
    })

    await user.click(screen.getByRole('button', { name: 'Mostrar' }))

    expect(within(region()).getByText('Decisão registrada')).toBeVisible()
    expect(within(region()).getByText('Espaço Exemplo A foi escolhido.')).toBeVisible()
  })

  it('anuncia a notificação de forma educada, sem interromper (aria-live polite)', async () => {
    const user = setup({ title: 'Decisão registrada', tone: 'success' })

    await user.click(screen.getByRole('button', { name: 'Mostrar' }))

    // O Radix anuncia o texto numa região de status oculta, fora da lista visível.
    const announcement = screen.getByRole('status')
    expect(announcement).toHaveAttribute('aria-live', 'polite')
    await waitFor(() => expect(announcement).toHaveTextContent('Decisão registrada'))
    expect(document.querySelector('[aria-live="assertive"]')).not.toBeInTheDocument()
  })

  it.each([
    ['success', 'Salvo'],
    ['attention', 'Falta um extra'],
    ['info', 'Atualizado'],
  ] as const)('no tom %s mostra um ícone decorativo junto do texto', async (tone, title) => {
    const user = setup({ title, tone })

    await user.click(screen.getByRole('button', { name: 'Mostrar' }))

    expect(within(region()).getByText(title)).toBeVisible()
    expect(region().querySelector('svg[aria-hidden="true"]')).toBeInTheDocument()
  })

  it('some depois de 4 segundos, e não antes', async () => {
    const user = setup({ title: 'Salvo', tone: 'success' })
    await user.click(screen.getByRole('button', { name: 'Mostrar' }))

    act(() => {
      vi.advanceTimersByTime(3800)
    })
    expect(within(region()).getByText('Salvo')).toBeVisible()

    act(() => {
      vi.advanceTimersByTime(400)
    })
    await waitFor(() => expect(within(region()).queryByText('Salvo')).not.toBeInTheDocument())
  })

  it('a ação Desfazer chama o callback e fecha a notificação', async () => {
    const onUndo = vi.fn()
    const user = setup({
      title: 'Contato arquivado',
      tone: 'info',
      action: { label: 'Desfazer', altText: 'Desfazer pelo histórico do contato', onClick: onUndo },
    })
    await user.click(screen.getByRole('button', { name: 'Mostrar' }))

    await user.click(within(region()).getByRole('button', { name: 'Desfazer' }))

    expect(onUndo).toHaveBeenCalledOnce()
    await waitFor(() =>
      expect(within(region()).queryByText('Contato arquivado')).not.toBeInTheDocument(),
    )
  })

  it('fecha pelo botão Fechar notificação', async () => {
    const user = setup({ title: 'Salvo', tone: 'success' })
    await user.click(screen.getByRole('button', { name: 'Mostrar' }))

    await user.click(within(region()).getByRole('button', { name: 'Fechar notificação' }))

    await waitFor(() => expect(within(region()).queryByText('Salvo')).not.toBeInTheDocument())
  })

  it('empilha várias notificações', async () => {
    const user = setup({ title: 'Salvo', tone: 'success' })

    await user.click(screen.getByRole('button', { name: 'Mostrar' }))
    await user.click(screen.getByRole('button', { name: 'Mostrar' }))

    expect(within(region()).getAllByText('Salvo')).toHaveLength(2)
  })

  it('o tom padrão é info', async () => {
    const user = setup({ title: 'Atualizado' })

    await user.click(screen.getByRole('button', { name: 'Mostrar' }))

    expect(within(region()).getByText('Atualizado')).toBeVisible()
  })

  it('useToast fora do ToastProvider explica o que falta', () => {
    const quiet = vi.spyOn(console, 'error').mockImplementation(() => {})

    expect(() => render(<Demo options={{ title: 'x' }} />)).toThrow(/ToastProvider/)

    quiet.mockRestore()
  })

  it('exige o altText da ação no tipo (verificado pelo tsc)', () => {
    const semAltText: ToastOptions = {
      title: 'Contato arquivado',
      // @ts-expect-error ação sem altText não compila: o Desfazer some em 4 s
      action: { label: 'Desfazer', onClick: () => {} },
    }

    expect(semAltText).toBeDefined()
  })
})
