import pandas as pd
import json
from pathlib import Path
from collections import Counter

class LogicEngine:
    def __init__(self, csv_path: Path):
        self.csv_path = csv_path
        self.df = self._load_data()

    def _load_data(self):
        try:
            return pd.read_csv(self.csv_path)
        except Exception as e:
            print(f"[!] LogicEngine Error: {e}")
            return pd.DataFrame()

    def analyze_infrastructure(self):
        if self.df.empty:
            return {"status": "error", "message": "No data found in registry."}

        total_targets = len(self.df)
        
        # Build global analytical components
        global_analysis = {
            "discovered_services": self._correlate_services(),
            "defense_landscape": self._correlate_defenses(),
            "infrastructure_clusters": self._identify_clusters()
        }

        # Generate the final handoff structure including per-target maturity
        return self._generate_handoff(global_analysis)

    def _correlate_services(self):
        if 'Services' not in self.df.columns: 
            return {"top_services": {}, "unique_service_count": 0}
        
        # Clean data: Remove TBDs and split multi-service strings (e.g., "ssh|http")
        all_services = []
        for s in self.df['Services'].dropna():
            if s != "TBD":
                all_services.extend(str(s).split('|'))
        
        service_counts = Counter(all_services)
        return {
            "top_services": dict(service_counts.most_common(5)),
            "unique_service_count": len(service_counts)
        }

    def _correlate_defenses(self):
        """Detects WAF/Edge protection based on OS_Tech and Services columns."""
        raw_signals = []
        for _, row in self.df.iterrows():
            # Check both columns for edge indicators
            tech = str(row.get("OS_Tech", "")).lower()
            svc = str(row.get("Services", "")).lower()
            raw_signals.extend([tech, svc])

        edge_vendors = ["cloudflare", "akamai", "fastly", "incapsula", "cf-ray"]
        matched_vendors = [v for v in edge_vendors if any(v in s for s in raw_signals)]

        defense_data = {
            "defensive_density": "0.0%",
            "detected_vendors": [],
            "is_edge_protected": False,
            "interpretation_hint": "standard_visibility"
        }

        if matched_vendors:
            vendors = sorted({v.capitalize() for v in matched_vendors if v != "cf-ray"})
            defense_data.update({
                "defensive_density": "HIGH (Edge-Based)",
                "detected_vendors": vendors,
                "is_edge_protected": True,
                "interpretation_hint": "edge_abstraction"
            })

        return defense_data

    def _identify_clusters(self):
        if 'Open_Ports' not in self.df.columns: return {}
        valid_ports = self.df[self.df['Open_Ports'].notna() & (self.df['Open_Ports'] != "TBD")]
        return valid_ports.groupby('Open_Ports').size().to_dict()

    def calculate_maturity_score(self, target_row, is_edge_protected):
        score = 0
        findings = []

        # 1. Edge Protection (+40)
        if is_edge_protected:
            score += 40
            findings.append("Edge/WAF Abstraction Active")

        # 2. Port Exposure Analysis
        ports_raw = str(target_row.get('Open_Ports', '')).replace('|', ',').split(',')
        open_ports = [p.strip() for p in ports_raw if p.strip() and p.strip() != "TBD" and p.strip() != "FILTERED"]
        
        if 0 < len(open_ports) <= 2:
            score += 30
            findings.append("Hardened Service Footprint (Low Exposure)")
        elif len(open_ports) > 5:
            score -= 20
            findings.append("High Service Density Risk (Excessive Exposure)")

        # 3. Version Leakage Check
        tech_info = str(target_row.get('OS_Tech', '')).lower()
        if any(v in tech_info for v in ["ubuntu", "debian", "apache/2.4", "nginx/1."]):
            score -= 10
            findings.append("Verbose Version Leakage Detected")

        return max(0, min(100, score)), findings

    def _generate_handoff(self, global_analysis):
        target_mapping = []
        is_edge = global_analysis['defense_landscape']['is_edge_protected']

        for _, row in self.df.iterrows():
            os_info = row.get('OS_Tech', 'TBD')
            # Intelligent label for hidden OS
            if os_info == "TBD" and is_edge:
                os_info = "INTENTIONALLY_MASKED_BY_EDGE"

            score, findings = self.calculate_maturity_score(row, is_edge)

            target_mapping.append({
                "tid": str(row.get('Target_ID', 'N/A')),
                "target_name": str(row.get('Target_Name', 'N/A')),
                "network_context": {
                    "ip": str(row.get('Input_Value', 'N/A')),
                    "status": str(row.get('Scope_Status', 'TBD'))
                },
                "technical_details": {
                    "os": os_info,
                    "ports": str(row.get('Open_Ports', 'TBD')),
                    "services": str(row.get('Services', 'TBD'))
                },
                "maturity": {
                    "score": score,
                    "findings": findings
                }
            })

        return {
            "metadata": {
                "engine": "VedicRecon LogicEngine v1.0-alpha",
                "total_scope": len(self.df)
            },
            "global_stats": global_analysis,
            "inventory": target_mapping
        }

def run_logic_engine(csv_path: Path, output_json: Path):
    engine = LogicEngine(csv_path)
    analysis = engine.analyze_infrastructure()
    
    with open(output_json, 'w') as f:
        json.dump(analysis, f, indent=4)
    
    return analysis