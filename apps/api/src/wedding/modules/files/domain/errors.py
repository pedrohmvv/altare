from wedding.shared_kernel.errors import DomainRuleViolated


class UnsupportedFileType(DomainRuleViolated):
    default_code = "unsupported_file_type"


class FileTooLarge(DomainRuleViolated):
    default_code = "file_too_large"


class EmptyFile(DomainRuleViolated):
    default_code = "empty_file"
