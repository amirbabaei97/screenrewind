import axios from 'axios';
import type { Project, Task, Rule } from '../types';

export type { Project, Task, Rule, ProjectAnalytics, TaskAnalytics } from '../types';

const api = axios.create({
    baseURL: 'http://localhost:8000',
});

// Projects
export const getProjects = async () => {
    const response = await api.get<Project[]>('/projects/');
    return response.data;
};

export const createProject = async (name: string, description?: string) => {
    const response = await api.post<Project>('/projects/', { name, description });
    return response.data;
};

export const updateProject = async (id: number, name: string, description?: string) => {
    const response = await api.put<Project>(`/projects/${id}`, { name, description });
    return response.data;
};

export const deleteProject = async (id: number) => {
    await api.delete(`/projects/${id}`);
};

// Tasks
export const createTask = async (projectId: number, name: string, description?: string) => {
    const response = await api.post<Task>(`/projects/${projectId}/tasks`, { name, description });
    return response.data;
};

export const deleteTask = async (taskId: number) => {
    await api.delete(`/projects/tasks/${taskId}`);
};

// Rules
export const getRules = async () => {
    const response = await api.get<Rule[]>('/rules/');
    return response.data;
};

export const createRule = async (rule: Omit<Rule, 'id'>) => {
    const response = await api.post<Rule>('/rules/', rule);
    return response.data;
};

export const deleteRule = async (id: number) => {
    await api.delete(`/rules/${id}`);
};

// Analytics
export interface ChartData {
    name: string;
    value: number;
    percentage: number;
}

export const getProjectAnalytics = async (start: Date, end: Date) => {
    const response = await api.get<ChartData[]>('/analytics/projects', {
        params: {
            start: start.toISOString(),
            end: end.toISOString()
        }
    });
    return response.data;
};

export const getTaskAnalytics = async (projectName: string, start: Date, end: Date) => {
    const response = await api.get<ChartData[]>(`/analytics/projects/${projectName}/tasks`, {
        params: {
            start: start.toISOString(),
            end: end.toISOString()
        }
    });
    return response.data;
};

// System
export const resetDatabase = async () => {
    const response = await api.delete('/system/reset-data');
    return response.data;
};
