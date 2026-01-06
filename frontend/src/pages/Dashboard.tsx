import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { getProjectAnalytics, getTaskAnalytics } from '../services/api';
import type { ChartData } from '../services/api';
import { Calendar, BarChart2 } from 'lucide-react';
import clsx from 'clsx';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FF6B6B', '#6B5B95'];

const Dashboard: React.FC = () => {
    const [period, setPeriod] = useState<'today' | 'yesterday'>('today');
    const [projectData, setProjectData] = useState<ChartData[]>([]);
    const [selectedProject, setSelectedProject] = useState<string | null>(null);
    const [taskData, setTaskData] = useState<ChartData[]>([]);
    const [loading, setLoading] = useState(false);

    const getDateRange = () => {
        const end = new Date();
        const start = new Date();
        start.setHours(0, 0, 0, 0);
        
        if (period === 'yesterday') {
            start.setDate(start.getDate() - 1);
            end.setDate(end.getDate() - 1);
            end.setHours(23, 59, 59, 999);
        }
        
        return { start, end };
    };

    useEffect(() => {
        fetchProjects();
    }, [period]);

    useEffect(() => {
        if (selectedProject) {
            fetchTasks(selectedProject);
        } else {
            setTaskData([]);
        }
    }, [selectedProject, period]);

    const fetchProjects = async () => {
        setLoading(true);
        try {
            const { start, end } = getDateRange();
            const data = await getProjectAnalytics(start, end);
            setProjectData(data);
        } catch (error) {
            console.error("Failed to fetch project data", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchTasks = async (projectName: string) => {
        try {
            const { start, end } = getDateRange();
            const data = await getTaskAnalytics(projectName, start, end);
            setTaskData(data);
        } catch (error) {
            console.error("Failed to fetch task data", error);
        }
    };

    const onProjectClick = (data: any) => {
        if (data && data.name) {
            setSelectedProject(data.name === selectedProject ? null : data.name);
        }
    };

    return (
        <div className="p-8">
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">Dashboard</h1>
                    <p className="text-gray-400 mt-1">Overview of your activity</p>
                </div>
                
                <div className="flex bg-gray-800 rounded-lg p-1 border border-gray-700">
                    <button 
                        onClick={() => setPeriod('today')}
                        className={clsx(
                            "px-4 py-2 rounded-md text-sm font-medium transition-colors",
                            period === 'today' ? "bg-blue-600 text-white" : "text-gray-300 hover:text-white"
                        )}
                    >
                        Today
                    </button>
                    <button 
                        onClick={() => setPeriod('yesterday')}
                        className={clsx(
                            "px-4 py-2 rounded-md text-sm font-medium transition-colors",
                            period === 'yesterday' ? "bg-blue-600 text-white" : "text-gray-300 hover:text-white"
                        )}
                    >
                        Yesterday
                    </button>
                </div>
            </header>

            {loading ? (
                <div className="text-white">Loading...</div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Project Distribution */}
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
                        <h2 className="text-xl font-semibold mb-6 flex items-center text-white">
                            <Calendar className="w-5 h-5 mr-2 text-blue-400" />
                            Project Distribution
                        </h2>
                        <div className="h-80">
                            {projectData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={projectData}
                                            cx="50%"
                                            cy="50%"
                                            labelLine={false}
                                            outerRadius={100}
                                            fill="#8884d8"
                                            dataKey="value"
                                            onClick={onProjectClick}
                                            cursor="pointer"
                                        >
                                            {projectData.map((entry, index) => (
                                                <Cell 
                                                    key={`cell-${index}`} 
                                                    fill={COLORS[index % COLORS.length]} 
                                                    stroke="rgba(0,0,0,0.1)"
                                                    strokeWidth={selectedProject === entry.name ? 4 : 0}
                                                />
                                            ))}
                                        </Pie>
                                        <Tooltip 
                                            contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                            formatter={(value: number) => [`\${value} mins`, 'Duration']}
                                        />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex items-center justify-center text-gray-500">
                                    No data available for this period
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Task Drill-down */}
                    <div className="bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
                        <h2 className="text-xl font-semibold mb-6 text-white">
                            {selectedProject ? `Tasks for "${selectedProject}"` : "Select a project to see tasks"}
                        </h2>
                        <div className="h-80">
                            {selectedProject && taskData.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={taskData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={100}
                                            fill="#8884d8"
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {taskData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip 
                                            contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                            formatter={(value: number) => [`\${value} mins`, 'Duration']}
                                        />
                                        <Legend />
                                    </PieChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full flex items-center justify-center text-gray-500">
                                    {selectedProject ? "No tasks recorded" : "Click on a project pie slice"}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}

            {/* Comparison Bar Chart */}
            {!loading && projectData.length > 0 && (
                <div className="mt-8 bg-gray-800 p-6 rounded-xl border border-gray-700 shadow-lg">
                    <h2 className="text-xl font-semibold mb-6 flex items-center text-white">
                        <BarChart2 className="w-5 h-5 mr-2 text-green-400" />
                        Project Comparison (Minutes)
                    </h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={projectData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                                <XAxis type="number" stroke="#9CA3AF" />
                                <YAxis dataKey="name" type="category" stroke="#9CA3AF" width={100} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                    cursor={{fill: 'rgba(255, 255, 255, 0.05)'}}
                                />
                                <Bar dataKey="value" fill="#00C49F" radius={[0, 4, 4, 0]}>
                                    {projectData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
