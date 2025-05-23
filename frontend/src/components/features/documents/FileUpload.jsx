// frontend/src/components/features/documents/FileUpload.jsx
import React, { useState } from 'react';
import documentService from '../../../services/documentService'; // Adjust path as needed

const FileUpload = ({ onUploadSuccess }) => {
    const [file, setFile] = useState(null);
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        // Optionally pre-fill title if not already set
        if (!title && e.target.files[0]) {
            setTitle(e.target.files[0].name.split('.').slice(0, -1).join('.')); // Remove extension
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file || !title) {
            setError('File and Title are required.');
            return;
        }
        setLoading(true);
        setError('');
        setSuccess('');
        try {
            await documentService.uploadDocument(file, title, description);
            setSuccess('File uploaded successfully!');
            setFile(null); // Reset file input
            setTitle('');
            setDescription('');
            if (e.target.file) e.target.file.value = null; // Reset file input visually
            if (onUploadSuccess) {
                onUploadSuccess(); // Callback to refresh document list or notify parent
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Upload failed. Please try again.');
            console.error("Upload error:", err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="my-6 p-6 bg-white rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-4">Upload New Document</h3>
            {error && <p className="text-red-500 bg-red-100 p-3 rounded mb-4">{error}</p>}
            {success && <p className="text-green-500 bg-green-100 p-3 rounded mb-4">{success}</p>}
            <form onSubmit={handleSubmit}>
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="title">
                        Document Title <span className="text-red-500">*</span>
                    </label>
                    <input
                        type="text" id="title" value={title} onChange={(e) => setTitle(e.target.value)}
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        required
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
                        Description (Optional)
                    </label>
                    <textarea
                        id="description" value={description} onChange={(e) => setDescription(e.target.value)}
                        rows="3"
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    />
                </div>
                <div className="mb-6">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="file">
                        Document File <span className="text-red-500">*</span>
                    </label>
                    <input
                        type="file" id="file" name="file" onChange={handleFileChange}
                        className="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none"
                        required
                    />
                    {file && <p className="text-xs text-gray-500 mt-1">Selected: {file.name}</p>}
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className="bg-indigo-500 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline disabled:opacity-50"
                >
                    {loading ? 'Uploading...' : 'Upload Document'}
                </button>
            </form>
        </div>
    );
};

export default FileUpload;
