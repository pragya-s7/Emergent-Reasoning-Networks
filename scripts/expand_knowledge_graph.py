#!/usr/bin/env python3
"""
Expands the minimal 4-entity KG to 50+ entities for proper evaluation.
Creates realistic multi-domain graph with multiple relation types to enable:
- Multi-hop reasoning
- Entity co-activation patterns
- Emergent connection formation
"""

import sys
import os
import random
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.knowledge_graph.knowledgeGraph import KnowledgeGraph


def create_expanded_kg():
    """Create a 50+ entity knowledge graph across security, finance, and governance domains."""
    
    kg = KnowledgeGraph()
    random.seed(42)  # reproducibility
    
    print("Creating expanded knowledge graph...")
    print("Target: 50+ entities, 8-10 relation types, 120+ relations")
    print()
    
    # ========== SECURITY DOMAIN (25 entities) ==========
    print("Adding security domain entities...")
    
    # Smart Contracts (15)
    contracts = [
        "ApolloContract", "ZeusContract", "HermesContract", "AthenaContract", 
        "PoseidonContract", "AresContract", "DionysusContract", "HephaestusContract",
        "DemeterContract", "HeraContract", "AphroditeContract", "ArtemisContract",
        "HadesContract", "HeliosContract", "PerseusContract"
    ]
    
    for contract in contracts:
        kg.add_entity(contract, "SmartContract")
    
    # Vulnerabilities (5)
    vulnerabilities = [
        "Reentrancy", "GasLimitVulnerability", "IntegerOverflow", 
        "AccessControlViolation", "FrontRunning"
    ]
    
    for vuln in vulnerabilities:
        kg.add_entity(vuln, "Vulnerability")
    
    # Audit Firms (5)
    auditors = [
        "ChainGuard", "CertiK", "TrailOfBits", "Quantstamp", "OpenZeppelin"
    ]
    
    for auditor in auditors:
        kg.add_entity(auditor, "AuditFirm")
    
    # ========== FINANCIAL DOMAIN (15 entities) ==========
    print("Adding financial domain entities...")
    
    # Tokens (8)
    tokens = [
        "ETH", "USDC", "USDT", "DAI", "WBTC", "LINK", "UNI", "AAVE"
    ]
    
    for token in tokens:
        kg.add_entity(token, "Token")
    
    # Exchanges/Protocols (5)
    exchanges = [
        "UniswapV3", "Curve", "Balancer", "SushiSwap", "PancakeSwap"
    ]
    
    for exchange in exchanges:
        kg.add_entity(exchange, "Exchange")
    
    # Liquidity Pools (2)
    pools = ["ETH-USDC-Pool", "DAI-USDT-Pool"]
    for pool in pools:
        kg.add_entity(pool, "LiquidityPool")
    
    # ========== GOVERNANCE DOMAIN (7 entities) ==========
    print("Adding governance domain entities...")
    
    # DAOs (5)
    daos = ["MakerDAO", "CompoundDAO", "AaveDAO", "UniswapDAO", "ENSDAO"]
    
    for dao in daos:
        kg.add_entity(dao, "DAO")
    
    # Voting Systems (2)
    voting_systems = ["SnapshotVoting", "OnChainVoting"]
    for vs in voting_systems:
        kg.add_entity(vs, "VotingSystem")
    
    # ========== NETWORKS (3 entities) ==========
    networks = ["Ethereum", "Polygon", "Arbitrum"]
    for network in networks:
        kg.add_entity(network, "Network")
    
    print(f"Total entities created: {len(kg.entities)}")
    print()
    
    # ========== CREATE RELATIONS ==========
    print("Creating relations...")
    
    # 1. Contract vulnerabilities (assign 1-3 vulnerabilities per contract)
    print("  - Contract vulnerabilities...")
    for contract in contracts[:12]:  # 12 contracts have vulnerabilities
        num_vulns = random.choice([1, 1, 2, 2, 3])  # most have 1-2
        selected_vulns = random.sample(vulnerabilities, num_vulns)
        for vuln in selected_vulns:
            kg.add_relation(
                contract, "has_vulnerability", vuln,
                confidence=random.uniform(0.7, 0.95),
                source="security_scan"
            )
    
    # 2. Contract audits (some contracts audited, some not)
    print("  - Contract audits...")
    for contract in random.sample(contracts, 8):  # only 8 of 15 audited
        auditor = random.choice(auditors)
        kg.add_relation(
            contract, "audited_by", auditor,
            confidence=random.uniform(0.85, 1.0),
            source="audit_report"
        )
    
    # 3. Contract deployments on networks
    print("  - Contract deployments...")
    for contract in contracts:
        network = random.choice(networks)
        kg.add_relation(
            contract, "deployed_on", network,
            confidence=1.0,
            source="blockchain_data"
        )
    
    # 4. Contract dependencies (some contracts depend on others)
    print("  - Contract dependencies...")
    for i in range(10):
        contract_a = random.choice(contracts)
        contract_b = random.choice([c for c in contracts if c != contract_a])
        kg.add_relation(
            contract_a, "depends_on", contract_b,
            confidence=random.uniform(0.8, 1.0),
            source="code_analysis"
        )
    
    # 5. Token trading on exchanges
    print("  - Token trading relationships...")
    for token in tokens:
        # each token trades on 2-4 exchanges
        selected_exchanges = random.sample(exchanges, random.randint(2, 4))
        for exchange in selected_exchanges:
            kg.add_relation(
                token, "trades_on", exchange,
                confidence=1.0,
                source="market_data"
            )
    
    # 6. Liquidity pool connections
    print("  - Liquidity pool relationships...")
    kg.add_relation("ETH-USDC-Pool", "contains_token", "ETH", confidence=1.0, source="pool_data")
    kg.add_relation("ETH-USDC-Pool", "contains_token", "USDC", confidence=1.0, source="pool_data")
    kg.add_relation("DAI-USDT-Pool", "contains_token", "DAI", confidence=1.0, source="pool_data")
    kg.add_relation("DAI-USDT-Pool", "contains_token", "USDT", confidence=1.0, source="pool_data")
    
    kg.add_relation("ETH-USDC-Pool", "hosted_on", "UniswapV3", confidence=1.0, source="pool_data")
    kg.add_relation("DAI-USDT-Pool", "hosted_on", "Curve", confidence=1.0, source="pool_data")
    
    # 7. DAO governance relationships
    print("  - DAO governance...")
    kg.add_relation("MakerDAO", "governs_token", "DAI", confidence=1.0, source="governance_docs")
    kg.add_relation("CompoundDAO", "uses_voting", "SnapshotVoting", confidence=1.0, source="governance_docs")
    kg.add_relation("AaveDAO", "uses_voting", "OnChainVoting", confidence=1.0, source="governance_docs")
    kg.add_relation("UniswapDAO", "governs_protocol", "UniswapV3", confidence=1.0, source="governance_docs")
    
    # 8. Security-Finance crossover (key for emergent connections!)
    print("  - Cross-domain connections...")
    kg.add_relation("ApolloContract", "provides_liquidity_to", "ETH-USDC-Pool", 
                   confidence=0.9, source="defi_analysis")
    kg.add_relation("ZeusContract", "provides_liquidity_to", "DAI-USDT-Pool",
                   confidence=0.85, source="defi_analysis")
    kg.add_relation("HermesContract", "integrates_with", "UniswapV3",
                   confidence=0.9, source="integration_docs")
    kg.add_relation("AthenaContract", "integrates_with", "Curve",
                   confidence=0.88, source="integration_docs")
    
    # 9. High-risk entities (for co-activation patterns)
    print("  - Risk assessments...")
    high_risk_contracts = ["ApolloContract", "HadesContract", "AresContract"]
    for contract in high_risk_contracts:
        kg.add_relation(contract, "has_risk_level", "High",
                       confidence=0.8, source="risk_assessment")
    
    # Add High as entity
    kg.add_entity("High", "RiskLevel")
    kg.add_entity("Medium", "RiskLevel")
    kg.add_entity("Low", "RiskLevel")
    
    print(f"Total relations created: {len(kg.relations)}")
    print()
    
    # ========== STATISTICS ==========
    print("="*60)
    print("KNOWLEDGE GRAPH STATISTICS")
    print("="*60)
    print(f"Total Entities: {len(kg.entities)}")
    print(f"Total Relations: {len(kg.relations)}")
    
    # Count relation types
    relation_types = {}
    for rel in kg.relations:
        relation_types[rel.predicate] = relation_types.get(rel.predicate, 0) + 1
    
    print(f"Unique Relation Types: {len(relation_types)}")
    print("\nRelation Type Distribution:")
    for rel_type, count in sorted(relation_types.items(), key=lambda x: -x[1]):
        print(f"  {rel_type}: {count}")
    
    # Entity type distribution
    entity_types = {}
    for entity in kg.entities.values():
        entity_types[entity.type] = entity_types.get(entity.type, 0) + 1
    
    print(f"\nEntity Type Distribution:")
    for ent_type, count in sorted(entity_types.items(), key=lambda x: -x[1]):
        print(f"  {ent_type}: {count}")
    
    print("="*60)
    
    return kg


def main():
    """Create and save expanded knowledge graph."""
    
    kg = create_expanded_kg()
    
    # Save to output directory
    output_path = "output/knowledge_graph.json"
    backup_path = "output/knowledge_graph_backup_minimal.json"
    
    # Backup old KG if it exists
    if os.path.exists(output_path):
        print(f"\nBacking up existing KG to: {backup_path}")
        os.makedirs("output", exist_ok=True)
        with open(output_path, 'r') as f:
            old_kg = json.load(f)
        with open(backup_path, 'w') as f:
            json.dump(old_kg, f, indent=2)
    
    # Save new KG
    print(f"\nSaving expanded KG to: {output_path}")
    os.makedirs("output", exist_ok=True)
    kg.save_to_json(output_path)
    
    print("\n✅ Knowledge graph expansion complete!")
    print(f"✅ Backed up original to: {backup_path}")
    print(f"✅ New KG saved to: {output_path}")
    print("\nYou can now run evaluations with the expanded knowledge graph.")


if __name__ == "__main__":
    main()

