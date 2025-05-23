// frontend/src/services/knowledgePointService.js
import apiClient from './api';

// Basic version: Fetches all KPs. Later, add filters (by document, search terms).
const getKnowledgePoints = async (documentId = null) => {
    let url = '/knowledge-points/'; // Assuming a new backend endpoint for KPs
    if (documentId) {
        url += `?document_id=${documentId}`;
    }
    // This endpoint needs to be created on the backend if it doesn't exist.
    // For now, let's assume it exists and returns a list of {id, title, document_title (optional)}.
    // If not, this service will be a placeholder.
    // As a fallback if a generic KP list endpoint is not ready,
    // we might need to fetch documents, then KPs for a selected document.
    // For now, this is a placeholder for a generic KP listing.
    // const response = await apiClient.get(url);
    // return response.data;
    
    // MOCKUP if backend endpoint is not ready for generic KP listing:
    console.warn("Mocking knowledge points as backend endpoint is not specified/ready.");
    return [
        { id: 'kp_uuid_1', title: 'Introduction to AI (Mock)', document_title: 'AI Basics Doc (Mock)' },
        { id: 'kp_uuid_2', title: 'Machine Learning Fundamentals (Mock)', document_title: 'AI Basics Doc (Mock)' },
        { id: 'kp_uuid_3', title: 'Neural Networks Overview (Mock)', document_title: 'Deep Learning Doc (Mock)' },
    ];
};

export default { getKnowledgePoints };
