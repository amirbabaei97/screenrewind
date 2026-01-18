import React, { useEffect, useState } from 'react';
import { getProjects, createProject, updateProject, deleteProject, createTask, deleteTask, updateTask } from '../services/api';
import type { Project } from '../types';
import { Plus, Trash2, Folder, Pencil, X } from 'lucide-react';

const Projects: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);

    // Project Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingProject, setEditingProject] = useState<Project | null>(null);
    const [projectName, setProjectName] = useState('');
    const [projectDesc, setProjectDesc] = useState('');

    // Task Modal State
    const [isTaskModalOpen, setIsTaskModalOpen] = useState(false);
    const [editingTask, setEditingTask] = useState<any | null>(null);
    const [taskName, setTaskName] = useState('');
    const [taskDesc, setTaskDesc] = useState('');
    const [currentProjectId, setCurrentProjectId] = useState<number | null>(null);

    // Removed newTaskNames state as we use modal now

    useEffect(() => {
        loadProjects();
    }, []);

    const loadProjects = async () => {
        try {
            const data = await getProjects();
            setProjects(data);
        } catch (e) {
            console.error(e);
        }
    };

    const openCreateModal = () => {
        setEditingProject(null);
        setProjectName('');
        setProjectDesc('');
        setIsModalOpen(true);
    };

    const openEditModal = (project: Project) => {
        setEditingProject(project);
        setProjectName(project.name);
        setProjectDesc(project.description || '');
        setIsModalOpen(true);
    };

    const handleSaveProject = async () => {
        if (!projectName) return;

        try {
            if (editingProject) {
                await updateProject(editingProject.id, projectName, projectDesc);
            } else {
                await createProject(projectName, projectDesc);
            }
            setIsModalOpen(false);
            loadProjects();
        } catch (e) {
            console.error("Failed to save project", e);
        }
    };

    const handleDeleteProject = async (id: number) => {
        if (confirm('Are you sure you want to delete this project?')) {
            await deleteProject(id);
            loadProjects();
        }
    };

    const openCreateTaskModal = (projectId: number) => {
        setEditingTask(null);
        setTaskName('');
        setTaskDesc('');
        setCurrentProjectId(projectId);
        setIsTaskModalOpen(true);
    };

    const openEditTaskModal = (task: any) => {
        setEditingTask(task);
        setTaskName(task.name);
        setTaskDesc(task.description || '');
        setCurrentProjectId(task.project_id);
        setIsTaskModalOpen(true);
    };

    const handleSaveTask = async () => {
        if (!taskName || currentProjectId === null) return;

        try {
            if (editingTask) {
                await updateTask(editingTask.id, taskName, taskDesc);
            } else {
                await createTask(currentProjectId, taskName, taskDesc);
            }
            setIsTaskModalOpen(false);
            loadProjects();
        } catch (e) {
            console.error("Failed to save task", e);
        }
    };

    const handleDeleteTask = async (taskId: number) => {
        if (confirm('Delete this task?')) {
            try {
                await deleteTask(taskId);
                loadProjects();
            } catch (e) {
                console.error("Failed to delete task", e);
            }
        }
    };

    return (
        <div className="p-8 text-white">
            <h1 className="text-3xl font-bold mb-8">Projects</h1>

            <button
                onClick={openCreateModal}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center mb-6"
            >
                <Plus className="w-5 h-5 mr-2" /> New Project
            </button>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map(p => (
                    <div key={p.id} className="bg-gray-800 p-6 rounded-xl border border-gray-700 flex flex-col h-full">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center">
                                <Folder className="w-6 h-6 text-blue-400 mr-3" />
                                <h3 className="text-xl font-semibold truncate max-w-[150px]" title={p.name}>{p.name}</h3>
                            </div>
                            <div className="flex space-x-2">
                                <button onClick={() => openEditModal(p)} className="text-gray-400 hover:text-white">
                                    <Pencil className="w-4 h-4" />
                                </button>
                                <button onClick={() => handleDeleteProject(p.id)} className="text-red-400 hover:text-red-300">
                                    <Trash2 className="w-5 h-5" />
                                </button>
                            </div>
                        </div>
                        <p className="text-gray-400 text-sm mb-4 flex-grow">{p.description || "No description"}</p>

                        <div className="bg-gray-900 rounded p-3 mt-auto">
                            <h4 className="flex justify-between items-center text-xs font-bold text-gray-500 uppercase mb-2">
                                <span>Tasks</span>
                                <button
                                    onClick={() => openCreateTaskModal(p.id)}
                                    className="text-blue-400 hover:text-blue-300"
                                    title="Add Task"
                                >
                                    <Plus className="w-4 h-4" />
                                </button>
                            </h4>

                            <ul className="space-y-2 mb-3 max-h-40 overflow-y-auto">
                                {p.tasks.length === 0 ? (
                                    <li className="text-gray-600 text-sm italic">No tasks defined</li>
                                ) : (
                                    p.tasks.map(t => (
                                        <li key={t.id} className="bg-gray-800 rounded p-2 text-sm text-gray-300 border border-gray-700 group">
                                            <div className="flex justify-between items-start">
                                                <span className="font-medium text-white">{t.name}</span>
                                                <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                                    <button
                                                        onClick={() => openEditTaskModal(t)}
                                                        className="text-gray-500 hover:text-white"
                                                    >
                                                        <Pencil className="w-3 h-3" />
                                                    </button>
                                                    <button
                                                        onClick={() => handleDeleteTask(t.id)}
                                                        className="text-gray-500 hover:text-red-400"
                                                    >
                                                        <X className="w-3 h-3" />
                                                    </button>
                                                </div>
                                            </div>
                                            {t.description && (
                                                <p className="text-xs text-gray-500 mt-1 line-clamp-2">{t.description}</p>
                                            )}
                                        </li>
                                    ))
                                )}
                            </ul>
                        </div>
                    </div>
                ))}
            </div>

            {/* Project Modal */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-gray-800 p-6 rounded-xl w-full max-w-md border border-gray-700 shadow-2xl">
                        <h2 className="text-xl font-bold mb-4">{editingProject ? 'Edit Project' : 'New Project'}</h2>
                        <input
                            type="text"
                            placeholder="Project Name"
                            className="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-4 text-white focus:outline-none focus:border-blue-500"
                            value={projectName}
                            onChange={e => setProjectName(e.target.value)}
                        />
                        <textarea
                            placeholder="Description"
                            className="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-6 text-white h-24 focus:outline-none focus:border-blue-500"
                            value={projectDesc}
                            onChange={e => setProjectDesc(e.target.value)}
                        />
                        <div className="flex justify-end space-x-3">
                            <button onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-gray-300 hover:text-white">Cancel</button>
                            <button onClick={handleSaveProject} className="px-4 py-2 bg-blue-600 rounded text-white hover:bg-blue-500">
                                {editingProject ? 'Save Changes' : 'Create Project'}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Task Modal */}
            {isTaskModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
                    <div className="bg-gray-800 p-6 rounded-xl w-full max-w-md border border-gray-700 shadow-2xl">
                        <h2 className="text-xl font-bold mb-4">{editingTask ? 'Edit Task' : 'New Task'}</h2>
                        <input
                            type="text"
                            placeholder="Task Name"
                            className="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-4 text-white focus:outline-none focus:border-blue-500"
                            value={taskName}
                            onChange={e => setTaskName(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && document.getElementById('save-task-btn')?.click()}
                        />
                        <textarea
                            placeholder="Description"
                            className="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-6 text-white h-24 focus:outline-none focus:border-blue-500"
                            value={taskDesc}
                            onChange={e => setTaskDesc(e.target.value)}
                        />
                        <div className="flex justify-end space-x-3">
                            <button onClick={() => setIsTaskModalOpen(false)} className="px-4 py-2 text-gray-300 hover:text-white">Cancel</button>
                            <button
                                id="save-task-btn"
                                onClick={handleSaveTask}
                                className="px-4 py-2 bg-blue-600 rounded text-white hover:bg-blue-500"
                            >
                                {editingTask ? 'Save Changes' : 'Add Task'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Projects;

