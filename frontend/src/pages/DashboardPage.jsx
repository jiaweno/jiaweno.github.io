// frontend/src/pages/DashboardPage.jsx
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import FileUpload from '../components/features/documents/FileUpload'; // Adjust path
import DocumentList from '../components/features/documents/DocumentList'; // Adjust path

const DashboardPage = () => {
    const { user } = useAuth();
    const [refreshTrigger, setRefreshTrigger] = useState(0); // To trigger list refresh

    const handleUploadSuccess = () => {
        setRefreshTrigger(prev => prev + 1); // Increment to trigger useEffect in DocumentList
    };

    return (
        <div>
            <h1 className="text-3xl font-bold mb-6 text-center md:text-left">
                Welcome, {user?.full_name || user?.email}!
            </h1>
            
            <div className="mb-8">
              <p className="text-lg text-gray-700">Manage your documents below. Upload new files and see their processing status.</p>
            </div>

            {/* Using a grid layout as suggested in the prompt for side-by-side view on medium screens and up */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-6"> {/* Added gap-x for horizontal spacing */}
                <div>
                    <FileUpload onUploadSuccess={handleUploadSuccess} />
                </div>
                <div>
                    <DocumentList refreshTrigger={refreshTrigger} />
                </div>
            </div>

            {/* Other dashboard content can go here, e.g.:
            <div className="mt-10 p-6 bg-white rounded-lg shadow-md">
                <h2 className="text-2xl font-semibold mb-4">Learning Paths</h2>
                <p>Your personalized learning paths will appear here soon.</p>
            </div>
            <div className="mt-6 p-6 bg-white rounded-lg shadow-md">
                <h2 className="text-2xl font-semibold mb-4">Quizzes & Assessments</h2>
                <p>Quizzes based on your documents will be available here.</p>
            </div>
            */}
        </div>
    );
};

export default DashboardPage;
