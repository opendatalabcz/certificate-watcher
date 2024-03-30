from .abstract_phishing_domain_checker import AbstractPhishingDomainChecker
from .levenshtein_phishing_domain_checker import LevenshteinPhishingDomainChecker
from .simple_phishing_domain_checker import SimplePhishingDomainChecker


def phishing_domain_checker_factory(algorithm: str, settings: dict) -> AbstractPhishingDomainChecker:
    if algorithm == "simple":
        return SimplePhishingDomainChecker(settings=settings)
    elif algorithm == "levenshtein":  # noqa: RET505
        return LevenshteinPhishingDomainChecker(settings=settings)
    elif algorithm == "scrambling":
        raise NotImplementedError("Scrambling algorithm not implemented yet")
    elif algorithm == "fuzzy_hashing":
        raise NotImplementedError("Fuzzy hashing algorithm not implemented yet")
    else:
        raise ValueError(f"Unknown algorithm {algorithm}")
