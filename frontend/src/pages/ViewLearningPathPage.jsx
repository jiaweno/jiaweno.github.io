// frontend/src/pages/ViewLearningPathPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import LearningPathDetail from '../components/features/learning-paths/LearningPathDetail';
import learningPathService from '../services/learningPathService';
import quizService from '../services/quizService'; // Import quiz service
import QuizDisplay from '../components/features/quizzes/QuizDisplay'; // Import display component

const ViewLearningPathPage = () => {
    const { pathId } = useParams();
    const [path, setPath] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    
    const [generatedQuiz, setGeneratedQuiz] = useState(null);
    const [quizLoading, setQuizLoading] = useState(false);
    const [quizError, setQuizError] = useState('');

    useEffect(() => {
        const fetchPath = async () => {
            try { 
                setLoading(true);
                setError('');
                setGeneratedQuiz(null); // Clear previous quiz on path change
                const data = await learningPathService.getLearningPathById(pathId);
                setPath(data);
            } catch (err) { 
                setError('Failed to load learning path.'); 
                console.error(err); 
            } finally { 
                setLoading(false); 
            }
        };
        if (pathId) fetchPath();
    }, [pathId]);

    const handleGenerateQuiz = async () => {
        if (!pathId) return;
        setQuizLoading(true);
        setQuizError('');
        setGeneratedQuiz(null);
        try {
            const quizData = await quizService.generateQuizForLP(pathId);
            setGeneratedQuiz(quizData);
        } catch (err) {
            setQuizError(err.response?.data?.detail || 'Failed to generate quiz.');
            console.error("Quiz generation error:", err);
        } finally {
            setQuizLoading(false);
        }
    };

    if (loading) return <p>Loading learning path...</p>;
    if (error) return <p className="text-red-500 bg-red-100 p-3 rounded text-center">{error}</p>;
    if (!path) return <p>Learning path not found.</p>;
    
    return (
        <div>
            <div className="mb-4">
                <Link to="/learning-paths" className="text-indigo-600 hover:text-indigo-800">&larr; Back to Learning Paths</Link>
            </div>
            <LearningPathDetail path={path} />
            
            <div className="mt-6 space-x-3">
                <Link to={`/learning-paths/edit/${path.id}`} className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                    Edit Path
                </Link>
                <button 
                    onClick={handleGenerateQuiz} 
                    disabled={quizLoading}
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
                >
                    {quizLoading ? 'Generating Quiz...' : 'Generate Quiz for this Path'}
                </button>
            </div>

            {quizError && <p className="text-red-500 bg-red-100 p-3 rounded text-center mt-4">{quizError}</p>}
            {generatedQuiz && <QuizDisplay quizData={generatedQuiz} />}
        </div>
    );
};
export default ViewLearningPathPage;
