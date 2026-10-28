// Prepara um banco temporário (migrações e os dois usuários de exemplo) e sobe a API do E2E.
import { spawn, spawnSync } from 'node:child_process'
import { mkdirSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import credentials from './credentials.json' with { type: 'json' }

const port = process.env.E2E_API_PORT ?? '8105'
const dir = join(tmpdir(), `altare-e2e-${port}`)
const apiDir = join(import.meta.dirname, '..', '..', 'api')

// Banco novo a cada execução: o E2E nunca enxerga o que uma execução anterior deixou.
rmSync(dir, { recursive: true, force: true })
mkdirSync(dir, { recursive: true })

const env = {
  ...process.env,
  DATABASE_URL: `sqlite:///${dir}/altare.db`,
  FILES_DIR: join(dir, 'files'),
  // O E2E roda em http://127.0.0.1, onde o navegador recusa um cookie `Secure`.
  SESSION_COOKIE_SECURE: 'false',
}

function run(args, input) {
  const result = spawnSync('uv', ['run', ...args], {
    cwd: apiDir,
    env,
    input,
    stdio: ['pipe', 'inherit', 'inherit'],
  })
  if (result.status !== 0) process.exit(result.status ?? 1)
}

run(['alembic', 'upgrade', 'head'])
for (const { username, profile } of [credentials.noivo, credentials.noiva]) {
  const password = `${credentials.password}\n${credentials.password}\n`
  run(['wedding', 'create-user', '--profile', profile, '--username', username], password)
}

const server = spawn(
  'uv',
  [
    'run',
    'uvicorn',
    'wedding.main:app',
    '--host',
    '127.0.0.1',
    '--port',
    port,
    '--log-level',
    'warning',
  ],
  { cwd: apiDir, env, stdio: 'inherit' },
)
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => server.kill(signal))
server.on('exit', (code) => process.exit(code ?? 0))
