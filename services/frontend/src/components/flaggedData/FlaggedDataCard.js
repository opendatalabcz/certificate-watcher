import React from 'react';
import useImageUrls from '../images/useImageUrls';

const FlaggedDataCard = ({ data }) => {
    // Prepare the logo for use in the useImageUrls hook
    const logos = data.searched_logo ? [data.searched_logo] : [];

    // Get URLs for the logos
    const logoUrls = useImageUrls(logos);
    const logoUrl = logos.length > 0 ? logoUrls[logos[0].id] : '/path_to_default_logo.jpg';

    return (
        <div className="card bg-dark text-white mb-3">
            <div className="card-header">
                Domain: {data.domain}
            </div>
            <div className="card-body">
                <h5 className="card-title">Algorithm: {data.algorithm}</h5>
                <p className="card-text">Flagged On: {new Date(data.flagged_time).toLocaleString()}</p>
                <p className="card-text">Successfully Scraped: {data.successfully_scraped ? "Yes" : "No"}</p>
                <p className="card-text">Suspected Logo URL: {data.suspected_logo || "None"}</p>
                <p className="card-text">Searched Domain: {data.searched_domain || "Not specified"}</p>
                {data.searched_logo && (
                    <div>
                        <h5>Searched Logo:</h5>
                        <img src={logoUrl} alt="Searched Logo" style={{ width: "100px", height: "100px" }}/>
                        <p>Logo Name: {data.searched_logo.name}</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FlaggedDataCard;