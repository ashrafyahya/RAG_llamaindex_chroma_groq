/**
 * Main Chat Page Component
 * Container for the entire RAG application
 */
import React, { useState, useEffect } from 'react';
import {
  IonPage,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButton,
  IonIcon,
  IonButtons,
} from '@ionic/react';
import { settingsOutline } from 'ionicons/icons';
import ChatInterface from '../components/ChatInterface';
import DocumentManagement from '../components/DocumentManagement';
import APISettings from '../components/APISettings';
import { Message, APIKeys, Provider } from '../types';
import apiService from '../services/api';

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [showAPISettings, setShowAPISettings] = useState(false);
  const [showDocuments, setShowDocuments] = useState(false);
  const [apiKeys, setApiKeys] = useState<APIKeys>({
    groq: '',
    openai: '',
    gemini: '',
    deepseek: '',
  });
  const [selectedProvider, setSelectedProvider] = useState<Provider>('groq');

  // Load saved API keys and provider on mount
  useEffect(() => {
    loadSavedSettings();
  }, []);

  const loadSavedSettings = async () => {
    try {
      const providerResponse = await apiService.getSelectedProvider();
      if (providerResponse.provider) {
        setSelectedProvider(providerResponse.provider);
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleSendMessage = async (query: string) => {
    const userMessage: Message = {
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages([...messages, userMessage]);

    try {
      const response = await apiService.queryRAG({
        query,
        api_provider: selectedProvider,
        api_key_groq: apiKeys.groq,
        api_key_openai: apiKeys.openai,
        api_key_gemini: apiKeys.gemini,
        api_key_deepseek: apiKeys.deepseek,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages([...messages, userMessage, assistantMessage]);
    } catch (error: any) {
      const errorMessage: Message = {
        role: 'assistant',
        content: `Error: ${error.response?.data?.detail || 'Failed to get response'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages([...messages, userMessage, errorMessage]);
    }
  };

  const handleClearChat = async () => {
    try {
      await apiService.clearChatMemory();
      setMessages([]);
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const handleSaveAPIKeys = async (keys: APIKeys, provider: Provider) => {
    setApiKeys(keys);
    setSelectedProvider(provider);
    
    // Save to backend
    try {
      for (const [providerName, key] of Object.entries(keys)) {
        if (key) {
          await apiService.saveAPIKey(providerName, key);
        }
      }
      await apiService.setSelectedProvider(provider);
    } catch (error) {
      console.error('Error saving API keys:', error);
    }
  };

  return (
    <IonPage>
      <IonHeader>
        <IonToolbar color="primary">
          <IonTitle>🤖 RAG AI Assistant</IonTitle>
          <IonButtons slot="end">
            <IonButton onClick={() => setShowDocuments(!showDocuments)}>
              📁 Documents
            </IonButton>
            <IonButton onClick={() => setShowAPISettings(!showAPISettings)}>
              <IonIcon icon={settingsOutline} />
            </IonButton>
          </IonButtons>
        </IonToolbar>
      </IonHeader>

      <IonContent>
        {showAPISettings ? (
          <APISettings
            apiKeys={apiKeys}
            selectedProvider={selectedProvider}
            onSave={handleSaveAPIKeys}
            onClose={() => setShowAPISettings(false)}
          />
        ) : showDocuments ? (
          <DocumentManagement onClose={() => setShowDocuments(false)} />
        ) : (
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            onClearChat={handleClearChat}
          />
        )}
      </IonContent>
    </IonPage>
  );
};

export default ChatPage;
