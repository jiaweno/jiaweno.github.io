// frontend/src/components/features/learning-paths/LearningPathDetail.jsx
import React from 'react';
// This component will be used by ViewLearningPathPage.
// It receives a 'path' object as a prop.

const LearningPathDetail = ({ path }) => {
    if (!path) return <p>Learning path data not available.</p>;

    return (
        <div className="p-6 bg-white rounded-lg shadow-lg">
            <h1 className="text-3xl font-bold mb-2 text-indigo-800">{path.title}</h1>
            <p className="text-md text-gray-700 mb-6">{path.description || "No description provided."}</p>
            
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">Knowledge Points</h2>
            {path.knowledge_points && path.knowledge_points.length > 0 ? (
                <ol className="list-decimal list-inside space-y-3 pl-2">
                    {path.knowledge_points.sort((a,b) => a.sequence_order - b.sequence_order).map(kp => (
                        <li key={kp.id} className="p-3 bg-gray-50 rounded-md shadow-sm hover:bg-gray-100">
                            <span className="font-medium text-gray-700">{kp.title}</span>
                            {/* Optionally, link to the KP or show more details */}
                        </li>
                    ))}
                </ol>
            ) : (
                <p className="text-gray-600">This learning path currently has no knowledge points.</p>
            )}
        </div>
    );
};
export default LearningPathDetail;
