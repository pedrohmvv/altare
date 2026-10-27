from wedding.shared_kernel.errors import Conflict, DomainRuleViolated, Unauthenticated


class InvalidCredentials(Unauthenticated):
    default_code = "invalid_credentials"


class InvalidUsername(DomainRuleViolated):
    default_code = "invalid_username"


class WeakPassword(DomainRuleViolated):
    default_code = "weak_password"


class DuplicateUsername(Conflict):
    default_code = "duplicate_username"


class ProfileTaken(Conflict):
    default_code = "profile_taken"
