import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for embeddings / model inference if needed
});

export const getHealth = async () => {
  const response = await api.get('/health');
  return response.data;
};

export const screenResumes = async ({ jdText, jdFile, resumes, topK = 5 }) => {
  const formData = new FormData();
  
  if (jdFile) {
    formData.append('jd_file', jdFile);
  } else if (jdText) {
    formData.append('jd_text', jdText);
  }
  
  resumes.forEach((file) => {
    formData.append('resumes', file);
  });
  
  formData.append('top_k', topK);

  const response = await api.post('/screen', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};
