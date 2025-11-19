/**
 * API Settings Component
 * Manages API key configuration for different LLM providers
 */
import React, { useState } from 'react';
import {
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonIcon,
  IonInput,
  IonItem,
  IonLabel,
  IonSegment,
  IonSegmentButton,
  IonText,
} from '@ionic/react';
import { closeOutline, saveOutline } from 'ionicons/icons';
import { APIKeys, Provider, PROVIDERS } from '../types';
import './APISettings.css';

interface APISettingsProps {
  apiKeys: APIKeys;
  selectedProvider: Provider;
  onSave: (keys: APIKeys, provider: Provider) => void;
  onClose: () => void;
}

const APISettings: React.FC<APISettingsProps> = ({
  apiKeys,
  selectedProvider,
  onSave,
  onClose,
}) => {
  const [localKeys, setLocalKeys] = useState<APIKeys>(apiKeys);
  const [localProvider, setLocalProvider] = useState<Provider>(selectedProvider);

  const handleSave = () => {
    onSave(localKeys, localProvider);
    onClose();
  };

  const handleKeyChange = (provider: Provider, value: string) => {
    setLocalKeys({
      ...localKeys,
      [provider]: value,
    });
  };

  return (
    <div className="api-settings">
      <IonCard>
        <IonCardHeader>
          <div className="header-row">
            <IonCardTitle>⚙️ API Settings</IonCardTitle>
            <IonButton fill="clear" onClick={onClose}>
              <IonIcon icon={closeOutline} />
            </IonButton>
          </div>
        </IonCardHeader>
        <IonCardContent>
          <div className="settings-content">
            <IonText color="medium">
              <p>Configure your API keys for different LLM providers. You only need to set up one provider to get started.</p>
            </IonText>

            <div className="provider-selection">
              <IonLabel>
                <strong>Active Provider:</strong>
              </IonLabel>
              <IonSegment
                value={localProvider}
                onIonChange={(e) => setLocalProvider(e.detail.value as Provider)}
              >
                {Object.keys(PROVIDERS).map((provider) => (
                  <IonSegmentButton key={provider} value={provider}>
                    {PROVIDERS[provider as Provider].name}
                  </IonSegmentButton>
                ))}
              </IonSegment>
            </div>

            <div className="api-keys-section">
              {Object.entries(PROVIDERS).map(([key, config]) => {
                const provider = key as Provider;
                return (
                  <div key={provider} className="api-key-input">
                    <IonItem>
                      <IonLabel position="stacked">
                        {config.name} API Key
                        <a
                          href={config.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="get-key-link"
                        >
                          (Get API Key)
                        </a>
                      </IonLabel>
                      <IonInput
                        type="password"
                        value={localKeys[provider]}
                        onIonInput={(e) => handleKeyChange(provider, e.detail.value || '')}
                        placeholder={`Enter ${config.name} API key`}
                      />
                    </IonItem>
                  </div>
                );
              })}
            </div>

            <div className="actions">
              <IonButton expand="block" onClick={handleSave}>
                <IonIcon icon={saveOutline} slot="start" />
                Save Settings
              </IonButton>
            </div>
          </div>
        </IonCardContent>
      </IonCard>
    </div>
  );
};

export default APISettings;
