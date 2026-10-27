import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { Tabs, TabsContent, TabsList, TabsTrigger } from './tabs'

const renderTabs = (props: Record<string, unknown> = { defaultValue: 'ativo' }) =>
  render(
    <Tabs {...props}>
      <TabsList aria-label="Orçamento">
        <TabsTrigger value="ativo">Orçamento ativo</TabsTrigger>
        <TabsTrigger value="simulador">Simulador</TabsTrigger>
        <TabsTrigger value="pagamentos">Pagamentos</TabsTrigger>
      </TabsList>
      <TabsContent value="ativo">Painel do orçamento ativo</TabsContent>
      <TabsContent value="simulador">Painel do simulador</TabsContent>
      <TabsContent value="pagamentos">Painel de pagamentos</TabsContent>
    </Tabs>,
  )

describe('Tabs', () => {
  it('tem uma lista de abas nomeada e marca a aba inicial como selecionada', () => {
    renderTabs()

    expect(screen.getByRole('tablist', { name: 'Orçamento' })).toBeInTheDocument()
    expect(screen.getAllByRole('tab')).toHaveLength(3)
    expect(screen.getByRole('tab', { name: 'Orçamento ativo' })).toHaveAttribute(
      'aria-selected',
      'true',
    )
  })

  it('mostra só o painel da aba ativa, nomeado pela própria aba', () => {
    renderTabs()

    expect(screen.getByRole('tabpanel', { name: 'Orçamento ativo' })).toHaveTextContent(
      'Painel do orçamento ativo',
    )
    expect(screen.queryByText('Painel do simulador')).not.toBeInTheDocument()
  })

  it('troca de aba ao clicar', async () => {
    renderTabs()

    await userEvent.click(screen.getByRole('tab', { name: 'Simulador' }))

    expect(screen.getByRole('tab', { name: 'Simulador' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.getByText('Painel do simulador')).toBeVisible()
    expect(screen.queryByText('Painel do orçamento ativo')).not.toBeInTheDocument()
  })

  it('troca e ativa a aba com as setas do teclado', async () => {
    renderTabs()

    await userEvent.tab()
    await userEvent.keyboard('{ArrowRight}')

    expect(screen.getByRole('tab', { name: 'Simulador' })).toHaveFocus()
    expect(screen.getByRole('tab', { name: 'Simulador' })).toHaveAttribute('aria-selected', 'true')
  })

  it('vai à última e à primeira aba com End e Home', async () => {
    renderTabs()

    await userEvent.tab()
    await userEvent.keyboard('{End}')
    expect(screen.getByRole('tab', { name: 'Pagamentos' })).toHaveFocus()

    await userEvent.keyboard('{Home}')
    expect(screen.getByRole('tab', { name: 'Orçamento ativo' })).toHaveFocus()
  })

  it('funciona controlado e avisa a troca', async () => {
    const onValueChange = vi.fn()
    renderTabs({ value: 'ativo', onValueChange })

    await userEvent.click(screen.getByRole('tab', { name: 'Pagamentos' }))

    expect(onValueChange).toHaveBeenCalledWith('pagamentos')
    expect(screen.getByRole('tab', { name: 'Orçamento ativo' })).toHaveAttribute(
      'aria-selected',
      'true',
    )
  })
})
