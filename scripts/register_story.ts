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
  
  // Use the correct client method
  const response = await client.registerIP({
    metadata: ip_metadata,
    nftMetadata: nft_metadata
  });
  
  return {
    explorerUrl: response.explorerUrl,
    txHash: response.txHash,
    ipId: response.ipId
  };
}