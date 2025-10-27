import '../styles/globals.css';
import type { AppProps } from 'next/app';
import Head from 'next/head';

export default function App({ Component, pageProps }: AppProps) {
  return (
    <>
      <Head>
        <link href="https://cdn.jsdelivr.net/npm/reactflow@11.1.0/dist/style.css" rel="stylesheet" />
      </Head>
      <Component {...pageProps} />
    </>
  );
}