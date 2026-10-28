from wedding.shared_kernel.errors import Conflict, DomainRuleViolated


class InvalidBaselineValue(DomainRuleViolated):
    default_code = "invalid_baseline_value"


class BaselineValueRequired(DomainRuleViolated):
    default_code = "baseline_value_required"


class InvalidScopeValue(DomainRuleViolated):
    default_code = "invalid_scope_value"


class DiscardReasonRequired(DomainRuleViolated):
    default_code = "discard_reason_required"


class CatalogItemNotDeletable(DomainRuleViolated):
    default_code = "catalog_item_not_deletable"


class GroupNotEmpty(DomainRuleViolated):
    default_code = "group_not_empty"


class DuplicateScopeName(Conflict):
    default_code = "duplicate_scope_name"
