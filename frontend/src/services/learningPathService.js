// frontend/src/services/learningPathService.js
import apiClient from './api';

const createLearningPath = async (pathData) => {
    // pathData: { title, description, knowledge_points: [{knowledge_point_id, sequence_order}] }
    const response = await apiClient.post('/learning-paths/', pathData);
    return response.data;
};

const getLearningPaths = async (skip = 0, limit = 10) => {
    const response = await apiClient.get('/learning-paths/', { params: { skip, limit } });
    return response.data; // Expects List[LearningPathResponse]
};

const getLearningPathById = async (pathId) => {
    const response = await apiClient.get(`/learning-paths/${pathId}`);
    return response.data; // Expects LearningPathResponse
};

const updateLearningPath = async (pathId, pathData) => {
    // pathData: { title?, description?, knowledge_points?: [{knowledge_point_id, sequence_order}] }
    const response = await apiClient.put(`/learning-paths/${pathId}`, pathData);
    return response.data;
};

const deleteLearningPath = async (pathId) => {
    await apiClient.delete(`/learning-paths/${pathId}`);
};

export default {
    createLearningPath,
    getLearningPaths,
    getLearningPathById,
    updateLearningPath,
    deleteLearningPath,
};
