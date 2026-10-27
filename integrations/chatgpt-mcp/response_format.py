"""Return-format adapter. No stochastic engine calls, no mutation of cast facts."""
from policy_adapter import selected_policy, selected_policy_reference


def method_policy_output(outcome: dict, include_policy_excerpts: bool = True) -> dict:
    """Attach policy material without altering the original cast envelope."""
    method = outcome.get("selected_method")
    if method not in {"tarot", "meihua", "liuyao"}:
        return outcome
    policy = (selected_policy(method) if include_policy_excerpts
              else selected_policy_reference(method))
    return {**outcome, "method_policy": policy}
