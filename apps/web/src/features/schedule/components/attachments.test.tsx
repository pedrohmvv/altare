import { fireEvent, screen, waitFor, within } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { type FakeApiHandlers, jsonResponse, problemResponse } from '@/test/fake-api'
import {
  DELETE_ATTACHMENT,
  GET_SCHEDULE,
  POST_ATTACHMENT_FILE,
  POST_ATTACHMENT_LINK,
  POST_CHECKLIST,
  POST_FILE,
  renderSchedule,
} from '@/test/render-schedule'
import {
  attachment,
  checklistItem,
  ID,
  imageAttachment,
  pdfAttachment,
  scheduleWithAttachments,
  scheduleWithTasks,
  task,
} from '@/test/schedule-fixtures'
import { memory } from '@/test/schedule-helpers'
import type { Attachment } from '../api/schedule'

// F-CRN-08: anexos e links no marco e na avulsa. Aqui, os do marco; o componente é o mesmo.
const PDF = pdfAttachment({ id: ID.anexoPdf, title: null, comment: 'Versão assinada.' })
const IMAGE = imageAttachment({ id: ID.anexoImagem, by: 'Noiva', can_remove: false })
const LINK = attachment({
  id: ID.anexoLink,
  title: 'Proposta Exemplo',
  comment: null,
  url: 'https://www.exemplo.test/proposta',
  domain: 'exemplo.test',
})

type Store = ReturnType<typeof memory>
type Routes = FakeApiHandlers

function setup(attachments: Attachment[] = [], routes: (store: Store) => Routes = () => ({})) {
  const store = memory(scheduleWithAttachments(ID.destravado, attachments))
  const view = renderSchedule(
    { [GET_SCHEDULE]: store.get, ...routes(store) },
    {
      marco: ID.destravado,
    },
  )
  return { store, ...view }
}

async function section() {
  const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
  return within(await within(painel).findByRole('region', { name: 'Anexos' }))
}

const fileRoutes = (store: Store): Routes => ({
  [POST_FILE]: jsonResponse(201, {
    id: ID.arquivoNovo,
    name: 'orcamento-exemplo.pdf',
    content_type: 'application/pdf',
    size_bytes: 2048,
  }),
  [POST_ATTACHMENT_FILE('milestones', ID.destravado)]: store.writeAttachments(
    ID.destravado,
    (items) => [
      ...items,
      pdfAttachment({
        id: ID.anexoNovo,
        file: {
          id: ID.arquivoNovo,
          name: 'orcamento-exemplo.pdf',
          content_type: 'application/pdf',
          size_bytes: 2048,
        },
      }),
    ],
  ),
})

const pdfFile = (name = 'orcamento-exemplo.pdf') =>
  new File(['%PDF-1.4 exemplo'], name, { type: 'application/pdf' })

async function openFileForm(
  user: ReturnType<typeof renderSchedule>['user'],
  region: Awaited<ReturnType<typeof section>>,
) {
  await user.click(region.getByRole('button', { name: 'Adicionar arquivo' }))
  return region.getByLabelText('Arquivo') as HTMLInputElement
}

describe('anexos do painel (F-CRN-08)', () => {
  it('aparece logo depois do Checklist no painel do marco, antes da Janela', async () => {
    setup([PDF])
    const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
    const titles = within(painel)
      .getAllByRole('heading', { level: 3 })
      .map((heading) => heading.textContent)

    const checklist = titles.indexOf('Checklist')
    expect(checklist).toBeGreaterThanOrEqual(0)
    expect(titles[checklist + 1]).toBe('Anexos')
    expect(titles.indexOf('Janela')).toBeGreaterThan(checklist + 1)
  })

  it('aparece logo depois do Checklist no painel da avulsa, antes de Excluir avulsa', async () => {
    const base = scheduleWithTasks([
      task({
        id: ID.avulsaUm,
        title: 'Avulsa Exemplo',
        checklist: [checklistItem({ id: ID.itemUm, text: 'Item Exemplo Um' })],
        attachments: [PDF],
      }),
    ])
    renderSchedule({ [GET_SCHEDULE]: jsonResponse(200, base) }, { avulsa: ID.avulsaUm })
    const painel = await screen.findByRole('dialog', { name: 'Avulsa Exemplo' })

    const titles = within(painel)
      .getAllByRole('heading', { level: 3 })
      .map((heading) => heading.textContent)
    expect(titles.indexOf('Anexos')).toBe(titles.indexOf('Checklist') + 1)
    const region = within(painel).getByRole('region', { name: 'Anexos' })
    expect(within(region).getByText('contrato-exemplo.pdf')).toBeVisible()
    const checklist = within(painel).getByRole('region', { name: 'Checklist' })
    const remove = within(painel).getByRole('button', { name: 'Excluir avulsa' })
    expect(
      region.compareDocumentPosition(checklist) & Node.DOCUMENT_POSITION_PRECEDING,
    ).toBeTruthy()
    expect(region.compareDocumentPosition(remove) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  })

  it('sem anexos, diz com calma e oferece as duas formas de anexar', async () => {
    setup([])
    const region = await section()

    expect(
      region.getByText('Ainda sem anexos. Guardem aqui a proposta, o contrato ou um link útil.'),
    ).toBeVisible()
    expect(region.queryByRole('list')).not.toBeInTheDocument()
    expect(region.getByRole('button', { name: 'Adicionar arquivo' })).toBeVisible()
    expect(region.getByRole('button', { name: 'Adicionar link' })).toBeVisible()
  })

  it('tem uma região de alerta vazia desde o início e uma de status', async () => {
    setup([])
    const region = await section()

    expect(region.getAllByRole('alert').some((alert) => alert.textContent === '')).toBe(true)
    expect(region.getByRole('status')).toBeEmptyDOMElement()
  })

  it('lista o PDF com o nome, o tamanho, o comentário, quem anexou e quando', async () => {
    setup([PDF])
    const region = await section()

    const item = within(region.getByRole('listitem'))
    const link = item.getByRole('link', { name: /contrato-exemplo\.pdf/ })
    expect(link).toHaveAttribute('href', `/api/v1/files/${ID.arquivoPdf}`)
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(item.getByText('1,4 MB')).toBeVisible()
    expect(item.getByText('Versão assinada.')).toBeVisible()
    expect(item.getByText(/Noivo · 27 out 2026, 12:30/)).toBeVisible()
  })

  it('lista a imagem como arquivo, sem miniatura', async () => {
    setup([IMAGE])
    const region = await section()

    expect(region.getByRole('link', { name: /planta-exemplo\.png/ })).toHaveAttribute(
      'href',
      `/api/v1/files/${ID.arquivoImagem}`,
    )
    expect(region.getByText('200 KB')).toBeVisible()
    expect(region.queryByRole('img')).not.toBeInTheDocument()
  })

  it('lista o link com o título e o domínio, e o abre em outra aba', async () => {
    setup([LINK])
    const region = await section()

    const link = region.getByRole('link', { name: /Proposta Exemplo/ })
    expect(link).toHaveAttribute('href', 'https://www.exemplo.test/proposta')
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
    expect(region.getByText('exemplo.test')).toBeVisible()
  })

  it('sem título, o link é nomeado pelo domínio e o arquivo, pelo nome', async () => {
    setup([attachment({ id: ID.anexoLink, title: null }), PDF])
    const region = await section()

    expect(region.getByRole('link', { name: /exemplo\.test/ })).toBeVisible()
    expect(region.getByRole('link', { name: /contrato-exemplo\.pdf/ })).toBeVisible()
  })

  it('um endereço que não é http nem https vindo do banco vira texto, nunca link', async () => {
    setup([
      attachment({
        id: ID.anexoLink,
        title: 'Endereço Exemplo',
        url: 'javascript:alert(1)',
        domain: null,
      }),
    ])
    const region = await section()

    expect(region.getByText('Endereço Exemplo')).toBeVisible()
    expect(region.queryByRole('link')).not.toBeInTheDocument()
  })

  it('só o autor vê Remover, com o nome de cada anexo no botão', async () => {
    setup([PDF, IMAGE, LINK])
    const region = await section()

    expect(region.getByRole('button', { name: 'Remover contrato-exemplo.pdf' })).toBeVisible()
    expect(region.getByRole('button', { name: 'Remover Proposta Exemplo' })).toBeVisible()
    expect(region.queryByRole('button', { name: /Remover planta-exemplo/ })).not.toBeInTheDocument()
  })

  describe('remover', () => {
    const removeRoutes = (store: Store): Routes => ({
      [DELETE_ATTACHMENT(ID.anexoPdf)]: store.removeAttachment(ID.anexoPdf),
    })

    async function askToRemove(
      user: ReturnType<typeof renderSchedule>['user'],
      region: Awaited<ReturnType<typeof section>>,
    ) {
      const origin = region.getByRole('button', { name: 'Remover contrato-exemplo.pdf' })
      await user.click(origin)
      const confirmation = await screen.findByRole('alertdialog', {
        name: 'Remover o anexo “contrato-exemplo.pdf”?',
      })
      return { origin, confirmation }
    }

    it('pede confirmação num AlertDialog que diz que sai da lista e o registro fica guardado', async () => {
      const { user } = setup([PDF], removeRoutes)
      const region = await section()

      const { confirmation } = await askToRemove(user, region)

      expect(confirmation).toHaveAccessibleDescription(/sai da lista/)
      expect(confirmation).toHaveAccessibleDescription(/registro fica guardado/)
      expect(confirmation).not.toHaveTextContent(/apagad|exclu/i)
      expect(within(confirmation).getByRole('button', { name: 'Cancelar' })).toHaveFocus()
      expect(
        within(confirmation).queryByRole('button', { name: 'Desfazer' }),
      ).not.toBeInTheDocument()
    })

    it('cancelar não envia nada e devolve o foco ao botão que abriu', async () => {
      const { api, user } = setup([PDF], removeRoutes)
      const region = await section()
      const { origin, confirmation } = await askToRemove(user, region)

      await user.click(within(confirmation).getByRole('button', { name: 'Cancelar' }))

      expect(api.callsTo(DELETE_ATTACHMENT(ID.anexoPdf))).toHaveLength(0)
      await waitFor(() => expect(origin).toHaveFocus())
      expect(region.getByText('contrato-exemplo.pdf')).toBeVisible()
    })

    it('Esc fecha só a confirmação: o painel continua e o foco volta ao botão', async () => {
      const { api, user } = setup([PDF], removeRoutes)
      const region = await section()
      const { origin } = await askToRemove(user, region)

      await user.keyboard('{Escape}')

      await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
      expect(screen.getByRole('dialog', { name: 'Marco Exemplo Destravado' })).toBeVisible()
      expect(api.callsTo(DELETE_ATTACHMENT(ID.anexoPdf))).toHaveLength(0)
      await waitFor(() => expect(origin).toHaveFocus())
    })

    it('confirmar remove da lista, leva o foco ao título Anexos e anuncia a remoção', async () => {
      const { api, user } = setup([PDF, LINK], removeRoutes)
      const region = await section()
      const { confirmation } = await askToRemove(user, region)

      await user.click(within(confirmation).getByRole('button', { name: 'Remover anexo' }))

      await waitFor(() => expect(api.callsTo(DELETE_ATTACHMENT(ID.anexoPdf))).toHaveLength(1))
      await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
      await waitFor(() =>
        expect(region.queryByText('contrato-exemplo.pdf')).not.toBeInTheDocument(),
      )
      expect(region.getByText('Proposta Exemplo')).toBeVisible()
      await waitFor(() =>
        expect(region.getByRole('heading', { level: 3, name: 'Anexos' })).toHaveFocus(),
      )
      expect(region.getByRole('status')).toHaveTextContent('Anexo removido.')
    })

    it('um erro do servidor aparece dentro da confirmação, que continua aberta', async () => {
      const { user } = setup([PDF], () => ({
        [DELETE_ATTACHMENT(ID.anexoPdf)]: problemResponse(403, 'forbidden', {
          detail: 'Só quem anexou pode remover.',
        }),
      }))
      const region = await section()
      const { confirmation } = await askToRemove(user, region)

      await user.click(within(confirmation).getByRole('button', { name: 'Remover anexo' }))

      await waitFor(() =>
        expect(within(confirmation).getByRole('alert')).toHaveTextContent(
          'Só quem anexou pode remover.',
        ),
      )
      expect(screen.getByRole('alertdialog')).toBeVisible()
      expect(within(confirmation).getByRole('button', { name: 'Remover anexo' })).toBeEnabled()
    })

    it('uma falha de rede avisa dentro da confirmação e deixa tentar de novo', async () => {
      const { user } = setup([PDF], () => ({
        [DELETE_ATTACHMENT(ID.anexoPdf)]: () => {
          throw new TypeError('Failed to fetch')
        },
      }))
      const region = await section()
      const { confirmation } = await askToRemove(user, region)

      await user.click(within(confirmation).getByRole('button', { name: 'Remover anexo' }))

      await waitFor(() =>
        expect(within(confirmation).getByRole('alert')).toHaveTextContent(
          /Não conseguimos remover o anexo/,
        ),
      )
      expect(within(confirmation).getByRole('button', { name: 'Remover anexo' })).toBeEnabled()
    })
  })

  describe('adicionar arquivo', () => {
    it('o campo aceita PDF e imagem e não pede a câmera: o sistema oferece câmera, galeria ou arquivos', async () => {
      const { user } = setup([], fileRoutes)
      const region = await section()

      const input = await openFileForm(user, region)

      expect(input).toHaveAttribute('type', 'file')
      expect(input).toHaveAttribute('accept', 'application/pdf,image/jpeg,image/png,image/webp')
      expect(input).not.toHaveAttribute('capture')
      expect(input).not.toHaveAttribute('multiple')
      expect(input).toHaveAccessibleDescription(/20 MB/)
      expect(region.getByLabelText('Título do anexo')).toHaveAccessibleDescription('Opcional.')
      expect(region.getByLabelText('Comentário')).toHaveAccessibleDescription('Opcional.')
    })

    it('envia o arquivo e só depois o vínculo, com o id que o envio devolveu', async () => {
      const { api, user } = setup([], fileRoutes)
      const region = await section()
      const input = await openFileForm(user, region)

      await user.upload(input, pdfFile())
      await user.type(region.getByLabelText('Título do anexo'), 'Orçamento Exemplo')
      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      await waitFor(() =>
        expect(api.callsTo(POST_ATTACHMENT_FILE('milestones', ID.destravado))).toHaveLength(1),
      )
      const order = api.calls
        .map((call) => `${call.method} ${call.path}`)
        .filter((route) => route === POST_FILE || route.includes('/attachments/'))
      expect(order).toEqual([POST_FILE, POST_ATTACHMENT_FILE('milestones', ID.destravado)])
      expect(api.callsTo(POST_ATTACHMENT_FILE('milestones', ID.destravado))[0]?.body).toEqual({
        file_id: ID.arquivoNovo,
        title: 'Orçamento Exemplo',
        comment: null,
      })
      expect(await region.findByText('orcamento-exemplo.pdf')).toBeVisible()
    })

    it('depois de anexar, a seção anuncia, fecha o formulário e leva o foco ao título', async () => {
      const { user } = setup([], fileRoutes)
      const region = await section()
      await user.upload(await openFileForm(user, region), pdfFile())

      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      await waitFor(() => expect(region.getByRole('status')).toHaveTextContent('Anexo adicionado.'))
      expect(region.queryByLabelText('Arquivo')).not.toBeInTheDocument()
      expect(region.getByRole('button', { name: 'Adicionar arquivo' })).toBeVisible()
      expect(region.getByRole('heading', { level: 3, name: 'Anexos' })).toHaveFocus()
    })

    it('enquanto envia, o botão fica ocupado e o status anuncia o envio', async () => {
      let release: () => void = () => {}
      const { user } = setup([], (store) => ({
        ...fileRoutes(store),
        [POST_FILE]: () =>
          new Promise<Response>((resolve) => {
            release = () =>
              resolve(
                jsonResponse(201, {
                  id: ID.arquivoNovo,
                  name: 'orcamento-exemplo.pdf',
                  content_type: 'application/pdf',
                  size_bytes: 2048,
                }),
              )
          }),
      }))
      const region = await section()
      await user.upload(await openFileForm(user, region), pdfFile())

      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      await waitFor(() =>
        expect(region.getByRole('button', { name: 'Anexar arquivo' })).toHaveAttribute(
          'aria-busy',
          'true',
        ),
      )
      expect(region.getByRole('status')).toHaveTextContent('Enviando o anexo…')
      release()
      await waitFor(() => expect(region.getByRole('status')).toHaveTextContent('Anexo adicionado.'))
    })

    it('o envio do arquivo não entra na fila das escritas do cronograma: o checklist não espera', async () => {
      let release: () => void = () => {}
      const { api, user } = setup([], (store) => ({
        ...fileRoutes(store),
        [POST_FILE]: () =>
          new Promise<Response>((resolve) => {
            release = () =>
              resolve(
                jsonResponse(201, {
                  id: ID.arquivoNovo,
                  name: 'orcamento-exemplo.pdf',
                  content_type: 'application/pdf',
                  size_bytes: 2048,
                }),
              )
          }),
        [POST_CHECKLIST('milestones', ID.destravado)]: store.writeChecklist(
          ID.destravado,
          (items) => [...items, checklistItem({ id: ID.itemNovo, text: 'Item Exemplo Novo' })],
        ),
      }))
      const painel = await screen.findByRole('dialog', { name: 'Marco Exemplo Destravado' })
      const region = within(await within(painel).findByRole('region', { name: 'Anexos' }))
      await user.upload(await openFileForm(user, region), pdfFile())
      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))
      await waitFor(() => expect(api.callsTo(POST_FILE)).toHaveLength(1))

      const checklist = within(within(painel).getByRole('region', { name: 'Checklist' }))
      await user.type(checklist.getByRole('textbox', { name: 'Novo item' }), 'Item Exemplo Novo')
      await user.click(checklist.getByRole('button', { name: 'Adicionar item' }))

      // O envio de 20 MB segue pendente e a escrita do checklist já foi ao servidor.
      await waitFor(() =>
        expect(api.callsTo(POST_CHECKLIST('milestones', ID.destravado))).toHaveLength(1),
      )
      expect(api.callsTo(POST_ATTACHMENT_FILE('milestones', ID.destravado))).toHaveLength(0)
      release()
      await waitFor(() =>
        expect(api.callsTo(POST_ATTACHMENT_FILE('milestones', ID.destravado))).toHaveLength(1),
      )
    })

    it('um tipo que não é PDF nem imagem é recusado no navegador, sem chamar a API', async () => {
      const { api, user } = setup([], fileRoutes)
      const region = await section()
      const input = await openFileForm(user, region)

      // O `accept` só filtra o seletor do sistema: o teste entrega o arquivo de tipo errado direto.
      fireEvent.change(input, {
        target: { files: [new File(['texto'], 'notas.txt', { type: 'text/plain' })] },
      })
      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      expect(await region.findByText(/Escolham um PDF ou uma imagem/)).toBeVisible()
      expect(input).toHaveAttribute('aria-invalid', 'true')
      expect(api.callsTo(POST_FILE)).toHaveLength(0)
    })

    it('sem arquivo escolhido, pede o arquivo e não chama a API', async () => {
      const { api, user } = setup([], fileRoutes)
      const region = await section()
      await openFileForm(user, region)

      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      expect(await region.findByText('Escolham um arquivo.')).toBeVisible()
      expect(api.callsTo(POST_FILE)).toHaveLength(0)
    })

    it('a recusa da API (arquivo grande, tipo ou conteúdo) aparece no campo e deixa tentar outro', async () => {
      const { api, user } = setup([], (store) => ({
        ...fileRoutes(store),
        [POST_FILE]: problemResponse(422, 'file_too_large', {
          detail: 'O arquivo passa de 20 MB.',
        }),
      }))
      const region = await section()
      const input = await openFileForm(user, region)
      await user.upload(input, pdfFile())

      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      expect(await region.findByText('O arquivo passa de 20 MB.')).toBeVisible()
      expect(input).toHaveAttribute('aria-invalid', 'true')
      expect(api.callsTo(POST_ATTACHMENT_FILE('milestones', ID.destravado))).toHaveLength(0)
      expect(region.getByRole('button', { name: 'Anexar arquivo' })).toBeEnabled()
    })

    it('se o vínculo falha, o aviso diz o motivo e o formulário continua com o que foi escrito', async () => {
      const { user } = setup([], (store) => ({
        ...fileRoutes(store),
        [POST_ATTACHMENT_FILE('milestones', ID.destravado)]: problemResponse(
          422,
          'invalid_schedule_value',
          { detail: 'O título passa de 120 caracteres.' },
        ),
      }))
      const region = await section()
      await user.upload(await openFileForm(user, region), pdfFile())
      await user.type(region.getByLabelText('Título do anexo'), 'Título Exemplo')

      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      await waitFor(() =>
        expect(
          region.getAllByRole('alert').find((alert) => alert.textContent !== ''),
        ).toHaveTextContent('O título passa de 120 caracteres.'),
      )
      expect(region.getByLabelText('Título do anexo')).toHaveValue('Título Exemplo')
    })

    it('uma falha de rede usa o texto padrão e mantém o formulário', async () => {
      const { user } = setup([], (store) => ({
        ...fileRoutes(store),
        [POST_FILE]: () => {
          throw new TypeError('Failed to fetch')
        },
      }))
      const region = await section()
      await user.upload(await openFileForm(user, region), pdfFile())

      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      await waitFor(() =>
        expect(
          region.getAllByRole('alert').find((alert) => alert.textContent !== ''),
        ).toHaveTextContent(/Não conseguimos anexar agora/),
      )
      expect(region.getByLabelText('Arquivo')).toBeVisible()
    })

    it('cancelar fecha o formulário e devolve o foco ao botão que o abriu', async () => {
      const { user } = setup([], fileRoutes)
      const region = await section()
      await openFileForm(user, region)

      await user.click(region.getByRole('button', { name: 'Cancelar' }))

      expect(region.queryByLabelText('Arquivo')).not.toBeInTheDocument()
      await waitFor(() =>
        expect(region.getByRole('button', { name: 'Adicionar arquivo' })).toHaveFocus(),
      )
    })
  })

  describe('adicionar link', () => {
    const linkRoutes = (store: Store): Routes => ({
      [POST_ATTACHMENT_LINK('milestones', ID.destravado)]: store.writeAttachments(
        ID.destravado,
        (items) => [...items, attachment({ id: ID.anexoNovo, title: 'Proposta Exemplo' })],
      ),
    })

    it('envia o endereço, o título e o comentário, e deixa em branco o que não foi escrito', async () => {
      const { api, user } = setup([], linkRoutes)
      const region = await section()
      await user.click(region.getByRole('button', { name: 'Adicionar link' }))

      await user.type(region.getByLabelText('Endereço do link'), 'https://exemplo.test/pagina')
      await user.type(region.getByLabelText('Título do anexo'), 'Proposta Exemplo')
      await user.click(region.getByRole('button', { name: 'Anexar link' }))

      await waitFor(() =>
        expect(api.callsTo(POST_ATTACHMENT_LINK('milestones', ID.destravado))).toHaveLength(1),
      )
      expect(api.callsTo(POST_ATTACHMENT_LINK('milestones', ID.destravado))[0]?.body).toEqual({
        url: 'https://exemplo.test/pagina',
        title: 'Proposta Exemplo',
        comment: null,
      })
      expect(await region.findByRole('link', { name: /Proposta Exemplo/ })).toBeVisible()
      await waitFor(() => expect(region.getByRole('status')).toHaveTextContent('Anexo adicionado.'))
      expect(region.getByRole('heading', { level: 3, name: 'Anexos' })).toHaveFocus()
    })

    it('um endereço sem http nem https é recusado no navegador, sem chamar a API', async () => {
      const { api, user } = setup([], linkRoutes)
      const region = await section()
      await user.click(region.getByRole('button', { name: 'Adicionar link' }))

      await user.type(region.getByLabelText('Endereço do link'), 'javascript:alert(1)')
      await user.click(region.getByRole('button', { name: 'Anexar link' }))

      expect(
        await region.findByText(
          'Informem um endereço completo, começando com http:// ou https://.',
        ),
      ).toBeVisible()
      expect(region.getByLabelText('Endereço do link')).toHaveAttribute('aria-invalid', 'true')
      expect(api.callsTo(POST_ATTACHMENT_LINK('milestones', ID.destravado))).toHaveLength(0)
    })

    it('a recusa da API aparece no campo do endereço e o que foi escrito continua', async () => {
      const { user } = setup([], () => ({
        [POST_ATTACHMENT_LINK('milestones', ID.destravado)]: problemResponse(
          422,
          'invalid_attachment_url',
          { detail: 'Esse endereço não é válido.' },
        ),
      }))
      const region = await section()
      await user.click(region.getByRole('button', { name: 'Adicionar link' }))
      await user.type(region.getByLabelText('Endereço do link'), 'https://exemplo.test')

      await user.click(region.getByRole('button', { name: 'Anexar link' }))

      expect(await region.findByText('Esse endereço não é válido.')).toBeVisible()
      expect(region.getByLabelText('Endereço do link')).toHaveValue('https://exemplo.test')
    })

    it('abrir o formulário do link leva o foco ao campo do endereço', async () => {
      const { user } = setup([], linkRoutes)
      const region = await section()

      await user.click(region.getByRole('button', { name: 'Adicionar link' }))

      expect(region.getByLabelText('Endereço do link')).toHaveFocus()
    })
  })

  describe('envio pendente', () => {
    const holdUpload = (store: Store) => {
      const gate = { release: () => {} }
      const routes: Routes = {
        ...fileRoutes(store),
        [POST_FILE]: () =>
          new Promise<Response>((resolve) => {
            gate.release = () =>
              resolve(
                jsonResponse(201, {
                  id: ID.arquivoNovo,
                  name: 'orcamento-exemplo.pdf',
                  content_type: 'application/pdf',
                  size_bytes: 2048,
                }),
              )
          }),
      }
      return { gate, routes }
    }

    it('o Cancelar do arquivo fica desabilitado enquanto envia; ao terminar, o anexo aparece e é anunciado', async () => {
      const held = { gate: { release: () => {} } }
      const { user } = setup([], (store) => {
        const { gate, routes } = holdUpload(store)
        held.gate = gate
        return routes
      })
      const region = await section()
      await user.upload(await openFileForm(user, region), pdfFile())

      await user.click(region.getByRole('button', { name: 'Anexar arquivo' }))

      await waitFor(() => expect(region.getByRole('button', { name: 'Cancelar' })).toBeDisabled())
      held.gate.release()
      expect(await region.findByText('orcamento-exemplo.pdf')).toBeVisible()
      await waitFor(() => expect(region.getByRole('status')).toHaveTextContent('Anexo adicionado.'))
    })

    it('o Cancelar do link fica desabilitado enquanto o vínculo está no ar; ao terminar, anuncia', async () => {
      let release: () => void = () => {}
      const { user } = setup([], (store) => ({
        [POST_ATTACHMENT_LINK('milestones', ID.destravado)]: () =>
          new Promise<Response>((resolve) => {
            release = () =>
              resolve(
                store.writeAttachments(ID.destravado, (items) => [
                  ...items,
                  attachment({ id: ID.anexoNovo, title: 'Proposta Exemplo' }),
                ])(),
              )
          }),
      }))
      const region = await section()
      await user.click(region.getByRole('button', { name: 'Adicionar link' }))
      await user.type(region.getByLabelText('Endereço do link'), 'https://exemplo.test/pagina')

      await user.click(region.getByRole('button', { name: 'Anexar link' }))

      await waitFor(() => expect(region.getByRole('button', { name: 'Cancelar' })).toBeDisabled())
      release()
      expect(await region.findByRole('link', { name: /Proposta Exemplo/ })).toBeVisible()
      await waitFor(() => expect(region.getByRole('status')).toHaveTextContent('Anexo adicionado.'))
    })
  })

  it('Esc com a remoção pendente não fecha e o erro aparece dentro da confirmação', async () => {
    let release: () => void = () => {}
    const { user } = setup([PDF], () => ({
      [DELETE_ATTACHMENT(ID.anexoPdf)]: () =>
        new Promise<Response>((resolve) => {
          release = () =>
            resolve(problemResponse(403, 'forbidden', { detail: 'Só quem anexou pode remover.' }))
        }),
    }))
    const region = await section()
    await user.click(region.getByRole('button', { name: 'Remover contrato-exemplo.pdf' }))
    const confirmation = await screen.findByRole('alertdialog')
    await user.click(within(confirmation).getByRole('button', { name: 'Remover anexo' }))
    await waitFor(() =>
      expect(within(confirmation).getByRole('button', { name: 'Cancelar' })).toBeDisabled(),
    )

    await user.keyboard('{Escape}')

    expect(screen.getByRole('alertdialog')).toBeVisible()
    release()
    await waitFor(() =>
      expect(within(confirmation).getByRole('alert')).toHaveTextContent(
        'Só quem anexou pode remover.',
      ),
    )
  })

  it.each([
    ['arquivo', 'Adicionar arquivo', 'Arquivo'],
    ['link', 'Adicionar link', 'Endereço do link'],
  ])(
    'abrir o formulário do %s e cancelar logo em seguida não deixa erro na tela',
    async (_name, open, field) => {
      const { user } = setup([])
      const region = await section()
      const opener = region.getByRole('button', { name: open })
      await user.click(opener)
      expect(region.getByLabelText(field)).toHaveFocus()

      await user.click(region.getByRole('button', { name: 'Cancelar' }))

      expect(region.queryByLabelText(field)).not.toBeInTheDocument()
      expect(region.getAllByRole('alert').every((alert) => alert.textContent === '')).toBe(true)
      expect(region.queryByText(/Escolham|Informem/)).not.toBeInTheDocument()
      await waitFor(() => expect(region.getByRole('button', { name: open })).toHaveFocus())
    },
  )

  it.each([
    ['arquivo', 'Adicionar arquivo', 'Arquivo'],
    ['link', 'Adicionar link', 'Endereço do link'],
  ])(
    'apertar o Cancelar do %s não valida o campo vazio antes do clique: o erro empurraria o botão e o clique se perderia',
    async (_name, open, field) => {
      const { user } = setup([])
      const region = await section()
      await user.click(region.getByRole('button', { name: open }))

      await user.pointer({
        keys: '[MouseLeft>]',
        target: region.getByRole('button', { name: 'Cancelar' }),
      })

      expect(region.getByLabelText(field)).toHaveFocus()
      expect(region.queryByText(/Escolham|Informem/)).not.toBeInTheDocument()
    },
  )

  it('com onTouched, o erro do endereço aparece ao sair do campo vazio', async () => {
    const { user } = setup([])
    const region = await section()
    await user.click(region.getByRole('button', { name: 'Adicionar link' }))

    await user.tab()

    expect(
      await region.findByText('Informem um endereço completo, começando com http:// ou https://.'),
    ).toBeVisible()
  })
})
