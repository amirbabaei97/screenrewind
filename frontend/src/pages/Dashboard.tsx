import React, { useEffect, useState } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { getProjectAnalytics, getTaskAnalytics } from '../services/api';
import type { ChartData } from '../services/api';
import { Calendar, BarChart2 } from 'lucide-react';
import clsx from 'clsx';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D', '#FF6B6B', '#6B5B95'];

const Dashboard: React.FC = () => {
    // Helper to get today's range
    const getTodayRange = () => {
        const start = new Date();
        const end = new Date();
        start.setHours(0, 0, 0, 0);
        end.setHours(23, 59, 59, 999);
        return { start, end };
    };

    // Dates are stored as Date objects (local time)
    // Initialize with today's full range immediately
    const [startDate, setStartDate] = useState<Date>(() => getTodayRange().start);
    const [endDate, setEndDate] = useState<Date>(() => getTodayRange().end);
    const [dateRangeLabel, setDateRangeLabel] = useState<'today' | 'yesterday' | 'week' | 'custom'>('today');

    const [projectData, setProjectData] = useState<ChartData[]>([]);
    const [selectedProject, setSelectedProject] = useState<string | null>(null);
    const [taskData, setTaskData] = useState<ChartData[]>([]);
    const [loading, setLoading] = useState(false);

    const handleDatePreset = (preset: 'today' | 'yesterday' | 'week') => {
        const start = new Date();
        const end = new Date();
        start.setHours(0, 0, 0, 0);

        if (preset === 'today') {
            const range = getTodayRange();
            setStartDate(range.start);
            setEndDate(range.end);
            setDateRangeLabel(preset);
            return;
        } else if (preset === 'yesterday') {
            start.setDate(start.getDate() - 1);
            end.setDate(end.getDate() - 1);
            end.setHours(23, 59, 59, 999);
        } else if (preset === 'week') {
            start.setDate(start.getDate() - 7);
            end.setHours(23, 59, 59, 999);
        }

        setStartDate(start);
        setEndDate(end);
        setDateRangeLabel(preset);
    };


    const handleCustomDateChange = (type: 'start' | 'end', value: string) => {
        // const date = new Date(value);
        // Correct for timezone offset if dealing with simple date inputs,
        // but typically input="date" returns YYYY-MM-DD. 
        // new Date("YYYY-MM-DD") is UTC, new Date(y,m,d) is local.
        // Let's rely on standard parsing but set time to boundary.

        const parts = value.split('-');
        if (parts.length === 3) {
            const d = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
            if (type === 'start') {
                d.setHours(0, 0, 0, 0);
                setStartDate(d);
            } else {
                d.setHours(23, 59, 59, 999);
                setEndDate(d);
            }
            setDateRangeLabel('custom');
        }
    };

    const formatDateForInput = (date: Date) => {
        const offset = date.getTimezoneOffset();
        const d = new Date(date.getTime() - (offset * 60 * 1000));
        return d.toISOString().split('T')[0];
    };

    useEffect(() => {
        fetchProjects();
    }, [startDate, endDate]);

    useEffect(() => {
        if (selectedProject) {
            fetchTasks(selectedProject);
        } else {
            setTaskData([]);
        }
    }, [selectedProject, startDate, endDate]);

    const fetchProjects = async () => {
        setLoading(true);
        try {
            const data = await getProjectAnalytics(startDate, endDate);
            setProjectData(data);
        } catch (error) {
            console.error("Failed to fetch project data", error);
        } finally {
            setLoading(false);
        }
    };

    const fetchTasks = async (projectName: string) => {
        try {
            const data = await getTaskAnalytics(projectName, startDate, endDate);
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
            <header className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-8 gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-white">Dashboard</h1>
                    <p className="text-gray-400 mt-1">
                        Activity from <span className="text-blue-400 font-medium">{startDate.toLocaleDateString()}</span> to <span className="text-blue-400 font-medium">{endDate.toLocaleDateString()}</span>
                    </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-2 bg-gray-800 rounded-lg p-2 border border-gray-700">
                    <div className="flex space-x-1">
                        <button
                            onClick={() => handleDatePreset('today')}
                            className={clsx("px-3 py-1.5 rounded text-xs font-medium transition-colors", dateRangeLabel === 'today' ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white")}
                        >
                            Today
                        </button>
                        <button
                            onClick={() => handleDatePreset('yesterday')}
                            className={clsx("px-3 py-1.5 rounded text-xs font-medium transition-colors", dateRangeLabel === 'yesterday' ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white")}
                        >
                            Yesterday
                        </button>
                        <button
                            onClick={() => handleDatePreset('week')}
                            className={clsx("px-3 py-1.5 rounded text-xs font-medium transition-colors", dateRangeLabel === 'week' ? "bg-blue-600 text-white" : "text-gray-400 hover:text-white")}
                        >
                            Last 7 Days
                        </button>
                    </div>
                    <div className="flex items-center space-x-2 border-t sm:border-t-0 sm:border-l border-gray-600 pt-2 sm:pt-0 sm:pl-2">
                        <input
                            type="date"
                            className="bg-gray-900 text-white border border-gray-700 rounded text-xs px-2 py-1"
                            value={formatDateForInput(startDate)}
                            onChange={(e) => handleCustomDateChange('start', e.target.value)}
                        />
                        <span className="text-gray-500">-</span>
                        <input
                            type="date"
                            className="bg-gray-900 text-white border border-gray-700 rounded text-xs px-2 py-1"
                            value={formatDateForInput(endDate)}
                            onChange={(e) => handleCustomDateChange('end', e.target.value)}
                        />
                    </div>
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
                                            data={projectData as any}
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
                                            itemStyle={{ color: '#fff' }}
                                            formatter={(value: any) => [`${value} mins`, 'Duration']}
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
                                            data={taskData as any}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={100}
                                            fill="#8884d8"
                                            paddingAngle={5}
                                            dataKey="value"
                                        >
                                            {taskData.map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                            itemStyle={{ color: '#fff' }}
                                            formatter={(value: any) => [`${value} mins`, 'Duration']}
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
                                    itemStyle={{ color: '#fff' }}
                                    cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                                />
                                <Bar dataKey="value" fill="#00C49F" radius={[0, 4, 4, 0]}>
                                    {projectData.map((_, index) => (
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
