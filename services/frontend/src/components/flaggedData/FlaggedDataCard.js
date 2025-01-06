import React, { useEffect, useState } from 'react';
import API from '../api/axios';

const FlaggedDataCard = ({ data }) => {
    const [logoUrl, setLogoUrl] = useState(""); // State to store the fetched logo URL

    useEffect(() => {
        const fetchLogo = async () => {
            if (data.searched_logo?.local_path) {
                const imagePath = `/files/${encodeURIComponent(data.searched_logo.local_path)}/${encodeURIComponent(data.searched_logo.name)}.${encodeURIComponent(data.searched_logo.format.toLowerCase())}`;
                try {
                    const response = await API.get(imagePath, { responseType: "blob" });
                    const blobUrl = URL.createObjectURL(response.data);
                    setLogoUrl(blobUrl);
                } catch (error) {
                    console.error("Failed to fetch image:", imagePath, error);
                    setLogoUrl(""); // Set to empty or a default placeholder
                }
            }
        };

        fetchLogo();
    }, [data.searched_logo]);

    return (
        <div className="card bg-dark text-white mb-3">
            <div className="card-header">
                Domain: {data.domain}
            </div>
            <div className="card-body">
                <h5 className="card-title">Algorithm: {data.algorithm}</h5>
                <p className="card-text">Flagged On: {new Date(data.flagged_time).toLocaleString()}</p>
                {data.searched_logo && (
                    <div>
                        <h5>Searched Logo:</h5>
                        <img src={logoUrl} alt="Searched Logo" style={{ maxHeight: "100px", maxWidth: "150px", objectFit: "contain" }}/>
                        <p>Logo Name: {data.searched_logo.name}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FlaggedDataCard;