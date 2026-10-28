import { z } from 'zod'
import { copy } from '../copy'

// Só exige o preenchimento: a regra de usuário e de senha vale na criação da conta, e mostrá-la
// aqui diria a quem erra o que uma conta pode ter.
export const loginSchema = z.object({
  username: z.string().trim().min(1, copy.login.usernameRequired),
  password: z.string().min(1, copy.login.passwordRequired),
})

export type LoginValues = z.infer<typeof loginSchema>
