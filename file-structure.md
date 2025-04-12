# Kairos - The Emergent Reasoning Network

## File Structure
```
.
├── blockchain
│   ├── near
│   ├── rootstock
│   └── saga
├── contracts
│   ├── execution
│   ├── reasoning-path
│   ├── trust-score
│   └── validation-market
├── core
│   ├── knowledge-graph
│   ├── orchestrator
│   └── types
├── data-ingestion
│   ├── file-parser
│   ├── rpc
│   ├── rss
│   └── social
├── eigenlayer-avs
│   ├── contracts
│   └── sdk
├── examples
│   ├── dao-treasury
│   ├── defi-risk-analysis
│   └── scientific-review
├── frontend
│   ├── components
│   ├── hooks
│   ├── plugins
│   └── visualizers
├── gensyn
│   ├── deployment
│   └── training
├── ip-layer
│   ├── contracts
│   └── sdk
├── pin-ai
│   └── preferences
├── reasoning-modules
│   ├── audit
│   ├── base
│   ├── defi
│   ├── macro
│   └── sentiment
├── scripts
├── upstage
│   └── document-parser
└── validation-nodes
    ├── alignment
    ├── base
    ├── grounding
    ├── logical
    └── novelty
```
blockchain: Contains integrations with various blockchain networks.

near: Integration with NEAR Protocol for the AI Agent Network
rootstock: Implementation for executing validated DeFi strategies
saga: Chainlet deployment for Kairos smart contracts


contracts: Smart contracts that manage on-chain components of the system.

execution: Contracts that execute validated strategies
reasoning-path: Manages and records reasoning pathways
trust-score: Records and calculates trust scores
validation-market: Handles staking and rewards for validators


core: Central system components that coordinate the reasoning network.

knowledge-graph: Builds and maintains the decentralized knowledge base
orchestrator: Breaks down queries and routes them to appropriate modules
types: Shared type definitions used across the system


data-ingestion: Components for gathering and processing external data.

file-parser: Processes uploaded documents
rpc: Collects blockchain data via RPC endpoints
rss: Processes news and other RSS feeds
social: Gathers data from social media platforms


eigenlayer-avs: EigenLayer integration for decentralized validation.

contracts: AVS-specific smart contracts
sdk: Tools for integrating with the EigenLayer protocol


examples: Example implementations demonstrating use cases.

dao-treasury: Treasury management use case
defi-risk-analysis: DeFi risk assessment example
scientific-review: Scientific paper review workflow


frontend: User interface components.

components: Reusable UI elements
hooks: Custom React hooks
plugins: Extensions for the UI
visualizers: Tools for visualizing reasoning pathways


gensyn: Tools for distributed model training.

deployment: Manages deployment of trained models
training: Implements reinforcement learning through feedback


ip-layer: Story Protocol integration for intellectual property rights.

contracts: IP registration smart contracts
sdk: Integration with Story Protocol


pin-ai: Personalization and alignment layer.

preferences: Manages user preferences for customized reasoning


reasoning-modules: Specialized AI agents for different reasoning domains.

audit: Smart contract audit reasoning
base: Common code for all reasoning modules
defi: DeFi-specific reasoning
macro: Macroeconomic analysis
sentiment: Social sentiment analysis


scripts: Utility scripts for development and deployment.
upstage: Document processing capabilities.

document-parser: Parses unstructured documents into structured knowledge


validation-nodes: Components for validating reasoning outputs.

alignment: Ensures outputs match user goals
base: Common code for all validation nodes
grounding: Verifies factual accuracy
logical: Checks reasoning structure and logic
novelty: Assesses originality and usefulness of insights





## Key Component Descriptions

### Core Components

- **Query Orchestrator**: Breaks down user queries into manageable sub-tasks and routes them to appropriate Reasoning Modules.
- **Knowledge Graph**: Stores structured data from various sources including documents, blockchain data, and external APIs.

### Reasoning Modules (RMs)

Specialized AI agents that handle specific types of reasoning:
- **DeFi RM**: Analyzes DeFi protocols, risks, and opportunities
- **Sentiment RM**: Processes social media and forum data for sentiment analysis
- **Audit RM**: Evaluates smart contract security and risk
- **Macro RM**: Analyzes macroeconomic indicators and trends

### Validation Nodes (VNs)

Independent validators that assess different aspects of reasoning:
- **Logical VNs**: Check for logical fallacies and inference structure
- **Grounding VNs**: Validate data claims against sources
- **Alignment VNs**: Ensure outputs align with user constraints and goals
- **Novelty VNs**: Assess originality and usefulness of insights

### Integration Components

- **EigenLayer AVS**: Coordinates validation, staking, and trust scoring
- **Blockchain (Rootstock/Saga/NEAR)**: Manages on-chain execution and smart contracts
- **IP Layer (Story Protocol)**: Handles registration and licensing of reasoning flows
- **Gensyn Swarm**: Facilitates distributed learning and model improvement
- **PIN AI**: Manages personalization and alignment with user preferences
- **Upstage API**: Parses unstructured documents into structured knowledge