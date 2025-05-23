// frontend/src/components/features/knowledge-points/KnowledgePointSelector.jsx
import React, { useState, useEffect } from 'react';
import knowledgePointService from '../../../services/knowledgePointService';

const KnowledgePointSelector = ({ selectedKPs, onAddKP, onRemoveKP, availableKPsList = null }) => {
    const [availableKPs, setAvailableKPs] = useState(availableKPsList || []);
    const [loading, setLoading] = useState(!availableKPsList);
    const [error, setError] = useState('');
    // const [searchTerm, setSearchTerm] = useState(''); // For future search/filter

    useEffect(() => {
        if (availableKPsList) return; // KPs provided directly

        const fetchKPs = async () => {
            try {
                setLoading(true);
                const kps = await knowledgePointService.getKnowledgePoints(); // Basic fetch
                setAvailableKPs(kps);
                setError('');
            } catch (err) {
                setError('Failed to load knowledge points.');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchKPs();
    }, [availableKPsList]);
    
    const selectedKPIds = selectedKPs.map(kp => kp.knowledge_point_id);

    if (loading) return <p>Loading knowledge points...</p>;
    if (error) return <p className="text-red-500">{error}</p>;

    return (
        <div className="border p-4 rounded-md">
            <h4 className="font-semibold mb-2">Available Knowledge Points</h4>
            {/* Add search/filter input here later */}
            <ul className="max-h-60 overflow-y-auto">
                {availableKPs.filter(kp => !selectedKPIds.includes(kp.id)).map(kp => (
                    <li key={kp.id} className="flex justify-between items-center p-2 border-b">
                        <span>{kp.title} <span className="text-xs text-gray-500">({kp.document_title || 'General'})</span></span>
                        <button 
                            type="button" 
                            onClick={() => onAddKP(kp)}
                            className="text-sm bg-green-500 hover:bg-green-700 text-white py-1 px-2 rounded"
                        >
                            Add
                        </button>
                    </li>
                ))}
                 {availableKPs.filter(kp => !selectedKPIds.includes(kp.id)).length === 0 && <p className="text-sm text-gray-500">No more KPs to add or all KPs selected.</p>}
            </ul>
        </div>
    );
};
export default KnowledgePointSelector;
