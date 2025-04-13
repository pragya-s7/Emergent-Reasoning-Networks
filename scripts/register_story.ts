import { client } from './utils';

interface IPMetadata {
  conclusion?: string;
  [key: string]: any;
}

interface NFTMetadata {
  name: string;
  description: string;
  [key: string]: any;
}

interface RegisterIPParams {
  ip_metadata: IPMetadata;
  nft_metadata: NFTMetadata;
}

export async function registerIP(params: RegisterIPParams) {
  const { ip_metadata, nft_metadata } = params;

  // Add trust score and validation metadata
  const fullMetadata = {
    ...ip_metadata,
    trust_score: ip_metadata.trust_score,
    validation_results: ip_metadata.validation_results,
    licensing_terms: "CC-BY", // or other
  };

  const response = await client.registerIP({
    metadata: fullMetadata,
    nftMetadata: nft_metadata
  });

  return {
    explorerUrl: response.explorerUrl,
    txHash: response.txHash,
    ipId: response.ipId
  };
}
