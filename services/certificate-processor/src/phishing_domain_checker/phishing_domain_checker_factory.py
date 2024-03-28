from .abstract_phishing_domain_checker import AbstractPhishingDomainChecker
from .simple_phishing_domain_checker import SimplePhishingDomainChecker


def phishing_domain_checker_factory(algorithm: str, settings: dict) -> AbstractPhishingDomainChecker:
    if algorithm == "simple":
        return SimplePhishingDomainChecker(settings=settings)
    elif algorithm == "hamming_weight":  # noqa: RET505
        raise NotImplementedError("Hamming weight algorithm not implemented yet")
    elif algorithm == "scrambling":
        raise NotImplementedError("Scrambling algorithm not implemented yet")
    elif algorithm == "fuzzy_hashing":
        raise NotImplementedError("Fuzzy hashing algorithm not implemented yet")
    else:
        raise ValueError(f"Unknown algorithm {algorithm}")
