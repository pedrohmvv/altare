import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Save } from 'lucide-react'
import { describe, expect, it, vi } from 'vitest'
import { Button } from './button'

describe('Button', () => {
  it('é um botão com o nome do rótulo e dispara o clique', async () => {
    const onClick = vi.fn()
    render(<Button onClick={onClick}>Registrar decisão</Button>)

    await userEvent.click(screen.getByRole('button', { name: 'Registrar decisão' }))

    expect(onClick).toHaveBeenCalledOnce()
  })

  it('não dispara o clique quando desabilitado', async () => {
    const onClick = vi.fn()
    render(
      <Button disabled onClick={onClick}>
        Salvar
      </Button>,
    )

    await userEvent.click(screen.getByRole('button', { name: 'Salvar' }))

    expect(onClick).not.toHaveBeenCalled()
  })

  it('em carregamento fica ocupado, desabilitado e não dispara o clique', async () => {
    const onClick = vi.fn()
    render(
      <Button loading onClick={onClick}>
        Salvar
      </Button>,
    )
    const button = screen.getByRole('button', { name: 'Salvar' })

    await userEvent.click(button)

    expect(button).toHaveAttribute('aria-busy', 'true')
    expect(button).toBeDisabled()
    expect(onClick).not.toHaveBeenCalled()
  })

  it('não se declara ocupado quando não está carregando', () => {
    render(<Button>Salvar</Button>)

    expect(screen.getByRole('button', { name: 'Salvar' })).not.toHaveAttribute('aria-busy')
  })

  it('não envia o formulário por acidente: o tipo padrão é button', () => {
    render(<Button>Salvar</Button>)

    expect(screen.getByRole('button', { name: 'Salvar' })).toHaveAttribute('type', 'button')
  })

  it('aceita type="submit" quando o formulário pede', () => {
    render(<Button type="submit">Enviar</Button>)

    expect(screen.getByRole('button', { name: 'Enviar' })).toHaveAttribute('type', 'submit')
  })

  it('com asChild entrega o estilo a um link e mantém o papel de link', () => {
    render(
      <Button asChild>
        <a href="/contatos">Ver contatos</a>
      </Button>,
    )

    expect(screen.getByRole('link', { name: 'Ver contatos' })).toHaveAttribute('href', '/contatos')
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('exige aria-label no botão só de ícone (verificado pelo tsc)', () => {
    render(
      <Button size="icon" aria-label="Salvar">
        <Save aria-hidden />
      </Button>,
    )
    expect(screen.getByRole('button', { name: 'Salvar' })).toBeInTheDocument()

    // @ts-expect-error botão só de ícone sem aria-label não compila
    const semRotulo = <Button size="icon">x</Button>
    expect(semRotulo).toBeDefined()
  })
})
