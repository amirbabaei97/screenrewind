import React from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { LayoutDashboard, ListTodo, Settings, Workflow, History } from 'lucide-react';
import clsx from 'clsx';

const MainLayout: React.FC = () => {
    const location = useLocation();

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/projects', label: 'Projects', icon: ListTodo },
        { path: '/rules', label: 'Rules', icon: Workflow },
        { path: '/rewind', label: 'Time Machine', icon: History },
        { path: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <div className="flex h-screen bg-gray-900 text-white">
            {/* Sidebar */}
            <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
                <div className="p-6 border-b border-gray-700">
                    <h1 className="text-xl font-bold text-blue-400">ScreenRewind</h1>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={clsx(
                                    "flex items-center px-4 py-3 rounded-lg transition-colors",
                                    isActive 
                                        ? "bg-blue-600 text-white" 
                                        : "text-gray-300 hover:bg-gray-700 hover:text-white"
                                )}
                            >
                                <Icon className="w-5 h-5 mr-3" />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto bg-gray-900">
                <Outlet />
            </div>
        </div>
    );
};

export default MainLayout;
