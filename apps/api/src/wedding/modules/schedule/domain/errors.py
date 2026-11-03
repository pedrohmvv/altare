from wedding.shared_kernel.errors import DomainRuleViolated


class InvalidScheduleValue(DomainRuleViolated):
    default_code = "invalid_schedule_value"


class MilestoneBlocked(DomainRuleViolated):
    default_code = "milestone_blocked"
