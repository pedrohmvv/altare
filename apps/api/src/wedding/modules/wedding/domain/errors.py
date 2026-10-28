from wedding.shared_kernel.errors import DomainRuleViolated


class InvalidBaselineValue(DomainRuleViolated):
    default_code = "invalid_baseline_value"


class BaselineValueRequired(DomainRuleViolated):
    default_code = "baseline_value_required"
