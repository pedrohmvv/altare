import { screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { problemResponse } from '@/test/fake-api'
import { GET_GUESTS, renderGuests } from '@/test/render-guests'

const POST_EXPORT = 'POST /api/v1/guests/exports'
const XLSX = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

const file = (type: string, name: string) =>
  new Response('conteudo-do-arquivo', {
    status: 200,
    headers: {
      'content-type': type,
      'content-disposition': `attachment; filename="${name}"`,
    },
  })

describe('exportar a lista (F-CNV-08)', () => {
  const created: Blob[] = []
  const clicked: { download: string; href: string }[] = []
  let revoked: string[] = []

  beforeEach(() => {
    created.length = 0
    clicked.length = 0
    revoked = []
    // O jsdom não traz as duas funções; acrescentá-las ao `URL` sem trocar o construtor.
    URL.createObjectURL = (blob: Blob) => {
      created.push(blob)
      return `blob:altare-${created.length}`
    }
    URL.revokeObjectURL = (href: string) => {
      revoked.push(href)
    }
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (
      this: HTMLAnchorElement,
    ) {
      clicked.push({ download: this.download, href: this.href })
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    // @ts-expect-error: o jsdom não define estas funções; o teste as tira ao terminar.
    delete URL.createObjectURL
    // @ts-expect-error: idem.
    delete URL.revokeObjectURL
  })

  async function openDialog(user: ReturnType<typeof renderGuests>['user']) {
    await user.click(await screen.findByRole('button', { name: 'Exportar lista' }))
    return screen.findByRole('dialog', { name: 'Exportar a lista' })
  }

  it('avisa o tamanho da lista e o cuidado com o arquivo antes de baixar', async () => {
    const { user } = renderGuests()
    const dialog = await openDialog(user)

    expect(within(dialog).getByText(/pessoas? na lista/)).toBeVisible()
    expect(
      within(dialog).getByText(
        'O arquivo tem telefone, e-mail e endereço de convidados. Guardem com cuidado.',
      ),
    ).toBeVisible()
  })

  it('baixa o Excel por padrão, com os ids das pessoas que estão na tela', async () => {
    const { user, api } = renderGuests({
      [POST_EXPORT]: file(XLSX, 'lista-de-convidados-2026-10-28.xlsx'),
    })
    const dialog = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Baixar arquivo' }))

    await waitFor(() => expect(clicked).toHaveLength(1))
    const [call] = api.callsTo(POST_EXPORT)
    expect(call?.body).toEqual({ format: 'xlsx', guest_ids: ['p-a', 'p-b', 'p-c', 'p-d'] })
    expect(clicked[0]?.download).toBe('lista-de-convidados-2026-10-28.xlsx')
    expect(created).toHaveLength(1)
    await waitFor(() => expect(revoked).toEqual(['blob:altare-1']))
  })

  it('baixa o CSV quando vocês escolhem o CSV', async () => {
    const { user, api } = renderGuests({
      [POST_EXPORT]: file('text/csv; charset=utf-8', 'lista-de-convidados-2026-10-28.csv'),
    })
    const dialog = await openDialog(user)

    await user.click(within(dialog).getByRole('radio', { name: 'CSV' }))
    await user.click(within(dialog).getByRole('button', { name: 'Baixar arquivo' }))

    await waitFor(() => expect(clicked).toHaveLength(1))
    expect(api.callsTo(POST_EXPORT)[0]?.body).toMatchObject({ format: 'csv' })
    expect(clicked[0]?.download).toBe('lista-de-convidados-2026-10-28.csv')
  })

  it('leva só as pessoas do filtro, e o aviso diz quantas são', async () => {
    const { user, api } = renderGuests(
      { [POST_EXPORT]: file(XLSX, 'lista-de-convidados-2026-10-28.xlsx') },
      { lado: 'noiva' },
    )
    const dialog = await openDialog(user)
    expect(within(dialog).getByTestId('export-count')).toHaveTextContent('1 pessoa na lista')

    await user.click(within(dialog).getByRole('button', { name: 'Baixar arquivo' }))

    await waitFor(() => expect(clicked).toHaveLength(1))
    expect(api.callsTo(POST_EXPORT)[0]?.body).toEqual({ format: 'xlsx', guest_ids: ['p-d'] })
  })

  it('diz "Gerando o arquivo…" enquanto espera e mostra o erro sem perder a escolha', async () => {
    let release: (response: Response) => void = () => {}
    const pending = new Promise<Response>((resolve) => {
      release = resolve
    })
    const { user } = renderGuests({ [POST_EXPORT]: () => pending })
    const dialog = await openDialog(user)
    await user.click(within(dialog).getByRole('radio', { name: 'CSV' }))

    await user.click(within(dialog).getByRole('button', { name: 'Baixar arquivo' }))
    expect(await within(dialog).findByRole('status')).toHaveTextContent('Gerando o arquivo…')

    release(problemResponse(404, 'not_found'))
    expect(await within(dialog).findByRole('alert')).toHaveTextContent(
      'A lista mudou desde que vocês abriram esta janela. Fechem e abram de novo.',
    )
    expect(within(dialog).getByRole('radio', { name: 'CSV' })).toBeChecked()
    expect(clicked).toHaveLength(0)
  })

  it('falha de rede mantém o diálogo e avisa com calma', async () => {
    const { user } = renderGuests({
      [POST_EXPORT]: () => {
        throw new TypeError('Failed to fetch')
      },
    })
    const dialog = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Baixar arquivo' }))

    expect(await within(dialog).findByRole('alert')).toHaveTextContent(
      'Não conseguimos gerar o arquivo agora. Tentem de novo em instantes.',
    )
  })

  it('não oferece exportar quando nenhuma pessoa corresponde ao filtro', async () => {
    renderGuests(
      {},
      { lado: 'noiva', status: 'confirmado', faixa: 'isenta', probabilidade: 'fase2' },
    )
    await screen.findByText('Nenhuma pessoa corresponde')

    expect(screen.getByRole('button', { name: 'Exportar lista' })).toBeDisabled()
  })

  it('o texto da busca nunca viaja no pedido', async () => {
    const { user, api } = renderGuests({
      [POST_EXPORT]: file(XLSX, 'lista-de-convidados-2026-10-28.xlsx'),
    })
    await user.type(await screen.findByRole('searchbox', { name: /Buscar por nome/ }), 'Exemplo')
    const dialog = await openDialog(user)

    await user.click(within(dialog).getByRole('button', { name: 'Baixar arquivo' }))

    await waitFor(() => expect(api.callsTo(POST_EXPORT)).toHaveLength(1))
    expect(JSON.stringify(api.callsTo(POST_EXPORT)[0]?.body)).not.toContain('Exemplo')
    expect(api.callsTo(POST_EXPORT)[0]?.request.url).not.toContain('Exemplo')
    expect(api.callsTo(GET_GUESTS).length).toBeGreaterThan(0)
  })
})
