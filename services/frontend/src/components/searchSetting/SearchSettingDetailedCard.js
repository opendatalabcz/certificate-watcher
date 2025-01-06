import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../api/axios';

const SearchSettingDetailedCard = ({ setting }) => {
    const [logoUrl, setLogoUrl] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const fetchLogo = async () => {
            if (setting.logo?.local_path) {
                const imagePath = `/files/${encodeURIComponent(setting.logo.local_path)}/${encodeURIComponent(setting.logo.name)}.${encodeURIComponent(setting.logo.format.toLowerCase())}`;
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
    }, [setting.logo]); 
    
    const handleDelete = async () => {
        if (window.confirm(`Are you sure you want to delete the search setting: ${setting.domain_base}?`)) {
            try {
                await API.delete(`/search-settings/${setting.id}/`);
                alert("Search setting deleted successfully.");
                navigate("/search-settings"); // Redirect to the list of search settings
            } catch (error) {
                console.error("Failed to delete search setting:", error);
                alert("Failed to delete search setting. Please try again.");
            }
        }
    };
    
    
    return (
        <div className="card bg-dark text-white mb-3">
            <div className="card-header d-flex justify-content-between align-items-center">
                <span>{setting.owner}</span>
                <button className="btn btn-danger btn-sm" onClick={handleDelete}>
                    Delete
                </button>
            </div>
            <div className="card-body d-flex justify-content-between align-items-start">
                {/* Text Section */}
                <div className="text-section">
                    <h5 className="card-title">{setting.domain_base}</h5>
                    <p className="card-text">Algorithm: {setting.algorithm}</p>
                    <p className="card-text">TLD: {setting.tld}</p>
                    <p className="card-text">Additional Settings: {JSON.stringify(setting.additional_settings)}</p>
                </div>

                {/* Image Section */}
                <div className="image-section">
                {logoUrl ? (
                        <img
                            src={logoUrl}
                            alt={`${setting.domain_base} Logo`}
                            className="img-fluid"
                            style={{ maxHeight: "100px", maxWidth: "150px", objectFit: "contain" }}
                        />
                    ) : (
                        <div className="placeholder" style={{ height: "100px", width: "150px", background: "#ccc" }}>
                            No Logo
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SearchSettingDetailedCard;