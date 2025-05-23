import React from 'react';
import { Link } from 'react-router-dom';
import LearningPathList from '../components/features/learning-paths/LearningPathList';

const LearningPathsPage = () => (
    <div>
        <div className="flex justify-between items-center mb-6">
            <h1 className="text-3xl font-bold">Learning Paths</h1>
            <Link to="/learning-paths/create" className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded">
                Create New Path
            </Link>
        </div>
        <LearningPathList />
    </div>
);
export default LearningPathsPage;
