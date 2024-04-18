import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from './authentication/AuthContext';

const Header = () => {
    const { authState, logout } = useAuth();
    const navigate = useNavigate();
    console.log("Authenticated:", authState.isAuthenticated);
    console.log("Admin:", authState.isAdmin);
    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-primary">
            <div className="container-fluid">
                <Link className="navbar-brand" to="/">Certwatcher</Link>
                <div className="collapse navbar-collapse" id="navbarNavAltMarkup">
                    <div className="navbar-nav">
                        <Link className="nav-link active" aria-current="page" to="/">Home</Link>
                    </div>
                    <div className="navbar-nav ms-auto">
                        {/* <Link className="nav-link active" aria-current="page" to="/">Home</Link> */}
                        {authState.isAuthenticated ? (
                            <>
                                { authState.isAdmin ? (
                                    <Link className="nav-link" to="/">Admin</Link>
                                ) : null }
                                <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
                            </>
                        ) : (
                            <>
                                <Link className="nav-link" to="/login">Login</Link>
                                <Link className="nav-link" to="/signup">Signup</Link>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Header;