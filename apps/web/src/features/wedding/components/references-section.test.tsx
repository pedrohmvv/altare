import { screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { jsonResponse, problemResponse } from '@/test/fake-api'
import { renderScope } from '@/test/render-scope'

const BASE = '/api/v1/wedding/scope/categories/c-foto/references'
const LIST = `GET ${BASE}`
const HISTORY = 'GET /api/v1/wedding/scope/categories/c-foto/history'
const ARQUIVO = '0190a1b2-c3d4-7e5f-8a9b-0c1d2e3f4a5b'

const ref = (over: Record<string, unknown> = {}) => ({
  id: 'r1',
  kind: 'link',
  url: 'https://www.exemplo.com/mesa',
  domain: 'exemplo.com',
  file_id: null,
  title: 'Mesa de madeira',
  comment: 'gostamos da luz',
  by: 'Noivo',
  at: '2026-10-28T15:30:00Z',
  can_remove: true,
  ...over,
})

const abre = (handlers: Parameters<typeof renderScope>[0] = {}) =>
  renderScope({ [HISTORY]: jsonResponse(200, []), ...handlers }, { categoria: 'c-foto' })

const secao = async () => {
  const dialog = await screen.findByRole('dialog', { name: 'Fotografia Exemplo' })
  return within(await within(dialog).findByRole('region', { name: 'Referências' }))
}

describe('Referências da categoria (F-PLN-06)', () => {
  it('lista um link com o domínio, o título, o comentário e o autor, abrindo em outra aba', async () => {
    abre({ [LIST]: jsonResponse(200, [ref()]) })
    const refs = await secao()
    const link = await refs.findByRole('link', { name: /Mesa de madeira/ })
    expect(link).toHaveAttribute('href', 'https://www.exemplo.com/mesa')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', expect.stringContaining('noopener'))
    expect(refs.getByText('exemplo.com')).toBeVisible()
    expect(refs.getByText('gostamos da luz')).toBeVisible()
    expect(refs.getByText(/Noivo/)).toBeVisible()
  })

  it('mostra a imagem como miniatura que abre o arquivo inteiro', async () => {
    abre({
      [LIST]: jsonResponse(200, [
        ref({
          id: 'r2',
          kind: 'imagem',
          url: null,
          domain: null,
          file_id: ARQUIVO,
          title: 'Salão',
        }),
      ]),
    })
    const refs = await secao()
    const miniatura = await refs.findByRole('img', { name: 'Salão' })
    expect(miniatura).toHaveAttribute('src', `/api/v1/files/${ARQUIVO}`)
    expect(miniatura).toHaveAttribute('loading', 'lazy')
    expect(miniatura.closest('a')).toHaveAttribute('href', `/api/v1/files/${ARQUIVO}`)
  })

  it('um endereço que não é http nem https nunca vira link clicável, mesmo vindo do banco', async () => {
    abre({
      [LIST]: jsonResponse(200, [
        ref({ url: 'javascript:alert(1)', domain: null, title: 'Estranho' }),
      ]),
    })
    const refs = await secao()
    expect(await refs.findByText('Estranho')).toBeVisible()
    expect(refs.queryByRole('link')).not.toBeInTheDocument()
  })

  it('sem referências diz com calma', async () => {
    abre({ [LIST]: jsonResponse(200, []) })
    expect(await (await secao()).findByText('Nenhuma referência ainda.')).toBeVisible()
  })

  it('adiciona um link e a lista se atualiza', async () => {
    let lista: unknown[] = []
    const { api, user } = abre({
      [LIST]: () => jsonResponse(200, lista),
      [`POST ${BASE}/links`]: () => {
        lista = [ref()]
        return jsonResponse(201, lista)
      },
    })
    const refs = await secao()
    await user.click(await refs.findByRole('button', { name: 'Adicionar link' }))
    await user.type(
      refs.getByRole('textbox', { name: 'Endereço do link' }),
      ' https://www.exemplo.com/mesa ',
    )
    await user.type(refs.getByRole('textbox', { name: 'Título' }), 'Mesa de madeira')
    await user.click(refs.getByRole('button', { name: 'Guardar link' }))

    await waitFor(() => expect(api.callsTo(`POST ${BASE}/links`)).toHaveLength(1))
    expect(api.callsTo(`POST ${BASE}/links`)[0]?.body).toEqual({
      url: 'https://www.exemplo.com/mesa',
      title: 'Mesa de madeira',
      comment: null,
    })
    expect(await refs.findByRole('link', { name: /Mesa de madeira/ })).toBeVisible()
  })

  it('endereço sem http é recusado na tela, com a orientação, sem chamar a API', async () => {
    const { api, user } = abre({ [LIST]: jsonResponse(200, []) })
    const refs = await secao()
    await user.click(await refs.findByRole('button', { name: 'Adicionar link' }))
    await user.type(refs.getByRole('textbox', { name: 'Endereço do link' }), 'exemplo.com/mesa')
    await user.click(refs.getByRole('button', { name: 'Guardar link' }))
    expect(
      await refs.findByText('Cole um endereço completo, começando com http:// ou https://.'),
    ).toBeVisible()
    expect(api.callsTo(`POST ${BASE}/links`)).toHaveLength(0)
  })

  it('mostra a mensagem da API quando ela recusa o endereço', async () => {
    const { user } = abre({
      [LIST]: jsonResponse(200, []),
      [`POST ${BASE}/links`]: problemResponse(422, 'invalid_reference_url', {
        detail: 'Cole um endereço completo, começando com http:// ou https://.',
      }),
    })
    const refs = await secao()
    await user.click(await refs.findByRole('button', { name: 'Adicionar link' }))
    await user.type(
      refs.getByRole('textbox', { name: 'Endereço do link' }),
      'https://u:p@exemplo.com',
    )
    await user.click(refs.getByRole('button', { name: 'Guardar link' }))
    expect(await refs.findByText(/Cole um endereço completo/)).toBeVisible()
  })

  it('envia a imagem e só depois a guarda como referência', async () => {
    let lista: unknown[] = []
    const { api, user } = abre({
      [LIST]: () => jsonResponse(200, lista),
      'POST /api/v1/files': jsonResponse(201, {
        id: ARQUIVO,
        name: 'salao.png',
        content_type: 'image/png',
        size_bytes: 10,
        sha256: 'a'.repeat(64),
      }),
      [`POST ${BASE}/images`]: () => {
        lista = [
          ref({
            id: 'r2',
            kind: 'imagem',
            url: null,
            domain: null,
            file_id: ARQUIVO,
            title: 'Salão',
          }),
        ]
        return jsonResponse(201, lista)
      },
    })
    const refs = await secao()
    await user.click(await refs.findByRole('button', { name: 'Adicionar imagem' }))
    const arquivo = new File(['x'], 'salao.png', { type: 'image/png' })
    await user.upload(refs.getByLabelText('Imagem'), arquivo)
    await user.type(refs.getByRole('textbox', { name: 'Título' }), 'Salão')
    await user.click(refs.getByRole('button', { name: 'Guardar imagem' }))

    await waitFor(() => expect(api.callsTo(`POST ${BASE}/images`)).toHaveLength(1))
    expect(api.callsTo('POST /api/v1/files')).toHaveLength(1)
    expect(api.callsTo(`POST ${BASE}/images`)[0]?.body).toEqual({
      file_id: ARQUIVO,
      title: 'Salão',
      comment: null,
    })
    const ordem = api.calls.map((c) => `${c.method} ${c.path}`)
    expect(ordem.indexOf('POST /api/v1/files')).toBeLessThan(ordem.indexOf(`POST ${BASE}/images`))
    expect(await refs.findByRole('img', { name: 'Salão' })).toBeVisible()
  })

  it('o seletor de arquivo aceita só imagens e abre a câmera ou a galeria no celular', async () => {
    const { user } = abre({ [LIST]: jsonResponse(200, []) })
    const refs = await secao()
    await user.click(await refs.findByRole('button', { name: 'Adicionar imagem' }))
    const campo = refs.getByLabelText('Imagem')
    expect(campo).toHaveAttribute('type', 'file')
    expect(campo).toHaveAttribute('accept', 'image/jpeg,image/png,image/webp')
    expect(campo).not.toHaveAttribute('capture')
  })

  it('arquivo que não é imagem é recusado na tela e nada é enviado', async () => {
    const { api, user } = abre({ [LIST]: jsonResponse(200, []) })
    const refs = await secao()
    await user.click(await refs.findByRole('button', { name: 'Adicionar imagem' }))
    await user.upload(
      refs.getByLabelText('Imagem'),
      new File(['x'], 'a.pdf', { type: 'application/pdf' }),
    )
    await user.click(refs.getByRole('button', { name: 'Guardar imagem' }))
    expect(await refs.findByText('Escolha uma imagem JPG, PNG ou WebP.')).toBeVisible()
    expect(api.callsTo('POST /api/v1/files')).toHaveLength(0)
  })

  it('sem escolher o arquivo, pede o arquivo', async () => {
    const { user } = abre({ [LIST]: jsonResponse(200, []) })
    const refs = await secao()
    await user.click(await refs.findByRole('button', { name: 'Adicionar imagem' }))
    await user.click(refs.getByRole('button', { name: 'Guardar imagem' }))
    expect(await refs.findByText('Escolha uma imagem JPG, PNG ou WebP.')).toBeVisible()
  })

  it('mostra a mensagem da API quando o envio é recusado (arquivo com extensão trocada)', async () => {
    const { user } = abre({
      [LIST]: jsonResponse(200, []),
      'POST /api/v1/files': problemResponse(422, 'unsupported_file_type', {
        detail: 'Envie um PDF ou uma imagem JPG, PNG ou WebP.',
      }),
    })
    const refs = await secao()
    await user.click(await refs.findByRole('button', { name: 'Adicionar imagem' }))
    await user.upload(
      refs.getByLabelText('Imagem'),
      new File(['nao sou imagem'], 'foto.png', { type: 'image/png' }),
    )
    await user.click(refs.getByRole('button', { name: 'Guardar imagem' }))
    expect(await refs.findByText(/Envie um PDF ou uma imagem/)).toBeVisible()
  })

  it('só o autor vê o Remover, e remove depois de confirmar', async () => {
    let lista = [
      ref(),
      ref({
        id: 'r3',
        title: 'Do outro',
        by: 'Noiva',
        can_remove: false,
        url: 'https://exemplo.com/b',
      }),
    ]
    const { api, user } = abre({
      [LIST]: () => jsonResponse(200, lista),
      [`DELETE ${BASE}/r1`]: () => {
        lista = [lista[1] as (typeof lista)[number]]
        return jsonResponse(200, lista)
      },
    })
    const refs = await secao()
    expect(await refs.findByRole('button', { name: 'Remover Mesa de madeira' })).toBeVisible()
    expect(refs.queryByRole('button', { name: 'Remover Do outro' })).not.toBeInTheDocument()

    await user.click(refs.getByRole('button', { name: 'Remover Mesa de madeira' }))
    const confirmacao = await screen.findByRole('dialog', { name: 'Remover esta referência?' })
    expect(api.callsTo(`DELETE ${BASE}/r1`)).toHaveLength(0)
    await user.click(within(confirmacao).getByRole('button', { name: 'Sim, remover' }))
    await waitFor(() => expect(api.callsTo(`DELETE ${BASE}/r1`)).toHaveLength(1))
    await waitFor(() =>
      expect(refs.queryByRole('link', { name: /Mesa de madeira/ })).not.toBeInTheDocument(),
    )
  })
})
