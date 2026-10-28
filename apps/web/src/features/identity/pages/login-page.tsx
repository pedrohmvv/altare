import { zodResolver } from '@hookform/resolvers/zod'
import { CircleAlert } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ApiError } from '@/lib/api/errors'
import { useLogin } from '../api/use-login'
import { copy } from '../copy'
import { type LoginValues, loginSchema } from '../schemas/login'

export interface LoginPageProps {
  /** Chamada depois que a sessão foi aberta; quem sabe para onde ir é a rota. */
  onAuthenticated: () => void
}

const FORM_FIELDS = ['username', 'password'] as const

/**
 * Tela de login, página 37 do guia. No desktop, o arco duplo emoldura o lockup vertical, com o ramo
 * na base, ao lado do cartão; no celular fica só o lockup pequeno acima do cartão, porque o arco
 * passaria atrás do formulário, o que a própria página proíbe.
 */
export function LoginPage({ onAuthenticated }: LoginPageProps) {
  const login = useLogin()
  const [alertText, setAlertText] = useState<string | null>(null)
  const {
    register,
    handleSubmit,
    setError,
    setFocus,
    resetField,
    formState: { errors },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    mode: 'onTouched',
    defaultValues: { username: '', password: '' },
  })

  function showFailure(error: unknown) {
    if (!(error instanceof ApiError)) {
      setAlertText(copy.login.network)
      return
    }
    const fieldErrors = error.fieldErrors.filter(({ field }) =>
      FORM_FIELDS.some((name) => name === field),
    )
    if (fieldErrors.length > 0) {
      for (const { field, message } of fieldErrors) {
        setError(field as (typeof FORM_FIELDS)[number], { message })
      }
      return
    }
    if (error.code === 'invalid_credentials') {
      setAlertText(error.message)
      resetField('password')
      setFocus('password')
      return
    }
    if (error.code === 'too_many_attempts' && error.retryAfterSeconds) {
      setAlertText(copy.login.tooManyAttempts(Math.ceil(error.retryAfterSeconds / 60)))
      return
    }
    setAlertText(error.message)
  }

  const onSubmit = handleSubmit((values) => {
    setAlertText(null)
    login.mutate(values, { onSuccess: onAuthenticated, onError: showFailure })
  })

  return (
    <main className="flex min-h-dvh items-center justify-center bg-canvas px-4 py-10">
      <div className="grid w-full max-w-[67rem] items-center justify-center gap-8 lg:grid-cols-[25rem_27.5rem] lg:gap-48">
        <div className="relative mx-auto flex w-full max-w-100 justify-center lg:h-[35.2rem]">
          <img
            src="/brand/ornamentos/arco-duplo.svg"
            alt=""
            className="absolute inset-0 hidden size-full lg:block"
          />
          <img
            src="/brand/logo/altare-vertical-oliva.svg"
            alt={copy.login.brandAlt}
            className="relative w-24 lg:absolute lg:top-[53%] lg:left-1/2 lg:w-48 lg:-translate-x-1/2 lg:-translate-y-1/2"
          />
          <img
            src="/brand/ornamentos/ramo-pequeno.svg"
            alt=""
            className="absolute bottom-2 left-1/2 hidden w-40 -translate-x-1/2 lg:block"
          />
        </div>

        <Card className="mx-auto w-full max-w-[27.5rem] p-10 max-md:p-6">
          <h1 tabIndex={-1} className="text-title text-ink">
            {copy.login.title}
          </h1>
          <p className="mt-1 text-body text-ink-muted">{copy.login.subtitle}</p>

          <form onSubmit={onSubmit} noValidate className="mt-8 flex flex-col">
            <div className="flex flex-col gap-5">
              <Input
                label={copy.login.usernameLabel}
                placeholder={copy.login.usernamePlaceholder}
                autoComplete="username"
                autoCapitalize="none"
                spellCheck={false}
                aria-required="true"
                error={errors.username?.message}
                {...register('username')}
              />
              <Input
                label={copy.login.passwordLabel}
                type="password"
                autoComplete="current-password"
                aria-required="true"
                error={errors.password?.message}
                {...register('password')}
              />
            </div>

            {/* A região existe vazia desde o início: um aviso que nasce já pronto não é anunciado. */}
            <div role="alert">
              {alertText && (
                <p className="mt-5 flex items-start gap-2 rounded-control bg-attention-bg px-3 py-2.5 text-body-sm text-attention-ink">
                  <CircleAlert aria-hidden className="mt-0.5 size-4 shrink-0" />
                  {alertText}
                </p>
              )}
            </div>

            <Button type="submit" size="lg" loading={login.isPending} className="mt-6 w-full">
              {copy.login.submit}
            </Button>
          </form>

          <p className="mt-4 text-center text-ui-sm text-ink-muted">{copy.login.note}</p>
        </Card>
      </div>
    </main>
  )
}
