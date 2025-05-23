// frontend/src/services/quizService.js
import apiClient from './api';

const generateQuizForKP = async (kpId) => {
    const response = await apiClient.post(`/quizzes/generate/kp/${kpId}`);
    return response.data; // Expects GeneratedQuizResponse
};

const generateQuizForLP = async (lpId) => {
    const response = await apiClient.post(`/quizzes/generate/lp/${lpId}`);
    return response.data; // Expects GeneratedQuizResponse
};

export default {
    generateQuizForKP,
    generateQuizForLP,
};
