import React, { useEffect, useState } from 'react';
import { getRules, createRule, deleteRule, getProjects } from '../services/api';
import type { Rule, Project } from '../types';
import { Plus, Trash2 } from 'lucide-react';

const Rules: React.FC = () => {
    const [rules, setRules] = useState<Rule[]>([]);
    const [projects, setProjects] = useState<Project[]>([]);
    const [isModalOpen, setIsModalOpen] = useState(false);

    // Form state
    const [name, setName] = useState('');
    const [pattern, setPattern] = useState('');
    const [field, setField] = useState('window_title'); // or app_name, ocr_text
    const [projectId, setProjectId] = useState<number | ''>('');
    const [taskId, setTaskId] = useState<number | ''>('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        const [r, p] = await Promise.all([getRules(), getProjects()]);
        setRules(r);
        setProjects(p);
    };

    const handleCreate = async () => {
        if (!name || !pattern || !projectId) return;

        await createRule({
            name,
            pattern,
            field,
            project_id: Number(projectId),
            task_id: taskId ? Number(taskId) : undefined
        });

        setIsModalOpen(false);
        resetForm();
        loadData();
    };

    const resetForm = () => {
        setName('');
        setPattern('');
        setProjectId('');
        setTaskId('');
    };

    const handleDelete = async (id: number) => {
        if (confirm('Delete rule?')) {
            await deleteRule(id);
            loadData();
        }
    };

    const selectedProject = projects.find(p => p.id === Number(projectId));

    return (
        <div className="p-8 text-white">
            <h1 className="text-3xl font-bold mb-8">Categorization Rules</h1>

            <button onClick={() => setIsModalOpen(true)} className="bg-blue-600 px-4 py-2 rounded mb-6 flex items-center">
                <Plus className="w-4 h-4 mr-2" /> New Rule
            </button>

            <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-gray-700 text-gray-300">
                        <tr>
                            <th className="p-4">Name</th>
                            <th className="p-4">Pattern (Regex)</th>
                            <th className="p-4">Field</th>
                            <th className="p-4">Maps To</th>
                            <th className="p-4">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rules.map(rule => {
                            const p = projects.find(x => x.id === rule.project_id);
                            const t = p?.tasks.find(x => x.id === rule.task_id);

                            return (
                                <tr key={rule.id} className="border-t border-gray-700 hover:bg-gray-750">
                                    <td className="p-4 font-medium">{rule.name}</td>
                                    <td className="p-4 font-mono text-sm text-yellow-500">{rule.pattern}</td>
                                    <td className="p-4 text-gray-400">{rule.field}</td>
                                    <td className="p-4">
                                        <span className="bg-blue-900 text-blue-200 px-2 py-1 rounded text-xs mr-2">{p?.name || 'Unknown'}</span>
                                        {t && <span className="bg-green-900 text-green-200 px-2 py-1 rounded text-xs">{t.name}</span>}
                                    </td>
                                    <td className="p-4">
                                        <button onClick={() => handleDelete(rule.id)} className="text-red-400">
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>

            {isModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
                    <div className="bg-gray-800 p-6 rounded-xl w-full max-w-lg border border-gray-700">
                        <h2 className="text-xl font-bold mb-4">Create Regex Rule</h2>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Rule Name</label>
                                <input type="text" className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                    value={name} onChange={e => setName(e.target.value)} />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Field</label>
                                    <select className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                        value={field} onChange={e => setField(e.target.value)}>
                                        <option value="window_title">Window Title</option>
                                        <option value="app_name">App Name</option>
                                        <option value="ocr_text">OCR Text</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Regex Pattern</label>
                                    <input type="text" className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white font-mono"
                                        value={pattern} onChange={e => setPattern(e.target.value)} placeholder="e.g. .*VS Code.*" />
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Assign Project</label>
                                    <select className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                        value={projectId} onChange={e => setProjectId(Number(e.target.value))}>
                                        <option value="">Select Project</option>
                                        {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm text-gray-400 mb-1">Assign Task (Optional)</label>
                                    <select className="w-full bg-gray-900 border border-gray-700 rounded p-2 text-white"
                                        value={taskId} onChange={e => setTaskId(Number(e.target.value))} disabled={!projectId}>
                                        <option value="">General</option>
                                        {selectedProject?.tasks.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
                                    </select>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end space-x-3 mt-6">
                            <button onClick={() => setIsModalOpen(false)} className="px-4 py-2 text-gray-300 hover:text-white">Cancel</button>
                            <button onClick={handleCreate} className="px-4 py-2 bg-blue-600 rounded text-white hover:bg-blue-500">Save Rule</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Rules;
