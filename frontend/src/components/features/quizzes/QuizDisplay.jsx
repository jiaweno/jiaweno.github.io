// frontend/src/components/features/quizzes/QuizDisplay.jsx
import React from 'react';

// Enum-like object for QuestionType on frontend (matches backend)
const QuestionType = {
    MULTIPLE_CHOICE: "multiple_choice",
    SHORT_ANSWER: "short_answer",
    TRUE_FALSE: "true_false",
};

const QuizDisplay = ({ quizData }) => {
    if (!quizData || !quizData.questions || quizData.questions.length === 0) {
        return <p className="text-gray-600">No quiz questions available to display.</p>;
    }

    return (
        <div className="p-6 bg-gray-50 rounded-lg shadow mt-6">
            <h2 className="text-2xl font-bold mb-4 text-indigo-700">{quizData.title || "Generated Quiz"}</h2>
            
            {quizData.knowledge_point_id && <p className="text-sm text-gray-500 mb-1">Related Knowledge Point ID: {quizData.knowledge_point_id}</p>}
            {quizData.learning_path_id && <p className="text-sm text-gray-500 mb-1">Related Learning Path ID: {quizData.learning_path_id}</p>}
            
            <div className="space-y-6 mt-4">
                {quizData.questions.map((question, index) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-md bg-white shadow-sm">
                        <p className="font-semibold text-gray-800 mb-2">
                            {index + 1}. {question.question_text} 
                            <span className="text-xs font-normal text-gray-500 ml-2">({question.question_type.replace('_', ' ')})</span>
                        </p>
                        
                        {question.question_type === QuestionType.MULTIPLE_CHOICE && question.options && (
                            <ul className="space-y-1 pl-4">
                                {question.options.map((option, optIndex) => (
                                    <li key={optIndex} className={`text-sm ${option.is_correct ? 'font-medium text-green-700' : 'text-gray-700'}`}>
                                        {String.fromCharCode(65 + optIndex)}. {option.text} 
                                        {option.is_correct && <span className="text-green-600 ml-2">(Correct Answer)</span>}
                                    </li>
                                ))}
                            </ul>
                        )}

                        {question.question_type === QuestionType.SHORT_ANSWER && (
                            <div className="mt-2">
                                <p className="text-sm text-gray-500 italic">(Short answer question - input field will be here for answering)</p>
                                {/* For display only, actual answer might be revealed later or not shown here */}
                                {/* {question.correct_answer_text && <p className="text-xs text-blue-500">Suggested Answer: {question.correct_answer_text}</p>} */}
                            </div>
                        )}
                        {/* Add display for other question types like TRUE_FALSE if implemented */}
                    </div>
                ))}
            </div>
            <p className="mt-6 text-sm text-gray-500 italic">
                Quiz display is for review purposes. Answering functionality will be part of the quiz attempt process.
            </p>
        </div>
    );
};

export default QuizDisplay;
