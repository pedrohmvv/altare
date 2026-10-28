/** Textos da feature (altare-conteudo-copy). Os do formulário são os do guia de identidade, pág. 37. */
export const copy = {
  login: {
    title: 'Bem-vindos ao Altare.',
    subtitle: 'Entre com o seu usuário.',
    usernameLabel: 'Usuário',
    usernamePlaceholder: 'noivo ou noiva',
    passwordLabel: 'Senha',
    submit: 'Entrar',
    note: 'Acesso exclusivo do casal.',
    usernameRequired: 'Informe o usuário.',
    passwordRequired: 'Informe a senha.',
    // O `detail` do servidor vale para os demais erros; estes dois dependem de algo que só o
    // cliente sabe (a espera) ou de a resposta nem ter chegado.
    tooManyAttempts: (minutes: number) =>
      `Houve muitas tentativas de entrada. Tentem de novo em ${minutes} ${minutes === 1 ? 'minuto' : 'minutos'}.`,
    network:
      'Não conseguimos falar com o servidor. O que vocês digitaram continua aqui: é só tentar de novo.',
    brandAlt: 'Altare',
  },
  session: {
    profileNoivo: 'Noivo',
    profileNoiva: 'Noiva',
    individualSession: 'sessão individual',
    menuTitle: 'Sessão',
    signOut: 'Sair',
    signingOut: 'Saindo…',
    signOutFailed: 'Não foi possível sair agora. Tentem de novo em instantes.',
  },
} as const
