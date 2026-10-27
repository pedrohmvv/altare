import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from './table'

const renderTable = (props: Partial<Parameters<typeof Table>[0]> = {}) =>
  render(
    <Table label="Comparativo de espaços" {...props}>
      <TableCaption>Cenários de orçamento (exemplo)</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Espaço</TableHead>
          <TableHead numeric>Custo real</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableHead scope="row">Espaço Exemplo A</TableHead>
          <TableCell numeric>R$ 12.480,00</TableCell>
        </TableRow>
        <TableRow>
          <TableHead scope="row">Espaço Exemplo B</TableHead>
          <TableCell numeric>R$ 9.950,00</TableCell>
        </TableRow>
      </TableBody>
    </Table>,
  )

describe('Table', () => {
  it('é uma tabela com o nome vindo da legenda', () => {
    renderTable()

    expect(
      screen.getByRole('table', { name: 'Cenários de orçamento (exemplo)' }),
    ).toBeInTheDocument()
  })

  it('declara o escopo das células de cabeçalho', () => {
    renderTable()

    const columns = screen.getAllByRole('columnheader')
    expect(columns).toHaveLength(2)
    for (const column of columns) expect(column).toHaveAttribute('scope', 'col')
    expect(screen.getByRole('rowheader', { name: 'Espaço Exemplo A' })).toHaveAttribute(
      'scope',
      'row',
    )
  })

  it('lista as linhas e as células com o conteúdo', () => {
    renderTable()

    const rows = screen.getAllByRole('row')
    expect(rows).toHaveLength(3)
    expect(within(rows[2] as HTMLElement).getByRole('cell')).toHaveTextContent('R$ 9.950,00')
  })

  it('alinha à direita as células e os cabeçalhos numéricos', () => {
    renderTable()

    expect(screen.getByRole('columnheader', { name: 'Custo real' })).toHaveClass('text-right')
    expect(screen.getByRole('cell', { name: 'R$ 12.480,00' })).toHaveClass('text-right')
    expect(screen.getByRole('columnheader', { name: 'Espaço' })).not.toHaveClass('text-right')
  })

  it('rola dentro de uma região nomeada, alcançável pelo teclado', async () => {
    renderTable()

    await userEvent.tab()

    expect(screen.getByRole('region', { name: 'Comparativo de espaços' })).toHaveFocus()
  })

  it('aceita a legenda só para leitor de tela', () => {
    render(
      <Table label="Parcelas">
        <TableCaption srOnly>Parcelas do contrato (exemplo)</TableCaption>
        <TableBody>
          <TableRow>
            <TableCell>1/3</TableCell>
          </TableRow>
        </TableBody>
      </Table>,
    )

    expect(
      screen.getByRole('table', { name: 'Parcelas do contrato (exemplo)' }),
    ).toBeInTheDocument()
  })
})
