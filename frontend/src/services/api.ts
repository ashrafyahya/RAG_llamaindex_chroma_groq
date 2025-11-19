/**
 * API Service for RAG System Backend
 * Handles all HTTP requests to the FastAPI backend
 */
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Document management
  async uploadDocument(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async listDocuments() {
    const response = await this.client.get('/api/documents');
    return response.data;
  }

  async deleteDocument(docId: string) {
    const response = await this.client.delete(`/api/documents/${docId}`);
    return response.data;
  }

  async clearAllDocuments() {
    const response = await this.client.delete('/api/documents/clear/all');
    return response.data;
  }

  // Chat functionality
  async queryRAG(params: {
    query: string;
    n_results?: number;
    api_provider: string;
    api_key_groq?: string;
    api_key_openai?: string;
    api_key_gemini?: string;
    api_key_deepseek?: string;
  }) {
    const response = await this.client.post('/api/chat/query', params);
    return response.data;
  }

  async clearChatMemory() {
    const response = await this.client.post('/api/chat/clear');
    return response.data;
  }

  // API Key management
  async saveAPIKey(provider: string, apiKey: string) {
    const response = await this.client.post('/api/keys/save', {
      provider,
      api_key: apiKey,
    });
    return response.data;
  }

  async checkAPIKey(provider: string) {
    const response = await this.client.get(`/api/keys/${provider}`);
    return response.data;
  }

  async setSelectedProvider(provider: string) {
    const response = await this.client.post('/api/keys/provider/set', {
      provider,
    });
    return response.data;
  }

  async getSelectedProvider() {
    const response = await this.client.get('/api/keys/provider/get');
    return response.data;
  }
}

const apiService = new APIService();
export default apiService;
