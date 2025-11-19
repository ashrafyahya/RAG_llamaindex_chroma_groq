/**
 * Chat Interface Component
 * Displays messages and input for chatting with the RAG system
 */
import React, { useState, useRef, useEffect } from 'react';
import {
  IonInput,
  IonButton,
  IonCard,
  IonCardContent,
  IonIcon,
  IonSpinner,
} from '@ionic/react';
import { sendOutline, trashOutline } from 'ionicons/icons';
import { Message } from '../types';
import './ChatInterface.css';

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (query: string) => Promise<void>;
  onClearChat: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  onClearChat,
}) => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() && !isLoading) {
      setIsLoading(true);
      try {
        await onSendMessage(input);
        setInput('');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Chat with the Assistant</h2>
        <div className="chat-actions">
          {messages.length > 0 && (
            <>
              <IonButton size="small" fill="outline" onClick={onClearChat}>
                <IonIcon icon={trashOutline} slot="start" />
                Clear Chat
              </IonButton>
            </>
          )}
        </div>
      </div>

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <h3>Welcome to RAG AI Assistant! 👋</h3>
            <p>Upload documents using the Documents button and start asking questions.</p>
          </div>
        ) : (
          <>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-wrapper ${message.role}`}
              >
                <div className="message-icon">
                  {message.role === 'user' ? '👤' : '🤖'}
                </div>
                <IonCard className={`message-card ${message.role}`}>
                  <IonCardContent>
                    <div className="message-content">{message.content}</div>
                    <div className="message-footer">
                      <span className="message-time">{message.timestamp}</span>
                      <IonButton
                        size="small"
                        fill="clear"
                        onClick={() => copyToClipboard(message.content)}
                      >
                        📋
                      </IonButton>
                    </div>
                  </IonCardContent>
                </IonCard>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="input-container">
        <IonInput
          value={input}
          placeholder="Type your message here..."
          onIonInput={(e) => setInput(e.detail.value || '')}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          className="chat-input"
        />
        <IonButton
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          color="primary"
        >
          {isLoading ? <IonSpinner name="crescent" /> : <IonIcon icon={sendOutline} />}
        </IonButton>
      </div>
    </div>
  );
};

export default ChatInterface;
