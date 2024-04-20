from ..commons.db_storage.models import SearchSetting
from .abstract_phishing_domain_checker import AbstractPhishingDomainChecker
from .fuzzing_phishing_domain_checker import FuzzingPhishingDomainChecker
from .levensh_fuzz_phishing_domain_checker import LevenshFuzzPhishingDomainChecker
from .levenshtein_phishing_domain_checker import LevenshteinPhishingDomainChecker
from .simple_phishing_domain_checker import SimplePhishingDomainChecker


def phishing_domain_checker_factory(algorithm: str, settings: list[SearchSetting]) -> AbstractPhishingDomainChecker:
    if algorithm == "simple":
        return SimplePhishingDomainChecker(settings=settings)
    elif algorithm == "levenshtein":  # noqa: RET505
        return LevenshteinPhishingDomainChecker(settings=settings)
    elif algorithm == "fuzzing":
        return FuzzingPhishingDomainChecker(settings=settings)
    elif algorithm == "levensh-fuzz":
        return LevenshFuzzPhishingDomainChecker(settings=settings)
    else:
        raise ValueError(f"Unknown algorithm {algorithm}")
