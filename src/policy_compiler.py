from datetime import datetime
class PolicyCompiler:
    """
    Compiles ai_profile.json + engine signals into a deterministic system prompt.
    v1.1-Beta: Hardened for Observability-focused black-box auditing.
    """

    def __init__(self, config: dict):
        self.config = config

    # def _compile_tone(self, vms_score: int) -> str:
    #     metrics = self.config.get("strategic_metrics", {})
    #     if not metrics.get("tone_binding", True):
    #         return "Neutral advisory tone."

    #     if vms_score >= 80:
    #         return "Defensive Excellence — focus on micro-optimizations."
    #     elif vms_score >= 50:
    #         return "Developing Posture — highlight missing hardening."
    #     return "Critical Exposure — demand foundational remediation for the infrastructure."
    def _compile_tone(self, vms_score: int, edge_opacity: str = "low") -> str:
        """
        Determines narrative tone based on maturity score and edge opacity.
        edge_opacity: 'low' | 'medium' | 'high'
        """
        metrics = self.config.get("strategic_metrics", {})
        if not metrics.get("tone_binding", True):
            return "Neutral advisory tone."

        #  NEW: Opaque / Ghosted Edge Handling
        if edge_opacity == "high":
            return (
                "Opaque Edge Posture — security controls appear intentionally non-attributable. "
                "Focus on limits of external verification rather than assumed weakness."
            )

        # Standard maturity-based tone
        if vms_score >= 80:
            return "Defensive Excellence — focus on micro-optimizations."
        elif vms_score >= 50:
            return "Developing Posture — highlight missing hardening."
        else:
            return "Critical Exposure — demand foundational remediation for the infrastructure."


    def _compile_recommendation_limit(self, vms_score: int) -> int:
        policy = self.config.get("recommendation_policy", {})
        if vms_score >= 80:
            return policy.get("max_if_high_maturity", 1)
        elif vms_score >= 50:
            return policy.get("max_if_medium_maturity", 3)
        return policy.get("max_if_low_maturity", 5)

    def _compile_constraints(self) -> str:
        constraints = self.config.get("ai_constraints", {})
        return "\n".join(
            f"- {k.replace('_', ' ').upper()}: {v}"
            for k, v in constraints.items()
        )

    def _compile_evidence_policy(self) -> str:
        evidence = self.config.get("evidence_policy", {})
        levels = ", ".join(evidence.get("allowed_levels", []))
        manual = evidence.get("require_manual_validation_notice", False)
        return (
            f"- Allowed Evidence Levels: {levels}\n"
            f"- Manual Validation Required: {manual}"
        )

    def compile_prompt(self, profile_data: dict, vms_score: int, node_count: int = 1,edge_opacity: str = "low") -> str:
        """
        Injects semantic guardrails to prevent 'over-assertion' on opaque targets.
        """
        tone = self._compile_tone(vms_score, edge_opacity=edge_opacity)
        report_date=datetime.now().strftime("%B %d, %Y")
        
        # MANDATORY: Observability Guardrails (The Butterfly Fix )
        # This prevents the AI from saying "There is no WAF" and forces "No WAF observed"
        semantic_calibration = (
            "\n[!] SEMANTIC GUARDRAIL (CRITICAL):\n"
            "- Do NOT claim a defense is 'absent', 'missing', or 'not present' unless verified by explicit error responses.\n"
            "- DO NOT use phrases such as 'No Edge Protection', 'Zero Defensive Density', or 'Lack of Security Controls'.\n"
            "- USE: 'No observable edge abstraction detected from external posture'.\n"
            "- USE: 'Internal defensive density not verifiable from black-box observation'.\n"
            "- DO NOT name or attribute any vendor, CDN, cloud provider, or security product "
            "unless its name appears verbatim in the raw scan evidence.\n"
            "- USE: 'Opaque / non-attributable edge behavior' instead of naming providers.\n"
            "- FRAME all attack discussion strictly as a 'Potential Attack Hypothesis'.\n"
            "- If a service name is derived solely from port heuristics and not banner confirmation, "
            "explicitly label it as 'Unverified Service Attribution'.\n"
            "- Do NOT assume protocol semantics or historical use cases."
        )


        meltdown_protocol = (
            f"\n[!] ALERT: VMS SCORE IS CRITICAL ({vms_score}/100).\n"
            "Explain that the score reflects a state where critical services are externally "
            "reachable without observable defensive abstraction."
        ) if vms_score <= 15 else ""

        context_instruction = (
            "AUDIT MODE: SURGICAL (Single Node). Provide technical density and an attacker's POV." 
            if node_count == 1 else 
            f"AUDIT MODE: FLEET-WIDE ({node_count} Nodes). Focus on systemic risk patterns."
        )

        return (
            #dynamic header injection
            f"# Strategic Security Report: {report_date}\n"
            f"## Subject: Foundational Infrastructure Remediation for Directly Exposed Services\n\n"
            f"ROLE: {profile_data['role']}\n"
            f"FOCUS: {profile_data['focus']}\n"
            f"CONTEXT: {context_instruction}{meltdown_protocol}{semantic_calibration}\n"
            f"FORMAT: {profile_data['format']}\n\n"

            "REQUIRED SECTIONS:\n"
            "1. OBSERVABILITY SUMMARY: List what can and cannot be verified from an external posture.\n"
            "2. SCORING RATIONALE: Detail deductions based on non-observable protective controls.\n"
            "3. POTENTIAL ATTACK HYPOTHESIS: Clinical narrative of reachability-based compromise.\n\n"

            "GOVERNANCE CONSTRAINTS:\n"
            f"{self._compile_constraints()}\n\n"

            f"STRATEGIC CONTEXT: {tone}\n"
            f"INFRASTRUCTURE MATURITY SCORE: {vms_score}/100\n\n"

            "TABLE FORMATTING RULES:\n"
            "1. Every Markdown table row MUST end with '|'.\n"
            "2. Columns: | Port | Service | Risk Class | Observability Note |\n"
            "3. If a service is 'tcpwrapped', note it as 'Obscured/Non-Attributable'.\n"
            "4. Fleet-Wide Exposure Summary tables MUST be populated ONLY using "
            "explicit fleet_exposure data provided in the analysis context.\n"
            "5. If no fleet_exposure data is present, the table MUST NOT be populated.\n"
            "6. DO NOT infer, guess, or synthesize table rows.\n\n"


            "BETA DISCLAIMER:\n"
            "Include this at the end: 'Assessments reflect externally observable posture only. "
            "Defensive controls that intentionally obscure their presence (e.g., Enterprise CDNs) "
            "may result in conservative scoring indicating non-observability rather than absence.'\n"
        )