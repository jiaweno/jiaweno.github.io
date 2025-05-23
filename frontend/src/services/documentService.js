// frontend/src/services/documentService.js
import apiClient from './api';

const uploadDocument = async (file, title, description) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    if (description) {
        formData.append('description', description);
    }

    // When sending FormData, the browser automatically sets the Content-Type to multipart/form-data
    // So, we don't need to set it manually in apiClient for this specific request.
    // However, if apiClient has a default Content-Type: application/json, it might need to be overridden or removed for FormData.
    // Axios should handle this correctly if no Content-Type is explicitly set for this request.
    const response = await apiClient.post('/documents/upload', formData, {
        // headers: { 'Content-Type': 'multipart/form-data' } // Axios typically handles this with FormData
    });
    return response.data;
};

const getDocuments = async (skip = 0, limit = 10) => {
    const response = await apiClient.get('/documents/', {
        params: { skip, limit }
    });
    return response.data;
};

const getDocumentById = async (documentId) => {
    const response = await apiClient.get(`/documents/${documentId}`);
    return response.data;
};

const deleteDocument = async (documentId) => {
    await apiClient.delete(`/documents/${documentId}`);
    // No specific response data on 204 No Content
};

export default {
    uploadDocument,
    getDocuments,
    getDocumentById,
    deleteDocument,
};
