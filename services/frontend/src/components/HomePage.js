import React, { useEffect, useState } from 'react';
import API from './api/axios';
import SearchSettingCard from './searchSetting/SearchSettingCard';
import { useAuth } from './authentication/AuthContext';
import { Link } from "react-router-dom";

const Homepage = () => {
    const [searchSettings, setSearchSettings] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { authState } = useAuth();

    useEffect(() => {
        const fetchData = async () => {
            if (!authState.isAuthenticated) {
                return;  // Early return if not authenticated
            }
            setLoading(true);
            try {
                const result = await API.get('/search-settings/');
                setSearchSettings(result.data);
                setError('');  // Clear previous errors
            } catch (error) {
                console.error('Error fetching search settings:', error);
                setError('Failed to fetch data');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [authState.isAuthenticated]);

    if (!authState.isAuthenticated) {
        return <div className="alert alert-danger" role="alert">Please log in to view this page.</div>;
    }

    return (
        <div className="container mt-4">
            <div className="d-flex justify-content-between align-items-center">
                <h2>Your Search Settings</h2>
                <Link to="/search-settings/create" className="btn btn-primary">
                    <i className="fas fa-plus"></i> Create
                </Link>
            </div>
            {loading ? <p>Loading...</p> : error ? <p>{error}</p> : searchSettings.length > 0 ? (
                searchSettings.map(setting => (
                    <SearchSettingCard key={setting.id} setting={setting}/>
                ))
            ) : (
                <p>No search settings available. Start by creating one.</p>
            )}
        </div>
    );
};

export default Homepage;