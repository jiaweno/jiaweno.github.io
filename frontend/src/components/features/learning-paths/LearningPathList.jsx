// frontend/src/components/features/learning-paths/LearningPathList.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import learningPathService from '../../../services/learningPathService';

const LearningPathList = () => {
    const [paths, setPaths] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchPaths = async () => {
            try {
                setLoading(true);
                const data = await learningPathService.getLearningPaths();
                setPaths(data);
            } catch (err) {
                setError('Failed to fetch learning paths.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchPaths();
    }, []);
    
    const handleDeletePath = async (pathId) => {
        if (window.confirm('Are you sure you want to delete this learning path?')) {
            try {
                await learningPathService.deleteLearningPath(pathId);
                setPaths(paths.filter(p => p.id !== pathId)); // Update UI
            } catch (err) {
                alert('Failed to delete path.');
                console.error(err);
            }
        }
    };


    if (loading) return <p>Loading learning paths...</p>;
    if (error) return <p className="text-red-500">{error}</p>;

    return (
        <div className="space-y-4">
            {paths.length === 0 && <p>No learning paths created yet.</p>}
            {paths.map(path => (
                <div key={path.id} className="p-4 bg-white rounded-lg shadow">
                    <h3 className="text-xl font-semibold text-indigo-700">{path.title}</h3>
                    <p className="text-sm text-gray-600 mb-2">{path.description || 'No description.'}</p>
                    <p className="text-xs text-gray-500">Knowledge Points: {path.knowledge_points?.length || 0}</p>
                    <div className="mt-3 space-x-2">
                        <Link to={`/learning-paths/${path.id}`} className="text-sm text-indigo-600 hover:text-indigo-800">View Details</Link>
                        <Link to={`/learning-paths/edit/${path.id}`} className="text-sm text-green-600 hover:text-green-800">Edit</Link>
                        <button onClick={() => handleDeletePath(path.id)} className="text-sm text-red-600 hover:text-red-800">Delete</button>
                    </div>
                </div>
            ))}
        </div>
    );
};
export default LearningPathList;
