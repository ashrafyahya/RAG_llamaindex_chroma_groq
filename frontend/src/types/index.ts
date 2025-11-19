/**
 * TypeScript type definitions for the RAG system
 */

export interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface Document {
  name: string;
  ids: string[];
}

export interface APIKeys {
  groq: string;
  openai: string;
  gemini: string;
  deepseek: string;
}

export type Provider = 'groq' | 'openai' | 'gemini' | 'deepseek';

export interface ProviderConfig {
  name: string;
  url: string;
}

export const PROVIDERS: Record<Provider, ProviderConfig> = {
  groq: {
    name: 'Groq',
    url: 'https://console.groq.com',
  },
  openai: {
    name: 'OpenAI',
    url: 'https://platform.openai.com/api-keys',
  },
  gemini: {
    name: 'Gemini',
    url: 'https://ai.google.dev',
  },
  deepseek: {
    name: 'Deepseek',
    url: 'https://platform.deepseek.com',
  },
};
