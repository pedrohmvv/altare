from collections.abc import Callable

from fastapi import Request

from wedding.platform.http.constants import SESSION_COOKIE
from wedding.shared_kernel.actor import Actor
from wedding.shared_kernel.errors import Unauthenticated

# O bootstrap injeta o resolvedor: o platform não conhece o módulo de identidade.
ActorResolver = Callable[[str], Actor | None]


def current_actor(request: Request) -> Actor:
    """Quem age, montado do cookie da sessão. A autoria nunca vem do corpo do pedido."""
    token = request.cookies.get(SESSION_COOKIE)
    resolver: ActorResolver | None = request.app.state.actor_resolver
    actor = resolver(token) if token and resolver else None
    if actor is None:
        raise Unauthenticated()
    return actor
