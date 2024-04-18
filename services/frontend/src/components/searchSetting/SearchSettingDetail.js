import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const SearchSettingDetail = () => {
    const { id } = useParams();  // Extract the ID from the URL
    const [setting, setSetting] = useState(null);

    useEffect(() => {
        const fetchSetting = async () => {
            try {
                const response = await axios.get(`/api/settings/${id}`);
                setSetting(response.data);
            } catch (error) {
                console.error('Failed to fetch setting details:', error);
            }
        };

        fetchSetting();
    }, [id]);

    if (!setting) return <div>Loading...</div>;

    return (
        <div className="container">
            <h1>Search Setting Detail - {setting.domain_base}</h1>
            <p>Owner: {setting.owner}</p>
            <p>Top Level Domain: {setting.tld}</p>
            <p>Flagged Data Count: {setting.flagged_data_count}</p>
            {/* Additional details and actions can be added here */}
        </div>
    );
};

export default SearchSettingDetail;