import React, { useState } from 'react';
import { resetDatabase } from '../services/api';
import { Trash2, AlertTriangle } from 'lucide-react';

const Settings: React.FC = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const handleReset = async () => {
        if (!confirm("DANGER: This will delete ALL screenshots and captured data. This action cannot be undone. \n\nProjects and Tasks will NOT be deleted.")) {
            return;
        }

        setIsLoading(true);
        setMessage(null);

        try {
            await resetDatabase();
            setMessage({ type: 'success', text: 'Database has been successfully cleared.' });
        } catch (error) {
            console.error(error);
            setMessage({ type: 'error', text: 'Failed to reset database.' });
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="p-8 text-white">
            <h1 className="text-3xl font-bold mb-8">Settings</h1>
            
            <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 max-w-2xl">
                <h2 className="text-xl font-semibold mb-4 text-red-500 flex items-center">
                    <AlertTriangle className="w-5 h-5 mr-2" />
                    Danger Zone
                </h2>
                
                <p className="text-gray-300 mb-6">
                    Resetting the database will permanently delete all captured screenshots, OCR text, and AI analysis data. 
                    Your configured Projects, Tasks, and Rules will remain intact.
                </p>

                <button 
                    onClick={handleReset} 
                    disabled={isLoading}
                    className="flex items-center px-4 py-3 bg-red-900/50 hover:bg-red-900 border border-red-700 text-red-200 rounded-lg transition-colors"
                >
                    <Trash2 className="w-5 h-5 mr-3" />
                    {isLoading ? 'Clearing Data...' : 'Reset Database (Keep Projects/Tasks)'}
                </button>

                {message && (
                    <div className={`mt-4 p-3 rounded ${message.type === 'success' ? 'bg-green-900/50 text-green-200' : 'bg-red-900/50 text-red-200'}`}>
                        {message.text}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Settings;
