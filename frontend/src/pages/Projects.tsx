import React, { useEffect, useState } from 'react';
import { getProjects, createProject, deleteProject } from '../services/api';
import type { Project } from '../types';
import { Plus, Trash2, Folder } from 'lucide-react';

const Projects: React.FC = () => {
    const [projects, setProjects] = useState<Project[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newProjectName, setNewProjectName] = useState('');
    const [newProjectDesc, setNewProjectDesc] = useState('');

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

    const handleCreate = async () => {
        if (!newProjectName) return;
        await createProject(newProjectName, newProjectDesc);
        setIsModalOpen(false);
        setNewProjectName('');
        setNewProjectDesc('');
        loadProjects();
    };

    const handleDelete = async (id: number) => {
        if (confirm('Are you sure you want to delete this project?')) {
            await deleteProject(id);
            loadProjects();
        }
    };

    return (
        <div className="p-8 text-white">
            <h1 className="text-3xl font-bold mb-8">Projects</h1>
            
            <button 
                onClick={() => setIsModalOpen(true)}
                className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg flex items-center mb-6"
            >
                <Plus className="w-5 h-5 mr-2" /> New Project
            </button>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {projects.map(p => (
                    <div key={p.id} className="bg-gray-800 p-6 rounded-xl border border-gray-700">
                        <div className="flex justify-between items-start mb-4">
                            <div className="flex items-center">
                                <Folder className="w-6 h-6 text-blue-400 mr-3" />
                                <h3 className="text-xl font-semibold">{p.name}</h3>
                            </div>
                            <button onClick={() => handleDelete(p.id)} className="text-red-400 hover:text-red-300">
                                <Trash2 className="w-5 h-5" />
                            </button>
                        </div>
                        <p className="text-gray-400 text-sm mb-4">{p.description || "No description"}</p>
                        <div className="bg-gray-900 rounded p-3">
                            <h4 className="text-xs font-bold text-gray-500 uppercase mb-2">Tasks</h4>
                            {p.tasks.length === 0 ? (
                                <span className="text-gray-600 text-sm">No tasks defined</span>
                            ) : (
                                <ul className="space-y-1">
                                    {p.tasks.map(t => (
                                        <li key={t.id} className="text-sm text-gray-300">• {t.name}</li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Modal - Basic implementation */}
            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
                    <div className="bg-gray-800 p-6 rounded-xl w-full max-w-md border border-gray-700">
                        <h2 className="text-xl font-bold mb-4">New Project</h2>
                        <input
                            type="text"
                            placeholder="Project Name"
                            className="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-4 text-white"
                            value={newProjectName}
                            onChange={e => setNewProjectName(e.target.value)}
                        />
                        <textarea
                            placeholder="Description"
                            className="w-full bg-gray-900 border border-gray-700 rounded p-2 mb-6 text-white h-24"
                            value={newProjectDesc}
                            onChange={e => setNewProjectDesc(e.target.value)}
                        />
                        <div className="flex justify-end space-x-3">
                            <button onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-gray-300 hover:text-white">Cancel</button>
                            <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 rounded text-white hover:bg-blue-500">Create</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Projects;
