import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import LearningPathForm from '../components/features/learning-paths/LearningPathForm';
import learningPathService from '../services/learningPathService';

const EditLearningPathPage = () => {
    const { pathId } = useParams();
    const [path, setPath] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchPath = async () => {
            try {
                const data = await learningPathService.getLearningPathById(pathId);
                setPath(data);
            } catch (err) {setError('Failed to load path data.'); console.error(err); }
            finally { setLoading(false); }
        };
        fetchPath();
    }, [pathId]);

    if (loading) return <p>Loading path data...</p>;
    if (error) return <p className="text-red-500">{error}</p>;
    if (!path) return <p>Learning path not found.</p>;

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6">Edit Learning Path</h1>
            <LearningPathForm existingPath={path} />
        </div>
    );
};
export default EditLearningPathPage;
