// frontend/src/components/features/learning-paths/LearningPathForm.jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import learningPathService from '../../../services/learningPathService';
import KnowledgePointSelector from '../knowledge-points/KnowledgePointSelector'; // Adjust path

const LearningPathForm = ({ existingPath }) => {
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [selectedKPs, setSelectedKPs] = useState([]); // Store as {knowledge_point_id, sequence_order, title (for display)}
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        if (existingPath) {
            setTitle(existingPath.title || '');
            setDescription(existingPath.description || '');
            // Map existing KPs to the format needed for the form
            const mappedKPs = existingPath.knowledge_points.map(kp => ({
                knowledge_point_id: kp.id, // Assuming kp.id from response is the knowledge_point_id
                sequence_order: kp.sequence_order,
                title: kp.title // For display in the selected list
            })).sort((a, b) => a.sequence_order - b.sequence_order);
            setSelectedKPs(mappedKPs);
        }
    }, [existingPath]);

    const handleAddKP = (kp) => {
        const newKP = { 
            knowledge_point_id: kp.id, 
            title: kp.title, // Store title for display in selected list
            sequence_order: selectedKPs.length + 1 
        };
        setSelectedKPs([...selectedKPs, newKP]);
    };

    const handleRemoveKP = (kpIdToRemove) => {
        setSelectedKPs(
            selectedKPs.filter(kp => kp.knowledge_point_id !== kpIdToRemove)
                         .map((kp, index) => ({ ...kp, sequence_order: index + 1 })) // Re-sequence
        );
    };
    
    const moveKP = (index, direction) => {
         const newKPs = [...selectedKPs];
         const kpToMove = newKPs[index];
         const swapIndex = direction === 'up' ? index - 1 : index + 1;

         if (swapIndex < 0 || swapIndex >= newKPs.length) return; // Boundary check

         newKPs[index] = newKPs[swapIndex];
         newKPs[swapIndex] = kpToMove;
         
         // Update sequence_order for all items
         const reorderedKPs = newKPs.map((kp, idx) => ({ ...kp, sequence_order: idx + 1 }));
         setSelectedKPs(reorderedKPs);
    };


    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!title) {
            setError('Title is required.');
            return;
        }
        setLoading(true);
        setError('');

        const pathData = {
            title,
            description,
            knowledge_points: selectedKPs.map(kp => ({
                knowledge_point_id: kp.knowledge_point_id,
                sequence_order: kp.sequence_order,
            })),
        };

        try {
            if (existingPath) {
                await learningPathService.updateLearningPath(existingPath.id, pathData);
            } else {
                await learningPathService.createLearningPath(pathData);
            }
            navigate('/learning-paths'); // Redirect after success
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to save learning path.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6 p-4 bg-white shadow rounded-lg">
            {error && <p className="text-red-500 bg-red-100 p-3 rounded">{error}</p>}
            <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">Title <span className="text-red-500">*</span></label>
                <input type="text" id="title" value={title} onChange={(e) => setTitle(e.target.value)} required
                       className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"/>
            </div>
            <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">Description</label>
                <textarea id="description" value={description} onChange={(e) => setDescription(e.target.value)} rows="3"
                          className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"/>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <h4 className="font-semibold mb-2">Selected Knowledge Points (Order Matters)</h4>
                    {selectedKPs.length === 0 ? <p className="text-sm text-gray-500">No knowledge points selected yet.</p> : (
                        <ul className="border p-2 rounded-md max-h-96 overflow-y-auto">
                            {selectedKPs.map((kp, index) => (
                                <li key={kp.knowledge_point_id} className="flex justify-between items-center p-2 border-b hover:bg-gray-50">
                                    <span className="flex-grow">
                                        <span className="font-medium">{kp.sequence_order}.</span> {kp.title}
                                    </span>
                                    <div className="space-x-1 flex-shrink-0">
                                        <button type="button" onClick={() => moveKP(index, 'up')} disabled={index === 0} className="text-xs p-1 rounded hover:bg-gray-200 disabled:opacity-50">↑</button>
                                        <button type="button" onClick={() => moveKP(index, 'down')} disabled={index === selectedKPs.length - 1} className="text-xs p-1 rounded hover:bg-gray-200 disabled:opacity-50">↓</button>
                                        <button type="button" onClick={() => handleRemoveKP(kp.knowledge_point_id)} className="text-xs bg-red-100 hover:bg-red-200 text-red-700 py-1 px-2 rounded">Remove</button>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
                </div>
                <KnowledgePointSelector selectedKPs={selectedKPs} onAddKP={handleAddKP} onRemoveKP={handleRemoveKP} />
            </div>

            <div className="flex justify-end space-x-3">
                <button type="button" onClick={() => navigate('/learning-paths')}
                        className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Cancel
                </button>
                <button type="submit" disabled={loading}
                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
                    {loading ? 'Saving...' : (existingPath ? 'Update Path' : 'Create Path')}
                </button>
            </div>
        </form>
    );
};
export default LearningPathForm;
