export interface Task {
    id: number;
    name: string;
    description?: string;
    project_id: number;
}

export interface Project {
    id: number;
    name: string;
    description?: string;
    tasks: Task[];
}

export interface Rule {
    id: number;
    name: string;
    pattern: string;
    field: string;
    project_id?: number;
    task_id?: number;
}

export interface ProjectAnalytics {
    project_name: string;
    duration_seconds: number;
    percentage: number;
}

export interface TaskAnalytics {
    task_name: string;
    duration_seconds: number;
    percentage: number;
}
