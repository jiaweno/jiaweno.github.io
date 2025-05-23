// frontend/src/components/features/documents/DocumentList.jsx
import React, { useEffect, useState } from 'react';
import documentService from '../../../services/documentService'; // Adjust path
import { useAuth } from '../../../contexts/AuthContext'; // To ensure user is loaded

const DocumentList = ({ refreshTrigger, onListRefreshed }) => {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const { user, isAuthenticated } = useAuth(); // Get user and isAuthenticated to ensure we only fetch when user is available

    const fetchDocuments = async () => {
        if (!isAuthenticated || !user) { // Check both isAuthenticated and user
            setLoading(false); // Stop loading if not authenticated
            return; 
        }
        setLoading(true);
        setError('');
        try {
            const docs = await documentService.getDocuments();
            setDocuments(docs);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to fetch documents.');
            console.error("Fetch documents error:", err);
        } finally {
            setLoading(false);
            if (onListRefreshed) onListRefreshed();
        }
    };

    useEffect(() => {
        // Only fetch documents if the user is authenticated.
        if (isAuthenticated) {
            fetchDocuments();
        } else {
            // If not authenticated, ensure documents list is empty and not loading.
            setDocuments([]);
            setLoading(false);
        }
    }, [user, isAuthenticated, refreshTrigger]); // Refetch if user, isAuthenticated, or refreshTrigger changes

    const handleDelete = async (docId) => {
        if (window.confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
            try {
                await documentService.deleteDocument(docId);
                setDocuments(documents.filter(doc => doc.id !== docId)); // Optimistic update or refetch
                // fetchDocuments(); // Or refetch the list
            } catch (err) {
                alert(err.response?.data?.detail || 'Failed to delete document.');
                console.error("Delete document error:", err);
            }
        }
    };

    // if (!isAuthenticated) return null; // Or a message prompting login

    if (loading) return <p className="text-center mt-4">Loading documents...</p>;
    if (error) return <p className="text-red-500 bg-red-100 p-3 rounded text-center mt-4">{error}</p>;

    return (
        <div className="my-6">
            <h3 className="text-xl font-semibold mb-4">My Documents</h3>
            {documents.length === 0 && !loading && (
                <p className="text-gray-600">You haven't uploaded any documents yet.</p>
            )}
            {documents.length > 0 && (
                <ul className="space-y-3">
                    {documents.map(doc => (
                        <li key={doc.id} className="p-4 bg-white rounded-lg shadow flex justify-between items-center">
                            <div>
                                <h4 className="text-lg font-medium text-indigo-700">{doc.title}</h4>
                                <p className="text-sm text-gray-600">{doc.description || 'No description'}</p>
                                <p className="text-xs text-gray-400">Status: {doc.status} | Uploaded: {new Date(doc.created_at).toLocaleDateString()}</p>
                                <a href={doc.s3_url} target="_blank" rel="noopener noreferrer" className="text-xs text-blue-500 hover:underline">
                                    View Original
                                </a>
                            </div>
                            <button
                                onClick={() => handleDelete(doc.id)}
                                className="text-sm bg-red-500 hover:bg-red-700 text-white py-1 px-3 rounded focus:outline-none focus:shadow-outline"
                            >
                                Delete
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default DocumentList;
