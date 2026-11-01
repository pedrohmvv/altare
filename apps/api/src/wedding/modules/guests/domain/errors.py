from wedding.shared_kernel.errors import Conflict, DomainRuleViolated


class InvalidGuestValue(DomainRuleViolated):
    default_code = "invalid_guest_value"


class GuestNameRequired(DomainRuleViolated):
    default_code = "guest_name_required"


class InvalidPhone(DomainRuleViolated):
    default_code = "invalid_phone"


class InvalidEmail(DomainRuleViolated):
    default_code = "invalid_email"


class DuplicateHouseholdName(Conflict):
    default_code = "duplicate_household_name"


class LastGuestInHousehold(DomainRuleViolated):
    default_code = "last_guest_in_household"


class CompanionAlreadyExists(DomainRuleViolated):
    default_code = "companion_already_exists"


class CompanionCannotHaveCompanion(DomainRuleViolated):
    default_code = "companion_cannot_have_companion"


class CompanionMovesWithHolder(DomainRuleViolated):
    default_code = "companion_moves_with_holder"


class CompanionNeedsName(DomainRuleViolated):
    default_code = "companion_needs_name"


class CompanionChoiceRequired(DomainRuleViolated):
    default_code = "companion_choice_required"
