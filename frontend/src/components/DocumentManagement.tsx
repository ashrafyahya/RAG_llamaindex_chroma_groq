/**
 * Document Management Component
 * Handles document upload, listing, and deletion
 */
import React, { useState, useEffect } from 'react';
import {
  IonButton,
  IonCard,
  IonCardContent,
  IonCardHeader,
  IonCardTitle,
  IonIcon,
  IonList,
  IonItem,
  IonLabel,
  IonSpinner,
  IonText,
} from '@ionic/react';
import {
  cloudUploadOutline,
  trashOutline,
  documentTextOutline,
  closeOutline,
} from 'ionicons/icons';
import { Document } from '../types';
import apiService from '../services/api';
import './DocumentManagement.css';

interface DocumentManagementProps {
  onClose: () => void;
}

const DocumentManagement: React.FC<DocumentManagementProps> = ({ onClose }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const docs = await apiService.listDocuments();
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    try {
      for (let i = 0; i < files.length; i++) {
        await apiService.uploadDocument(files[i]);
      }
      await loadDocuments();
    } catch (error) {
      console.error('Error uploading documents:', error);
      alert('Error uploading documents. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDeleteDocument = async (docId: string) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }

    try {
      await apiService.deleteDocument(docId);
      await loadDocuments();
    } catch (error) {
      console.error('Error deleting document:', error);
      alert('Error deleting document. Please try again.');
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to delete ALL documents?')) {
      return;
    }

    try {
      await apiService.clearAllDocuments();
      await loadDocuments();
    } catch (error) {
      console.error('Error clearing documents:', error);
      alert('Error clearing documents. Please try again.');
    }
  };

  return (
    <div className="document-management">
      <IonCard>
        <IonCardHeader>
          <div className="header-row">
            <IonCardTitle>📁 Document Management</IonCardTitle>
            <IonButton fill="clear" onClick={onClose}>
              <IonIcon icon={closeOutline} />
            </IonButton>
          </div>
        </IonCardHeader>
        <IonCardContent>
          <div className="upload-section">
            <input
              type="file"
              id="file-upload"
              multiple
              accept=".txt,.pdf,.docx,.md"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <label htmlFor="file-upload">
              <IonButton expand="block" disabled={uploading}>
                <IonIcon icon={cloudUploadOutline} slot="start" />
                {uploading ? 'Uploading...' : 'Upload Documents'}
              </IonButton>
            </label>

            {documents.length > 0 && (
              <IonButton
                expand="block"
                color="danger"
                fill="outline"
                onClick={handleClearAll}
                disabled={loading}
              >
                <IonIcon icon={trashOutline} slot="start" />
                Clear All Documents
              </IonButton>
            )}
          </div>

          <div className="documents-list">
            <h3>Uploaded Documents ({documents.length})</h3>
            {loading ? (
              <div className="loading-container">
                <IonSpinner />
              </div>
            ) : documents.length === 0 ? (
              <IonText color="medium">
                <p>No documents uploaded yet. Upload some documents to get started.</p>
              </IonText>
            ) : (
              <IonList>
                {documents.map((doc) => (
                  <IonItem key={doc.ids[0]}>
                    <IonIcon icon={documentTextOutline} slot="start" />
                    <IonLabel>{doc.name}</IonLabel>
                    <IonButton
                      fill="clear"
                      color="danger"
                      onClick={() => handleDeleteDocument(doc.ids[0])}
                    >
                      <IonIcon icon={trashOutline} />
                    </IonButton>
                  </IonItem>
                ))}
              </IonList>
            )}
          </div>
        </IonCardContent>
      </IonCard>
    </div>
  );
};

export default DocumentManagement;
