from app.domains import registry


def test_all_domains_registered():
    domains = registry.get_domain_names()
    expected = ["code_dev", "copywriting", "data_analysis", "marketing",
                "healthcare", "legal", "education", "ai_visual"]
    for d in expected:
        assert d in domains, f"{d} should be registered"


def test_each_domain_has_template():
    for domain in registry.get_domain_names():
        strategy = registry.get(domain)
        assert strategy.template, f"{domain} missing template"
        assert strategy.role_instruction, f"{domain} missing role_instruction"
        assert strategy.rules, f"{domain} missing rules"
        assert strategy.scoring_weights, f"{domain} missing scoring_weights"


def test_scoring_weights_sum():
    for domain in registry.get_domain_names():
        strategy = registry.get(domain)
        total = sum(strategy.scoring_weights.values())
        assert abs(total - 1.0) < 0.05, f"{domain} weights sum to {total}, expected ~1.0"
