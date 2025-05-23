import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Navbar = () => {
    const { isAuthenticated, user, logout, loading } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/'); // Redirect to home after logout
    };

    if (loading && !isAuthenticated) { 
        return (
         <nav className="bg-gray-800 text-white p-4">
             <div className="container mx-auto flex justify-between items-center">
                 <Link to="/" className="text-xl font-bold">AI LMS</Link>
                 <div>Loading...</div>
             </div>
         </nav>
        );
    }

    return (
        <nav className="bg-gray-800 text-white p-4">
            <div className="container mx-auto flex justify-between items-center">
                <Link to="/" className="text-xl font-bold">AI LMS</Link>
                <div>
                    <Link to="/" className="px-3 hover:text-gray-300">Home</Link>
                    {isAuthenticated ? (
                        <>
                            <Link to="/dashboard" className="px-3 hover:text-gray-300">Dashboard</Link>
                            <Link to="/learning-paths" className="px-3 hover:text-gray-300">Learning Paths</Link> {/* New Link */}
                            <span className="px-3">Welcome, {user?.full_name || user?.email}</span>
                            <button onClick={handleLogout} className="px-3 hover:text-gray-300 font-semibold">Logout</button>
                        </>
                    ) : (
                        <>
                            <Link to="/login" className="px-3 hover:text-gray-300">Login</Link>
                            <Link to="/register" className="px-3 hover:text-gray-300">Register</Link>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};
export default Navbar;
